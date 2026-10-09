"""Bounded GET-only observation; never imports a provider or opens an exec session."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
EXECS = [
    "3cb528138771884a52fa9bd01e5d5458ca4ffbd41c949282328d08b2dc0286bf",
    "fe36c6b84e7ab5a74fbfe441848c95fa4fab65fe5db8cfba3477d0fdb0960e73",
]
DAEMON = "165fb59b3d43bd73a48072e6c283d338e9140b700f3e3f3bd0b3bc3602b06402"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def main():
    phase = sys.argv[1]
    assert phase in ("before", "before_authorized", "detail", "security", "after")
    rawdir = HERE / ("raw_live_" + phase)
    rawdir.mkdir(exist_ok=False)
    commands = json.loads((HERE / "commands_run.json").read_text())
    phase_commands = []

    def run(argv, api_path=None):
        permitted = (
            argv[:3] in (["docker", "context", "show"], ["docker", "context", "inspect"])
            or argv[:2] in (["docker", "inspect"], ["docker", "top"], ["docker", "logs"])
            or (argv[0] == "curl" and "--request" in argv and argv[argv.index("--request") + 1] == "GET"
                and "--unix-socket" in argv and argv[-1].startswith("http://localhost/"))
        )
        assert permitted, argv
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            proc = subprocess.run(argv, capture_output=True, timeout=40,
                                  env=dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1"))
            out, err, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            out, err, rc = exc.stdout or b"", exc.stderr or b"", None
        stem = f"{len(phase_commands) + 1:03d}"
        for suffix, raw in (("stdout", out), ("stderr", err)):
            (rawdir / (stem + "." + suffix)).write_bytes(raw)
        entry = {"argv": argv, "api_method": "GET" if api_path else None, "api_path": api_path,
                 "started_at": started, "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 "returncode": rc, "stdout_path": str(rawdir.relative_to(HERE) / (stem + ".stdout")),
                 "stderr_path": str(rawdir.relative_to(HERE) / (stem + ".stderr")),
                 "stdout_sha256": sha(out), "stderr_sha256": sha(err)}
        phase_commands.append(entry)
        commands.append(entry)
        write("commands_run.json", commands)
        return out, entry

    context_raw, context_cmd = run(["docker", "context", "show"])
    if context_cmd["returncode"] != 0:
        write("raw_live_" + phase + "_summary.json", {"status": "ENGINE_CONTEXT_UNAVAILABLE"})
        return
    context = context_raw.decode().strip()
    context_inspect, inspect_cmd = run(["docker", "context", "inspect", context])
    host = json.loads(context_inspect)[0]["Endpoints"]["docker"]["Host"]
    assert host.startswith("unix://"), "Only existing authorized local Unix Engine is supported"
    endpoint = host[len("unix://"):]
    write("raw_engine_endpoint_" + phase + ".json", {"context": context, "Host": host,
          "resolution_commands": [context_cmd, inspect_cmd], "no_other_daemon": True})

    def get(path):
        argv = ["curl", "--silent", "--show-error", "--max-time", "30", "--noproxy", "*",
                "--include", "--request", "GET", "--unix-socket", endpoint, "http://localhost" + path]
        raw, cmd = run(argv, path)
        status = None
        body = b""
        if b"\r\n\r\n" in raw:
            header, body = raw.split(b"\r\n\r\n", 1)
            status = int(header.splitlines()[0].split()[1])
        cmd["http_status"] = status
        cmd["response_body_sha256"] = sha(body)
        write("commands_run.json", commands)
        parsed = None
        if cmd["returncode"] == 0 and status == 200:
            try:
                parsed = json.loads(body)
            except (ValueError, UnicodeDecodeError):
                pass
        return {"command": cmd, "http_status": status, "parsed": parsed,
                "body_sha256": sha(body), "available": parsed is not None}

    inventory = {"containers_list": get("/containers/json?all=1"), "images": get("/images/json?all=1"),
                 "networks": get("/networks"), "volumes": get("/volumes")}
    inventory["containers"] = []
    for container in inventory["containers_list"]["parsed"] or []:
        inventory["containers"].append(get("/containers/" + container["Id"] + "/json"))
    inventory["network_details"] = [get("/networks/" + network["Id"])
                                    for network in inventory["networks"]["parsed"] or []]
    write("raw_docker_inventory_" + phase + ".json", inventory)
    observations = {eid: get("/exec/" + eid + "/json") for eid in EXECS}
    daemon = next((x["parsed"] for x in inventory["containers"]
                   if x["available"] and x["parsed"]["Id"] == DAEMON), None)
    if daemon:
        for eid in daemon.get("ExecIDs") or []:
            if eid not in observations:
                observations[eid] = get("/exec/" + eid + "/json")
        daemon_raw, daemon_cmd = run(["docker", "inspect", daemon["Name"].lstrip("/")])
        observations["full_daemon_cli_inspect"] = {"command": daemon_cmd, "parsed": json.loads(daemon_raw)
            if daemon_cmd["returncode"] == 0 else None}
    proxy = next((x["parsed"] for x in inventory["containers"] if x["available"]
                  and x["parsed"].get("Name") == "/errpilot-v6-egress-42393faa3385-v1-proxy"), None)
    if proxy:
        proxy_raw, proxy_cmd = run(["docker", "inspect", proxy["Name"].lstrip("/")])
        observations["full_proxy_cli_inspect"] = {"command": proxy_cmd, "parsed": json.loads(proxy_raw)
            if proxy_cmd["returncode"] == 0 else None}
    raw, top_cmd = run(["docker", "top", DAEMON, "-eo", "pid,ppid,lstart,etime,args"])
    observations["docker_top"] = {"command": top_cmd, "stdout": raw.decode(errors="replace")}
    observations["engine_top"] = get("/containers/" + DAEMON + "/top?ps_args=-eo%20pid%2Cppid%2Clstart%2Cetime%2Cargs")
    if phase.startswith("before"):
        raw, log_cmd = run(["docker", "logs", "--timestamps", DAEMON])
        observations["daemon_logs"] = {"command": log_cmd, "stdout_size": len(raw)}
    observations["current_socket_table"] = "CURRENT_SOCKET_TABLE_NOT_REOBSERVED"
    write("exec_inspect_observations_" + phase + ".json", observations)
    write("raw_live_" + phase + "_summary.json", {"inventory_available": {
        k: v["available"] for k, v in inventory.items() if isinstance(v, dict)},
        "execs": {eid: observations[eid]["parsed"] for eid in EXECS},
        "read_only": True, "phase": phase})
    print(json.dumps({"phase": phase, "commands": len(phase_commands),
          "inventory_available": inventory["containers_list"]["available"],
          "execs": {eid: observations[eid]["parsed"] for eid in EXECS}}, indent=2))


if __name__ == "__main__":
    main()
