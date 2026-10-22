"""Demo diff-based risk floor. Not an enterprise semantic classifier."""
import argparse, ast, json, subprocess, sys
from pathlib import Path
CRITICAL=('finance/','auth/','migrations/','.github/workflows/','controls/','hosted/')
GOVERNING=('policy/','requirements/','.github/')
def git(*args): return subprocess.check_output(['git',*args],text=True).strip()
def show(ref,path):
    try: return subprocess.check_output(['git','show',f'{ref}:{path}'],text=True,stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError: return None
def ast_same(a,b):
    if a is None or b is None: return False
    try: return ast.dump(ast.parse(a),include_attributes=False)==ast.dump(ast.parse(b),include_attributes=False)
    except SyntaxError: return False
def classify(base,head='HEAD'):
    paths=[p for p in git('diff','--name-only',f'{base}...{head}').splitlines() if p]
    floor=1; reasons=[]
    for p in paths:
        if p=='.pilot/task.json': continue
        if p.endswith(('.md','.txt')) and not p.startswith(GOVERNING): continue
        if p.endswith('.py') and ast_same(show(base,p),show(head,p)): continue
        if p.startswith(CRITICAL) or p.startswith(GOVERNING):
            floor=3; reasons.append(f'{p}: protected')
        else:
            floor=max(floor,2); reasons.append(f'{p}: >=R2')
    return f'R{floor}',paths,reasons
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--head',default='HEAD');ap.add_argument('--output',default='pilot-risk-report.json')
    a=ap.parse_args();floor,paths,reasons=classify(a.base,a.head)
    f=Path('.pilot/task.json');claimed=json.loads(f.read_text()).get('claimed_risk','UNSET') if f.exists() else 'UNSET'
    rank={'R1':1,'R2':2,'R3':3};ok=claimed in rank and rank[claimed]>=rank[floor]
    data=dict(base=a.base,head=a.head,floor=floor,claimed=claimed,paths=paths,reasons=reasons,risk_gate_pass=ok,human_signoff_proved=False)
    Path(a.output).write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
    if not ok: print('BLOCKED: insufficient risk declaration',file=sys.stderr);return 3
    return 0
if __name__=='__main__':sys.exit(main())
