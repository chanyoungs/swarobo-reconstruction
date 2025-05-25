import os
from PIL import Image

def remove_metadata(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                with Image.open(input_path) as img:
                    data = list(img.getdata())
                    clean_img = Image.new(img.mode, img.size)
                    clean_img.putdata(data)
                    clean_img.save(output_path)
                    print(f"Metadata removed: {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

# Example usage
input_folder = 'D:/Users/chany/Downloads/250522_현곤텐트_dji매빅2-20250522T071912Z-1-001/250522_현곤텐트_dji매빅2'
output_folder = 'D:/Users/chany/Downloads/250522_현곤텐트_dji매빅2-20250522T071912Z-1-001/250522_incheon_tent_dji_mavick2_metadata_removed'
remove_metadata(input_folder, output_folder)
