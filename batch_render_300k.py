import os
from glob import glob
import re

for path_checkpoint in sorted(list(glob(f"/home/chanyoungs/Documents/SWAROBO/swarobo/outputs/2_3_4-jpeg-colmap/splatfacto/2024-11-19_154853/nerfstudio_models/*.ckpt"))):
    steps = re.findall("step-0+(\d+).ckpt", path_checkpoint)[0]
    print(f"*****************\n\n\n\n{steps}\n\n\n\n*****************")

    # Read the original file and replace the line
    with open("/home/chanyoungs/Documents/SWAROBO/swarobo/outputs/2_3_4-jpeg-colmap/splatfacto/2024-11-19_154853/config.yml", "r") as file:
        lines = file.readlines()

    # Replace the target line
    modified_lines = [
        line.replace("load_step: null", f"load_step: {steps}") for line in lines
    ]

    # Write the modified content to a new file
    with open("/home/chanyoungs/Documents/SWAROBO/swarobo/outputs/2_3_4-jpeg-colmap/splatfacto/2024-11-19_154853/config_steps.yml", "w") as file:
        file.writelines(modified_lines)
    
    if steps == "299999":
        steps = "300000"
    os.system(f"""ns-render camera-path \
--load-config /home/chanyoungs/Documents/SWAROBO/swarobo/outputs/2_3_4-jpeg-colmap/splatfacto/2024-11-19_154853/config_steps.yml \
--camera-path-filename /media/chanyoungs/DATA/SWAROBO-Data/drone_captures_05.11.24/preprocessed/regained/2_3_4-jpeg-colmap/camera_paths/300k.json \
--output-path renders/2_3_4-jpeg-colmap/300k/{steps[:-3]}k.mp4""")