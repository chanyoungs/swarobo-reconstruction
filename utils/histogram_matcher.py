import skimage.io
import skimage.exposure
import numpy as np
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def process_image(source_path, reference_img_array, save_path):
    """
    Worker function to perform histogram matching for a single image.
    This function is designed to be run in a separate process.
    """
    try:
        # Read the source image
        original = skimage.io.imread(source_path)

        # Ensure source image is 3-channel RGB for matching
        if original.ndim == 2:
            original = np.stack((original,) * 3, axis=-1)
        # Handle images with an alpha channel (e.g., RGBA)
        elif original.shape[2] == 4:
            original = original[..., :3]

        # Match histograms - THE CORRECTED LINE IS HERE
        matched = skimage.exposure.match_histograms(original, reference_img_array, channel_axis=-1)

        # Save the result
        skimage.io.imsave(save_path, matched, check_contrast=False)
        return None
    except Exception as e:
        return f"Error processing {source_path}: {e}"


def match_images_parallel(images_dir_str, reference_img_str):
    """
    Performs histogram matching for all images in a directory in parallel.
    """
    # 1. Use pathlib for robust path handling
    images_dir = Path(images_dir_str)
    reference_path = Path(reference_img_str)
    
    # Create the output directory
    save_dir = images_dir.parent / (images_dir.name + "_normalized")
    save_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving normalized images to: {save_dir}")

    # 2. Read the reference image ONCE
    print("Loading reference image...")
    reference_img = skimage.io.imread(reference_path)
    
    # Ensure reference image is 3-channel RGB
    if reference_img.ndim == 2:
        reference_img = np.stack((reference_img,) * 3, axis=-1)
    elif reference_img.shape[2] == 4:
        reference_img = reference_img[..., :3]

    # 3. Get a list of all images to process, excluding the reference itself
    image_paths_to_process = [p for p in images_dir.glob('*.png') if p.resolve() != reference_path.resolve()]
    
    if not image_paths_to_process:
        print("No images found to process (other than the reference image).")
        return

    print(f"Found {len(image_paths_to_process)} images to process...")

    # 4. Use a process pool to execute tasks in parallel
    with ProcessPoolExecutor() as executor:
        # Create a list of tasks (futures)
        futures = [
            executor.submit(
                process_image,
                source_path,
                reference_img,
                save_dir / source_path.name
            )
            for source_path in image_paths_to_process
        ]

        # Use tqdm to show a progress bar
        for future in tqdm(futures, total=len(image_paths_to_process), desc="Processing images"):
            result = future.result()
            if result: # Print any errors that occurred in the child processes
                print(result)

    print("Done!")


if __name__ == "__main__":
    # Use raw strings (r"...") for Windows paths to avoid issues with backslashes
    reference_img = r"E:/SWAROBO/hyogwang/250909_camping_D_polygon_블랙매직_폴리곤넓게/images_4k/floor/250909-033651-848433_005_camping_D_3F_5m_pitch-30_in_101115.png"
    image_dir = r"E:/SWAROBO/hyogwang/250909_camping_D_polygon_블랙매직_폴리곤넓게/images_4k/floor"
    
    match_images_parallel(image_dir, reference_img)