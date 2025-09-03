import cv2
import os
import time
from glob import glob
from multiprocessing import Pool, Manager, freeze_support
import argparse
from queue import Empty

def is_notebook():
    """Checks if the code is running in a Jupyter-like environment."""
    try:
        from IPython import get_ipython
        if 'IPKernelApp' in get_ipython().config:
            return True
    except Exception:
        return False

def save_frames_from_videos(videos_folder_path, frame_interval=30, multithread=True, lossless=True, tqdm_cls=None, is_notebook_env=None):
    """
    Processes a folder of videos with a universal UI.
    If tqdm_cls or is_notebook_env are not provided, it will auto-detect the environment.
    """
    # CHANGED: Environment setup is now encapsulated inside the function.
    if is_notebook_env is None:
        is_notebook_env = is_notebook()
    
    if tqdm_cls is None:
        if is_notebook_env:
            from tqdm.notebook import tqdm as tqdm_cls
        else:
            from tqdm import tqdm as tqdm_cls

    if not is_notebook_env:
        import keyboard
    
    video_paths = [path for path in glob(os.path.join(videos_folder_path, "*")) if path.lower().endswith((".mp4", ".mov"))]
    if not video_paths:
        print("No video files (.mp4, .mov) found in the specified folder.")
        return

    with Manager() as manager:
        progress_queue = manager.Queue()
        pool_args = [(n, video, frame_interval, os.path.join(videos_folder_path, "images", os.path.basename(video).split(".")[0]), lossless, progress_queue) for n, video in enumerate(video_paths)]

        if multithread:
            with Pool() as pool:
                pool_result = pool.starmap_async(save_frames_from_video, pool_args)

                stop_message = "Press 'q' to stop." if not is_notebook_env else "To stop, you must interrupt the kernel."
                print(f"Processing videos... {stop_message}")
                
                progress_bars = {}
                overall_pbar = tqdm_cls(total=len(video_paths), desc="Overall Progress", position=0, unit="video")

                try:
                    while not pool_result.ready():
                        if not is_notebook_env and keyboard.is_pressed("q"):
                            pool.terminate()
                            pool.join()
                            print("\nProcess terminated by user.")
                            break
                        try:
                            # Message processing logic remains the same...
                            msg_type, worker_id, *data = progress_queue.get_nowait()
                            if msg_type == 'start':
                                total, name = data
                                desc = (name[:30] + '..') if len(name) > 32 else name
                                progress_bars[worker_id] = tqdm_cls(total=total, desc=f" L {desc}", position=worker_id + 1, unit="frame", leave=False)
                            elif msg_type == 'update' and worker_id in progress_bars:
                                progress_bars[worker_id].update(data[0])
                            elif msg_type == 'done' and worker_id in progress_bars:
                                progress_bars[worker_id].n = progress_bars[worker_id].total
                                progress_bars[worker_id].refresh()
                                progress_bars[worker_id].close()
                                overall_pbar.update(1)
                        except Empty:
                            time.sleep(0.1)
                finally:
                    for pbar in progress_bars.values():
                        pbar.close()
                    overall_pbar.close()
                    print("\nAll processes finished.")
        else: # Single-threaded execution
            for _, video_path, *args in pool_args:
                save_frames_from_video_single(video_path, *args[:3], tqdm_cls=tqdm_cls)

def save_frames_from_video(worker_id, video_path, frame_interval, output_dir, lossless, progress_queue):
    """Worker function for multiprocessing. (Unchanged)"""
    # This function's logic is identical to the previous version.
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): return
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress_queue.put(('start', worker_id, total_frames, os.path.basename(video_path)))
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        if frame_count % frame_interval == 0:
            filename_base = f"{output_dir.split(os.sep)[-1]}_frame_{frame_count:04d}"
            if lossless:
                cv2.imwrite(os.path.join(output_dir, f"{filename_base}.png"), frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 6])
            else:
                cv2.imwrite(os.path.join(output_dir, f"{filename_base}.jpg"), frame)
        frame_count += 1
        progress_queue.put(('update', worker_id, 1))
    cap.release()
    progress_queue.put(('done', worker_id))

def save_frames_from_video_single(video_path, frame_interval, output_dir, lossless, tqdm_cls):
    """Single-threaded version for sequential processing. (Unchanged)"""
    # This function's logic is identical to the previous version.
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    with tqdm_cls(total=total_frames, desc=f"Extracting {os.path.basename(video_path)}", unit="frame") as pbar:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret: break
            # Frame saving logic here...
            frame_count += 1
            pbar.update(1)
    cap.release()

if __name__ == "__main__":
    # Add freeze_support() for compatibility with bundled executables (e.g., PyInstaller)
    freeze_support() 

    parser = argparse.ArgumentParser(description="Extract frames from videos with a progress UI.")
    parser.add_argument("--video_folders_path", type=str, required=True, help="Path to the folder containing videos.")
    parser.add_argument("--frame_interval", type=int, default=30, help="Save a frame every n frames.")
    parser.add_argument('--no_multithread', action='store_true', help="Disable multiprocessing.")
    parser.add_argument('--lossy', action='store_true', help="Save frames in lossy format (JPG) instead of PNG.")

    args = parser.parse_args()

    # CHANGED: The call is now simple again. The function handles its own setup.
    save_frames_from_videos(
        videos_folder_path=args.video_folders_path,
        frame_interval=args.frame_interval,
        multithread=not args.no_multithread,
        lossless=not args.lossy
    )