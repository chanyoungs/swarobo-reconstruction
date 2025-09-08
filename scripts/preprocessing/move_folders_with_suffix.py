import os
import re
import shutil

def move_folders_with_suffix(source_dir):
    # Regular expression to match folders with pattern (\d+)_\d+_\d+_(\d+_.+)_\d+F
    pattern = r'(\d+)_\d+_\d+_(\d+_.+)_\d+F$'
    
    for folder_name in os.listdir(source_dir):
        folder_path = os.path.join(source_dir, folder_name)

        if os.path.isdir(folder_path):
            match = re.match(pattern, folder_name)
            if match:
                first_number, base_part = match.groups()
                base_name = f"{first_number}_{base_part}"

                # Create the "images" directory for this dataset
                target_dir = os.path.join(source_dir, "dataset", base_name, "images")
                os.makedirs(target_dir, exist_ok=True)

                # Final destination for this folder
                destination = os.path.join(target_dir, folder_name)

                # If destination already exists, skip to avoid nesting
                if os.path.exists(destination):
                    print(f"Skipping {folder_name}, destination already exists: {destination}")
                    continue

                # Move the folder safely
                shutil.move(folder_path, destination)
                print(f"Moved {folder_name} → {destination}")

if __name__ == "__main__":
    source_directory = os.getcwd()
    move_folders_with_suffix(source_directory)
