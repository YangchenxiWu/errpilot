"""Read installer source configuration inside already local network=none bases.

Only allowlist classification is returned. Credential-bearing URLs/configuration
and unrelated environment values are never emitted.
"""
from __future__ import annotations

import json
import subprocess

from . import qualify_runtime as q

CODE = r'''
import configparser,json,os
from urllib.parse import urlsplit
def classify(raw):
    try:
        u=urlsplit(raw)
        if u.scheme=='https' and u.hostname=='pypi.org' and u.port in (None,443) and u.path in ('/simple','/simple/') and not u.username and not u.password and not u.query and not u.fragment:
            return 'ACCEPTED_PYPI_SIMPLE'
    except Exception:
        pass
    return 'UNAPPROVED_SOURCE_VALUE_REDACTED'
values=[]
for name in ('PIP_INDEX_URL','PIP_EXTRA_INDEX_URL','PIP_FIND_LINKS'):
    if os.environ.get(name):
        values.append({'origin':'environment:'+name,'classification':classify(os.environ[name])})
paths=('/etc/xdg/pip/pip.conf','/etc/pip.conf','/root/.pip/pip.conf','/root/.config/pip/pip.conf',os.environ.get('PIP_CONFIG_FILE',''))
for index,path in enumerate(paths):
    if path and os.path.isfile(path):
        parser=configparser.RawConfigParser()
        try:
            parser.read(path)
            for section in parser.sections():
                for key in ('index-url','extra-index-url','find-links'):
                    if parser.has_option(section,key):
                        values.append({'origin':'config-slot-'+str(index)+':'+section+':'+key,'classification':classify(parser.get(section,key))})
        except Exception:
            values.append({'origin':'config-slot-'+str(index),'classification':'UNREADABLE_CONFIG'})
try:
    from pip._internal.models.index import PyPI
    default_classification=classify(PyPI.simple_url)
except Exception:
    default_classification='UNVERIFIED_INSTALLED_PIP_DEFAULT'
print(json.dumps({'namespace':'SYNTHETIC_QUALIFICATION_ONLY','declared_source_values':values,'installed_pip_default_classification':default_classification,'source_scope_matches':default_classification=='ACCEPTED_PYPI_SIMPLE' and all(v['classification']=='ACCEPTED_PYPI_SIMPLE' for v in values)},sort_keys=True))
'''


def main():
    bases = json.loads((q.E / "base_runtime_local_status.json").read_bytes())["bases"]
    observations = []
    for base in bases:
        if base["local_status"] != "LOCAL_PRESENT":
            continue
        argv = ["docker", "run", "--rm", "--pull=never", "--platform=linux/amd64",
                "--network=none", "--read-only", "--entrypoint=python", base["reference"], "-c", CODE]
        result = subprocess.run(argv, capture_output=True, check=False, timeout=60)
        observations.append({"reference": base["reference"], "exit_code": result.returncode,
            "probe": json.loads(result.stdout) if result.returncode == 0 else "PROBE_FAILED",
            "stdout_sha256": q.a.sha(result.stdout), "stderr_sha256": q.a.sha(result.stderr),
            "argv": argv, "live_network": False})
    q.save("base_installer_source_status.json", {"namespace": q.l.SYNTHETIC,
        "observations": observations, "network_installations": 0,
        "limitations": "Read-only configured-source/default observation; package-level provenance "
                        "and actual egress confinement remain unqualified."})
    print(json.dumps({"bases_probed": len(observations), "source_scope_matches": all(
        x["exit_code"] == 0 and x["probe"]["source_scope_matches"] for x in observations)}))


if __name__ == "__main__":
    main()
