import os
import json
import argparse
import shutil

parser = argparse.ArgumentParser(description="Update file paths in a JSON file.")
parser.add_argument("--data_dir", type=str, help="Directory to the data folder")
parser.add_argument("--sampling_density", type=float, help="Sampling density value between 0 and 1")
args = parser.parse_args()

TRANSFORMS_PATH_ORIGINAL = os.path.join(args.data_dir, "transforms_original.json")
TRANSFORMS_PATH_NEW = os.path.join(args.data_dir, "transforms.json")

if not os.path.exists(TRANSFORMS_PATH_ORIGINAL):
    shutil.copy(TRANSFORMS_PATH_NEW, TRANSFORMS_PATH_NEW.split(".json")[0]+"_original.json")

if args.sampling_density >= 1:
    shutil.copy(TRANSFORMS_PATH_ORIGINAL, TRANSFORMS_PATH_NEW)
else:
    # Load the JSON data from the file
    with open(TRANSFORMS_PATH_ORIGINAL, "r") as file:
        data = json.load(file)

    frames_original = len(data["frames"])
    frames = []
    # Update the file_path values
    for n, frame in enumerate(data["frames"]):
        if n % int(1 / args.sampling_density) == 0:
            frames.append(frame)

    data["frames"] = frames
    frames_new = len(data["frames"])

    # Save the modified data back to the JSON file
    with open(TRANSFORMS_PATH_NEW, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Sampling density({args.sampling_density}) updated successfully: {frames_original} -> {frames_new} frames.")