"""Harmless Python 3.6+ egress fixture. No install or dependency resolution."""
from __future__ import print_function

import http.client
import json
import os
import socket
import ssl
import sys
from urllib.parse import urlsplit


def connect_result(host, port):
    try:
        with socket.create_connection((host, port), timeout=3):
            return {"connected": True}
    except OSError as exc:
        return {"connected": False, "exception_type": type(exc).__name__}


def request_proxy(host, port, raw):
    with socket.create_connection((host, port), timeout=3) as stream:
        stream.sendall(raw)
        return stream.recv(1024).decode("ascii", "strict").split("\r\n", 1)[0]


def main():
    with open("/topology.json") as stream:
        topology = json.load(stream)
    proxy_ip, proxy_port = topology["proxy_internal_ip"], 3128
    if sys.argv[1] == "none":
        proxies = {k: v for k, v in os.environ.items() if k.lower().endswith("proxy") and v}
        route_lines = open("/proc/net/route").read().splitlines()[1:]
        external_routes = [line for line in route_lines if line.split()[0] != "lo"]
        connected = connect_result(proxy_ip, proxy_port)
        assert not proxies and not external_routes and not connected["connected"]
        print("NONE_OBSERVATION=" + json.dumps({"proxy_variables": proxies, "external_routes": external_routes,
            "proxy_connection": connected, "status": "PASS"}, sort_keys=True), flush=True)
        return
    expected = topology["proxy_url"]
    assert os.environ["HTTP_PROXY"] == os.environ["HTTPS_PROXY"] == expected
    assert os.environ["PIP_INDEX_URL"] == "https://pypi.org/simple"
    assert not os.environ.get("PIP_TRUSTED_HOST") and not os.environ.get("PIP_EXTRA_INDEX_URL")
    binding = {"HTTP_PROXY": expected, "HTTPS_PROXY": expected, "PIP_INDEX_URL": os.environ["PIP_INDEX_URL"],
        "PIP_TRUSTED_HOST": "ABSENT", "PIP_EXTRA_INDEX_URL": "ABSENT"}
    binding["proxy_hostname_resolves_to_internal_ip"] = socket.gethostbyname(urlsplit(expected).hostname) == proxy_ip
    assert binding["proxy_hostname_resolves_to_internal_ip"]
    print("APPLICATION_BINDING=" + json.dumps(binding, sort_keys=True), flush=True)
    direct = connect_result(topology["fixture_external_ip"], topology["fixture_port"])
    assert not direct["connected"]
    print("DIRECT_EXTERNAL_FIXTURE=" + json.dumps(direct, sort_keys=True), flush=True)
    cases = [
        ("denied.invalid:443", b"CONNECT denied.invalid:443 HTTP/1.1\r\nHost: denied.invalid:443\r\n\r\n"),
        ("pypi.org:80", b"CONNECT pypi.org:80 HTTP/1.1\r\nHost: pypi.org:80\r\n\r\n"),
        ("127.0.0.1:443", b"CONNECT 127.0.0.1:443 HTTP/1.1\r\nHost: 127.0.0.1:443\r\n\r\n"),
        ("malformed", b"CONNECT broken\r\n\r\n"),
        ("ordinary_http", b"GET http://denied.invalid/ HTTP/1.1\r\nHost: denied.invalid\r\n\r\n"),
        ("userinfo", b"CONNECT user@pypi.org:443 HTTP/1.1\r\nHost: pypi.org\r\n\r\n"),
    ]
    rejected = []
    for name, raw in cases:
        status = request_proxy(proxy_ip, proxy_port, raw)
        assert status == "HTTP/1.1 403 Forbidden"
        rejected.append({"case": name, "status": status})
    print("NEGATIVE_PROXY=" + json.dumps({"internal_proxy_reachable": True, "rejections": rejected}, sort_keys=True), flush=True)
    parsed = urlsplit(os.environ["HTTPS_PROXY"])
    assert parsed.scheme == "http" and not parsed.username and parsed.port == proxy_port
    for host, path in [("pypi.org", "/simple/"), ("files.pythonhosted.org", "/")]:
        context = ssl.create_default_context()
        assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
        connection = http.client.HTTPSConnection(parsed.hostname, parsed.port, timeout=15, context=context)
        connection.set_tunnel(host, 443)
        try:
            connection.connect()
            certificate = connection.sock.getpeercert()
            ssl.match_hostname(certificate, host)
            tls_version = connection.sock.version()
            connection.request("GET", path, headers={"Host": host, "Connection": "close", "User-Agent": "ErrPilot-V6-Connectivity-Qualification/1"})
            response = connection.getresponse()
            body = response.read(256)
            assert 100 <= response.status <= 599
            observation = {"host": host, "path": path, "status": response.status, "read_bytes": len(body),
                "maximum_bytes": 256, "TLS_verification": "PASS", "TLS_version": tls_version,
                "check_hostname": context.check_hostname, "verify_mode": int(context.verify_mode),
                "certificate_subject_alt_names": certificate.get("subjectAltName", []), "proxy": expected,
                "connectivity_only": True, "package_installation": False}
            print("POSITIVE_ORIGIN=" + json.dumps(observation, sort_keys=True), flush=True)
        finally:
            connection.close()


if __name__ == "__main__":
    main()
