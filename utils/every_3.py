from glob import glob
import os
import shutil
from tqdm import tqdm

for path in tqdm(glob(os.path.join("/media/chanyoungs/DATA1/SWAROBO-Data/drone_captures_05.11.24/preprocessed/regained/all-named-folder-jpeg", "*"))[::3]):
    shutil.copy(path, "/media/chanyoungs/DATA1/SWAROBO-Data/drone_captures_05.11.24/preprocessed/regained/all-named-folder-every-3-jpeg")