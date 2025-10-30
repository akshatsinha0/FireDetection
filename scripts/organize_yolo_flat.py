import argparse, random, shutil
from pathlib import Path
import yaml

# Organize a flat YOLO directory (images/, labels/) into train/val/test splits

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default='data/fire_yolo')
    ap.add_argument('--train', type=float, default=0.8)
    ap.add_argument('--val', type=float, default=0.1)
    ap.add_argument('--test', type=float, default=0.1)
    ap.add_argument('--seed', type=int, default=42)
    args=ap.parse_args()

    root=Path(args.root)
    img_dir=root/'images'
    lbl_dir=root/'labels'
    assert img_dir.exists() and lbl_dir.exists(), 'images/ and labels/ not found'

    exts={'.jpg','.jpeg','.png','.bmp','.tif','.tiff'}
    imgs=[p for p in img_dir.glob('*') if p.suffix.lower() in exts]
    # keep only items that have labels
    items=[(p, lbl_dir/(p.stem+'.txt')) for p in imgs]
    items=[(p,l) for (p,l) in items if l.exists()]
    if not items:
        raise SystemExit('no labeled images found')

    random.seed(args.seed)
    random.shuffle(items)
    n=len(items)
    n_train=int(n*args.train)
    n_val=int(n*args.val)
    n_test=n-n_train-n_val
    splits=(('train',items[:n_train]),('val',items[n_train:n_train+n_val]),('test',items[n_train+n_val:]))

    for split, pairs in splits:
        (img_dir/split).mkdir(parents=True, exist_ok=True)
        (lbl_dir/split).mkdir(parents=True, exist_ok=True)
        for img,lbl in pairs:
            shutil.move(str(img), str(img_dir/split/img.name))
            shutil.move(str(lbl), str(lbl_dir/split/lbl.name))

    # write/overwrite data.yaml to use new structure
    data_yaml=root/'data.yaml'
    y={
        'train': (img_dir/'train').as_posix(),
        'val': (img_dir/'val').as_posix(),
        'test': (img_dir/'test').as_posix(),
        'nc': 1,
        'names': ['fire']
    }
    with open(data_yaml,'w',encoding='utf-8') as f:
        yaml.safe_dump(y,f,sort_keys=False)

    print('organized_images', n)
    for split,_ in splits:
        print(split+'_count', len(list((img_dir/split).glob('*'))))
    print('data_yaml', str(data_yaml))

if __name__=='__main__':
    main()
