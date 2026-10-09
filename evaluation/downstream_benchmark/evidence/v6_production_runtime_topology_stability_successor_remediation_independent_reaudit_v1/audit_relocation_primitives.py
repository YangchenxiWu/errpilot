"""Darwin syscall model, entirely inside the new audit namespace.

This does NOT invoke a candidate constructor or candidate protected write.
It establishes the behavior of held dirfds across a same-owner rename, without
redirecting any candidate/real path or writing outside the authorized audit root.
"""
import fcntl
import os
from pathlib import Path
from .audit_inventory import HERE,QUAL,write,tree

root=HERE/'owned_syscall_sandbox'
root.mkdir(mode=0o700)
def fdpath(fd):return fcntl.fcntl(fd,fcntl.F_GETPATH,bytes(1024)).split(b'\0',1)[0].decode()
records=[]
for operation in ('exclusive_creation','hardlink_publication'):
 original=root/(operation+'_original');retained=root/(operation+'_retained')
 original.mkdir(mode=0o700)
 if operation=='hardlink_publication':
  with (original/'terminal.partial').open('xb') as f:f.write(b'AUDIT_SYSCALL_MODEL_ONLY\n');f.flush();os.fsync(f.fileno())
 fd=os.open(original,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  before=fdpath(fd);assert before==str(original)
  original.rename(retained)
  after=fdpath(fd);assert after==str(retained)
  if operation=='exclusive_creation':
   leaf=os.open('empty_reserved.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
   try:
    actual=fdpath(leaf);assert actual==str(retained/'empty_reserved.json')
   finally:os.close(leaf)
  else:
   os.link('terminal.partial','terminal.json',src_dir_fd=fd,dst_dir_fd=fd,follow_symlinks=False)
   actual=str(retained/'terminal.json');assert Path(actual).read_bytes()==b'AUDIT_SYSCALL_MODEL_ONLY\n'
  os.fsync(fd)
  records.append({'operation':operation,'expected_before_rename':before,'descriptor_path_after_rename':after,'created_path':actual,'all_paths_inside_authorized_audit_root':Path(actual).is_relative_to(HERE),'current_uid':os.getuid(),'current_euid':os.geteuid(),'directory_owner_uid':retained.stat().st_uid,'result':'SYSCALL_TARGET_FOLLOWS_HELD_DIRECTORY_AFTER_NAME_CHECK'})
 finally:os.close(fd)
permissions={str(p):{'uid':p.stat().st_uid,'mode':p.stat().st_mode&0o777,'current_process_write_search_access':os.access(p,os.W_OK|os.X_OK)} for p in (QUAL.parent,QUAL,QUAL/'run_4',QUAL/'run_4/fixture_1')}
write('relocation_primitive_probe.json',{'status':'PASS_OS_MECHANISM_REPRODUCTION_ONLY','candidate_constructor_exploit_executed':False,'candidate_sources_or_globals_modified':False,'qualification_population_modified':False,'unauthorized_outside_audit_artifacts':0,'records':records,'existing_qualification_directory_permissions':permissions,'retained_sandbox_inventory':tree(root),'inference':'Candidate F_GETPATH checks are not atomic with following open/write/link syscalls. Same-owner rename requires no root privilege in this owned sandbox. No accepted threat-model exclusion for such a writer was found.'})
print({'operations':len(records),'euid':os.geteuid(),'candidate_protected_writes_executed':0,'outside_audit_writes':0})
