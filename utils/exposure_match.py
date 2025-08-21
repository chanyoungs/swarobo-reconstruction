# exposure_match.py
# Usage: python exposure_match.py /path/in_frames /path/out_frames ref_index
import cv2, numpy as np, sys, os, glob
from tqdm import tqdm

in_dir, out_dir, ref_idx = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(out_dir, exist_ok=True)
paths = sorted(glob.glob(os.path.join(in_dir, '*.*')))
ref = cv2.imread(paths[ref_idx], cv2.IMREAD_COLOR)
ref_lab = cv2.cvtColor(ref, cv2.COLOR_BGR2LAB)
L_ref = ref_lab[...,0].astype(np.float32)

# Compute robust stats from reference lightness
mu_ref, sig_ref = np.mean(L_ref), np.std(L_ref) + 1e-6

alpha_prev, beta_prev = 1.0, 0.0  # temporal smoothing state
for i,p in enumerate(tqdm(paths)):
    img = cv2.imread(p, cv2.IMREAD_COLOR)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[...,0]
    mu, sig = np.mean(L), np.std(L) + 1e-6

    # Affine match on L channel: L' = alpha*L + beta
    alpha = sig_ref / sig
    beta  = mu_ref - alpha * mu

    # Temporal smooth the correction (reduce frame-to-frame noise)
    t = 0.8  # 0=no smoothing, 0.9=very smooth
    alpha = t*alpha_prev + (1-t)*alpha
    beta  = t*beta_prev  + (1-t)*beta
    alpha_prev, beta_prev = alpha, beta

    L_corr = np.clip(alpha*L + beta, 0, 255)
    lab[...,0] = L_corr
    out = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    # Optional gentle contrast normalization on the corrected L channel
    # to reduce dullness in cloudy segment:
    # out_yuv = cv2.cvtColor(out, cv2.COLOR_BGR2YUV)
    # out_yuv[...,0] = cv2.equalizeHist(out_yuv[...,0])
    # out = cv2.cvtColor(out_yuv, cv2.COLOR_YUV2BGR)

    gamma = 1.1  # >1.0 = brighten, <1.0 = darken
    out = np.clip(((out/255.0) ** (1.0/gamma)) * 255, 0, 255).astype(np.uint8)

    cv2.imwrite(os.path.join(out_dir, os.path.basename(p)), out)
