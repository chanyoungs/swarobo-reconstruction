import skimage
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import os
from tqdm import tqdm

def match_histograms(reference_img_path, original_img_path, save_dir):
    # Read the images
    original = plt.imread(original_img_path)
    reference = plt.imread(reference_img_path)

    # Ensure images are in the same color space
    if original.ndim == 2:  # Grayscale
        original = np.stack((original,) * 3, axis=-1)
    if reference.ndim == 2:  # Grayscale
        reference = np.stack((reference,) * 3, axis=-1)

    # Match histograms
    matched = skimage.exposure.match_histograms(original, reference)

    # Save the matched image in the specified directory with the same name as the original
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.basename(original_img_path)
    save_path = os.path.join(save_dir, filename)
    plt.imsave(save_path, matched)

def match_images(images_dir, reference_img_path):
    for image_path in tqdm(glob(os.path.join(images_dir, "*", '*.png'))):
        if os.path.realpath(os.path.dirname(image_path)) != os.path.realpath(os.path.dirname(reference_img_path)):
            save_dir = os.path.realpath(os.path.join(
                images_dir + "_normalized",
                os.path.relpath(os.path.dirname(image_path), images_dir)
            ))
            match_histograms(reference_img_path, image_path, save_dir)

if __name__ == "__main__":
    reference_img = "D:/Users/chany/Downloads/pngs/siyi_a8_mini_png - Copy/images/drone_1/drone_1_frame_0000.png"
    image_dir = "D:/Users/chany/Downloads/pngs/siyi_a8_mini_png - Copy/images"
    match_images(image_dir, reference_img)