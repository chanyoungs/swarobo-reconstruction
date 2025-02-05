import os
from glob import glob

for r in [5, 10, 25, 50, 100, 200, 500]:
    config = glob(f"/home/chanyoungs/Documents/SWAROBO/swarobo/outputs/van-EEVEE-{r}-colmap/splatfacto/*/config.yml")[0]
    os.system(f"""ns-render camera-path \
--load-config {config} \
--camera-path-filename /home/chanyoungs/Documents/SWAROBO/blender/data/images/van/camera_paths/2024-11-14-16-46-15.json \
--output-path renders/van-EEVEE/{r}_images.mp4""")