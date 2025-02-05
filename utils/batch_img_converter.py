#!/usr/bin/python

import argparse, glob, os
from PIL import Image
from tqdm import tqdm

formats = ["BMP", "DIB", "EPS", "GIF", "ICNS", "ICO", "IM", "JPG", "JPEG",
           "J2K", "J2P", "JPX", "MSP", "PCX", "PNG", "PPM", "SGI",
           "SPIDER", "TGA", "TIFF", "WebP", "XBM"]
parser = argparse.ArgumentParser(description="Pillow example - batch converter.")
parser.add_argument('--in-dir', type=str)
parser.add_argument('--out-dir', default='.', help='Directory to save converted image files')
parser.add_argument('--out-format', choices=formats,
                    help='Output image format required. The output file will be written with the same base-name as the input file, but with an extension reflecting the format',
                    default="JPEG")
args = parser.parse_args()

infiles = list(glob.glob(os.path.join(args.in_dir, "*")))

os.makedirs(args.out_dir, exist_ok=True)

for fname in tqdm(infiles):
    if os.path.isdir(fname): continue
    base = os.path.basename(fname)
    f, ext = os.path.splitext(base)
    if len(ext) <= 1: continue
    ext = ext[1:]
    if ext.upper() not in formats:
        print('{}: format not supported .. ignoring'.format(fname))
        continue
    image = Image.open(fname)
    image = image.convert("RGB")
    opath = os.path.join(args.out_dir, '{}.{}'.format(f, args.out_format.lower()))
    image.save(opath, args.out_format)