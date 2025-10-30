import os
from roboflow import Roboflow
rf=Roboflow(api_key=os.getenv('ROBOFLOW_API_KEY'))
proj=rf.workspace('truck-rakshak').project('fire-detection-k1ima')
print('project_id',getattr(proj,'id',None))
print('attrs', [a for a in dir(proj) if not a.startswith('_')][:40])
# attempt to call potential versions listing methods
for meth in ('versions','get_versions','list_versions'):
    if meth in dir(proj):
        try:
            r=getattr(proj,meth)()
            print(meth, type(r).__name__, r)
        except Exception as e:
            print(meth,'error', type(e).__name__, str(e)[:200])
# try multiple version numbers
for vid in range(1,21):
    try:
        v=proj.version(vid)
        # Attempt a lightweight attribute access
        name=getattr(v,'name',None)
        print('HAS_VERSION',vid,name)
    except Exception as e:
        print('NO_VERSION',vid,str(e)[:160])
