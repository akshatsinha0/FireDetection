import argparse,os,torch
from ultralytics import YOLO

def main():
    p=argparse.ArgumentParser(description='Run inference with a trained YOLO model')
    p.add_argument('--weights',default='runs/train-fire/weights/best.pt')
    p.add_argument('--source',default='data/samples')
    p.add_argument('--conf',type=float,default=0.25)
    p.add_argument('--save',action='store_true')
    p.add_argument('--show',action='store_true')
    a=p.parse_args()
    if not os.path.exists(a.weights):raise SystemExit('weights not found: '+a.weights)
    if not torch.cuda.is_available():raise SystemExit('CUDA not available. Install GPU-enabled torch.')
    model=YOLO(a.weights)
    model.predict(source=a.source,conf=a.conf,device=0,save=a.save,show=a.show)

if __name__=='__main__':
    main()
