"""Stdlib CONNECT tunnel: exact two-host allowlist, reject before DNS."""
from __future__ import print_function

import ipaddress
import json
import re
import select
import socket
import socketserver
import time
import uuid

ALLOWED = frozenset(["pypi.org", "files.pythonhosted.org"])
POLICY = {
    "schema": "V6_RESTRICTED_BUILD_EGRESS_ALLOWLIST_POLICY_V1",
    "method": "CONNECT_ONLY", "allowed_exact_case_insensitive_hostnames": sorted(ALLOWED),
    "allowed_port": 443, "default_action": "DENY_BEFORE_DNS_AND_UPSTREAM_CONNECT",
    "TLS": "END_TO_END_CLIENT_ORIGIN_NO_TERMINATION",
    "PIP_INDEX_URL": "https://pypi.org/simple", "TLS_verification": "REQUIRED",
    "PIP_TRUSTED_HOST": "ABSENT", "alternate_indexes": "ABSENT",
}


def authorize(method, authority, version):
    if method != "CONNECT":
        return None, "HTTP_FORWARDING_PROHIBITED"
    if version not in ("HTTP/1.0", "HTTP/1.1"):
        return None, "MALFORMED_CONNECT"
    match = re.fullmatch(r"([A-Za-z0-9.-]+):([0-9]+)", authority)
    if match is None:
        return None, "MALFORMED_OR_USERINFO_AUTHORITY"
    host, port = match.groups()
    try:
        ipaddress.ip_address(host)
        return None, "IP_LITERAL_PROHIBITED"
    except ValueError:
        pass
    if port != "443":
        return None, "ALTERNATE_PORT_PROHIBITED"
    if host.lower() not in ALLOWED:
        return None, "HOST_NOT_ALLOWLISTED"
    return host.lower(), "ALLOW"


def emit(event, request_id, **fields):
    record = {"event": event, "request_id": request_id, "time_unix": time.time()}
    record.update(fields)
    print(json.dumps(record, sort_keys=True), flush=True)


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        request_id = uuid.uuid4().hex
        self.request.settimeout(8)
        raw = b""
        try:
            while b"\r\n\r\n" not in raw and len(raw) <= 16384:
                chunk = self.request.recv(1024)
                if not chunk:
                    break
                raw += chunk
            if len(raw) > 16384 or b"\r\n\r\n" not in raw:
                raise ValueError("malformed header")
            line = raw.split(b"\r\n", 1)[0].decode("ascii", "strict")
            parts = line.split(" ")
            if len(parts) != 3 or not all(parts):
                raise ValueError("malformed request line")
            host, reason = authorize(*parts)
        except (ValueError, UnicodeError, OSError):
            host, reason = None, "MALFORMED_CONNECT"
        if host is None:
            emit("DENY", request_id, reason=reason, upstream_dns=False, upstream_connect=False)
            try:
                self.request.sendall(b"HTTP/1.1 403 Forbidden\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
            except OSError:
                pass
            return
        emit("ALLOW", request_id, host=host, port=443, upstream_dns=False, upstream_connect=False)
        upstream = None
        try:
            emit("UPSTREAM_DNS", request_id, host=host, upstream_dns=True, upstream_connect=False)
            addresses = socket.getaddrinfo(host, 443, socket.AF_INET, socket.SOCK_STREAM)
            for family, socktype, protocol, _, address in addresses:
                candidate = socket.socket(family, socktype, protocol)
                candidate.settimeout(12)
                try:
                    emit("UPSTREAM_CONNECT", request_id, host=host, address=address[0], port=443,
                         upstream_dns=True, upstream_connect=True)
                    candidate.connect(address)
                    upstream = candidate
                    break
                except OSError:
                    candidate.close()
            if upstream is None:
                raise OSError("approved upstream unreachable")
            self.request.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            self.request.setblocking(False)
            upstream.setblocking(False)
            deadline = time.monotonic() + 45
            relayed = 0
            while time.monotonic() < deadline and relayed < 2 * 1024 * 1024:
                readable, _, _ = select.select([self.request, upstream], [], [], 1)
                for current in readable:
                    data = current.recv(65536)
                    if not data:
                        return
                    target = upstream if current is self.request else self.request
                    target.settimeout(8)
                    target.sendall(data)
                    target.setblocking(False)
                    relayed += len(data)
        except OSError as exc:
            emit("UPSTREAM_ERROR", request_id, host=host, exception_type=type(exc).__name__)
        finally:
            if upstream is not None:
                upstream.close()
            emit("CLOSE", request_id, host=host)


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    emit("READY", "server", policy=POLICY, port=3128)
    with Server(("0.0.0.0", 3128), Handler) as server:
        server.serve_forever()
