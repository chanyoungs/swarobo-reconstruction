import os
import json
import argparse

def modify_registration(output_dir):
    # Define the path to the transforms

    TRANSFORMS_PATH_NEW = os.path.join(output_dir, "transforms.json")

    os.replace(
        os.path.join(output_dir, "images", "transforms.json"),
        TRANSFORMS_PATH_NEW
    )

    # Load the JSON data from the file
    with open(TRANSFORMS_PATH_NEW, "r") as file:
        data = json.load(file)

    # Update the file_path values
    for frame in data["frames"]:
        # Extract the numeric part of the filename and reformat the path
        filename = os.path.basename(frame["file_path"])
        number_part = filename.split(".")[0]  # Get the part before ".jpg"
        new_file_path = f"images/{number_part.zfill(5)}.jpg"  # Pad with leading zeros
        frame["file_path"] = new_file_path

    data["ply_file_path"] = "sparse_pc.ply"

    # Save the modified data back to the JSON file
    with open(TRANSFORMS_PATH_NEW, "w") as file:
        json.dump(data, file, indent=4)

    print("File paths have been updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, required=True)
    args = parser.parse_args()
    modify_registration(args.output_dir)