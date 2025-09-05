import os
import re
import shutil

def move_folders_with_suffix(source_dir):
    # Regular expression to match folders with pattern (\d+)_\d+_\d+_(\d+_.+)_\d+F
    pattern = r'(\d+)_\d+_\d+_(\d+_.+)_\d+F$'
    
    # Get list of all folders in source directory
    for folder_name in os.listdir(source_dir):
        folder_path = os.path.join(source_dir, folder_name)
        
        # Check if it's a directory and matches the pattern
        if os.path.isdir(folder_path):
            match = re.match(pattern, folder_name)
            if match:
                # Extract first number set and the part after third underscore (excluding _\d+F)
                first_number, base_part = match.groups()
                # Construct base_name by combining first number and base_part
                base_name = f"{first_number}_{base_part}"
                
                # Create target directory structure
                target_dir = os.path.join(source_dir, 'dataset', base_name, 'images', folder_name)
                os.makedirs(target_dir, exist_ok=True)
                
                # Move the folder to the target directory
                shutil.move(folder_path, target_dir)
                print(f"Moved {folder_name} to {target_dir}")

if __name__ == "__main__":
    # Specify the source directory (current directory in this case)
    source_directory = os.getcwd()
    move_folders_with_suffix(source_directory)