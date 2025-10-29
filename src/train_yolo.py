import argparse,os,sys,torch
from ultralytics import YOLO

def parse_args():
    p=argparse.ArgumentParser(description='Train YOLO on fire dataset')
    p.add_argument('--data',default='data/fire_yolo/data.yaml')
    p.add_argument('--model',default='yolov8n.pt')
    p.add_argument('--epochs',type=int,default=50)
    p.add_argument('--imgsz',type=int,default=640)
    p.add_argument('--batch',type=int,default=16)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--project',default='runs')
    p.add_argument('--name',default='train-fire')
    p.add_argument('--resume',action='store_true')
    return p.parse_args()

if __name__=='__main__':
    a=parse_args()
    if not os.path.exists(a.data):raise SystemExit('data.yaml not found: '+a.data)
    if not torch.cuda.is_available():raise SystemExit('CUDA not available. Install GPU-enabled torch.')
    print('gpu:',torch.cuda.get_device_name(0))
    model=YOLO(a.model)
    model.train(data=a.data,epochs=a.epochs,imgsz=a.imgsz,device=0,batch=a.batch,workers=a.workers,project=a.project,name=a.name,resume=a.resume,cache=True,seed=42)
