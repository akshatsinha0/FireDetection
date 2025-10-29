import argparse,os,shutil,random,yaml
from pathlib import Path

# Download Roboflow dataset and optionally create a 2000-image train subset

def pick_latest_version(project):
    # try common patterns for latest version id
    try:
        vers=project.versions()
        if isinstance(vers,list) and vers:
            # items may be dicts like {'version':1}
            ids=[]
            for v in vers:
                for k in ('version','id','number'):
                    if k in v:
                        try: ids.append(int(v[k])); break
                        except: pass
            if ids:
                return max(ids)
    except Exception:
        pass
    # fallback guesses
    for v in (1,2,3,4,5):
        try:
            project.version(v)  # will raise if not exists
            return v
        except Exception:
            continue
    raise RuntimeError('Could not determine project version')


def copy_subset(src_images,src_labels,dst_images,dst_labels,limit):
    files=[p for p in sorted(Path(src_images).glob('*.*')) if p.suffix.lower() in {'.jpg','.jpeg','.png','.bmp','.tif','.tiff'}]
    if not files: raise RuntimeError(f'no images in {src_images}')
    random.seed(42)
    files=random.sample(files,k=min(limit,len(files)))
    Path(dst_images).mkdir(parents=True,exist_ok=True)
    Path(dst_labels).mkdir(parents=True,exist_ok=True)
    for img in files:
        lbl=Path(src_labels)/ (img.stem+'.txt')
        if not lbl.exists():
            # skip images without labels
            continue
        shutil.copy2(img, Path(dst_images)/img.name)
        shutil.copy2(lbl, Path(dst_labels)/lbl.name)
    return len(list(Path(dst_images).glob('*.*')))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--api_key',default=os.getenv('ROBOFLOW_API_KEY'))
    ap.add_argument('--workspace',required=True)
    ap.add_argument('--project',required=True)
    ap.add_argument('--outdir',default='data/fire_yolo_full')
    ap.add_argument('--subset_out',default='data/fire_yolo_2000')
    ap.add_argument('--limit',type=int,default=2000)
    ap.add_argument('--format',default='yolov8')
    ap.add_argument('--version',type=int,default=None)
    args=ap.parse_args()
    if not args.api_key:
        raise SystemExit('Set ROBOFLOW_API_KEY env var or pass --api_key')

    from roboflow import Roboflow
    rf=Roboflow(api_key=args.api_key)
    proj=rf.workspace(args.workspace).project(args.project)
    ver_id=args.version or pick_latest_version(proj)
    ds=proj.version(ver_id).download(args.format, location=args.outdir)
    # roboflow returns a path; detect yaml
    base=Path(ds.location if hasattr(ds,'location') else ds)
    yaml_path=None
    for c in ('data.yaml','dataset.yaml'):
        p=base/c
        if p.exists(): yaml_path=p; break
    if not yaml_path: raise RuntimeError('data.yaml not found in download')
    meta=yaml.safe_load(open(yaml_path,'r',encoding='utf-8'))

    # Build subset with up to N train images; keep val/test as-is
    src_train_images=base/'train/images'
    src_train_labels=base/'train/labels'
    if not src_train_images.exists():
        # alternate layout
        src_train_images=base/'images'/'train'
        src_train_labels=base/'labels'/'train'
    dst=Path(args.subset_out)
    (dst/'images'/'train').mkdir(parents=True,exist_ok=True)
    (dst/'labels'/'train').mkdir(parents=True,exist_ok=True)

    copied=copy_subset(src_train_images,src_train_labels,dst/'images/train',dst/'labels/train',args.limit)

    # copy val/test entirely if present
    for split in ('val','valid','validation'):
        simg=base/f'images/{split}'
        slbl=base/f'labels/{split}'
        if simg.exists() and slbl.exists():
            tgt_img=dst/f'images/val'
            tgt_lbl=dst/f'labels/val'
            shutil.copytree(simg,tgt_img,dirs_exist_ok=True)
            shutil.copytree(slbl,tgt_lbl,dirs_exist_ok=True)
            break
    stimg=base/'images/test'
    stlbl=base/'labels/test'
    if stimg.exists() and stlbl.exists():
        shutil.copytree(stimg,dst/'images/test',dirs_exist_ok=True)
        shutil.copytree(stlbl,dst/'labels/test',dirs_exist_ok=True)

    # write new data.yaml
    out_yaml=dst/'data.yaml'
    nc=meta.get('nc',1)
    names=meta.get('names',['fire'])
    y={
        'train': str((dst/'images/train').as_posix()),
        'val': str((dst/'images/val').as_posix()) if (dst/'images/val').exists() else str((dst/'images/train').as_posix()),
        'test': str((dst/'images/test').as_posix()) if (dst/'images/test').exists() else str((dst/'images/train').as_posix()),
        'nc': int(nc),
        'names': names,
    }
    with open(out_yaml,'w',encoding='utf-8') as f:
        yaml.safe_dump(y,f,sort_keys=False)
    print('downloaded_version',ver_id)
    print('subset_train_images',copied)
    print('subset_dir',str(dst))

if __name__=='__main__':
    main()
