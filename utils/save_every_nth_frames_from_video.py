import cv2
import os
import time
from glob import glob
from multiprocessing import Pool, Manager, freeze_support
import argparse
from queue import Empty
import numpy as np
import traceback

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
    Processes a folder of videos with a universal UI, fully supporting Unicode paths.
    """
    # Environment setup is encapsulated inside the function.
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

    # Prepare arguments for each worker process
    pool_args = []
    for n, video in enumerate(video_paths):
        # Create the full output directory path
        video_name = os.path.basename(video).split(".")[0]
        output_dir = os.path.join(videos_folder_path, "images", video_name)
        pool_args.append((n, video, frame_interval, output_dir, lossless))

    if multithread:
        with Manager() as manager:
            progress_queue = manager.Queue()
            # Add the queue to the arguments for each worker
            worker_args = [args + (progress_queue,) for args in pool_args]

            with Pool() as pool:
                pool_result = pool.starmap_async(save_frames_from_video, worker_args)
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
        print("Processing videos in single-threaded mode...")
        for _, video_path, frame_interval, output_dir, lossless in tqdm_cls(pool_args, desc="Video Progress"):
            save_frames_from_video_single(video_path, frame_interval, output_dir, lossless, tqdm_cls)

def save_frames_from_video(worker_id, video_path, frame_interval, output_dir, lossless, progress_queue):
    """Worker function for multiprocessing with Unicode path fix."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"🔴 [Worker {worker_id}] Could not open video: {video_path}")
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress_queue.put(('start', worker_id, total_frames, os.path.basename(video_path)))
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret: break

            if frame_count % frame_interval == 0:
                if frame is None:
                    continue

                ext = ".png" if lossless else ".jpg"
                filename_base = f"{os.path.basename(output_dir)}_frame_{frame_count:04d}"
                full_path = os.path.join(output_dir, f"{filename_base}{ext}")

                result, buffer = cv2.imencode(ext, frame)
                if result:
                    with open(full_path, 'wb') as f:
                        f.write(buffer)
                
            frame_count += 1
            progress_queue.put(('update', worker_id, 1))

        cap.release()
        progress_queue.put(('done', worker_id))

    except Exception:
        print(f"🔴🔴🔴 [Worker {worker_id}] A critical exception occurred! 🔴🔴🔴")
        traceback.print_exc()

def save_frames_from_video_single(video_path, frame_interval, output_dir, lossless, tqdm_cls):
    """Single-threaded version with Unicode path fix."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Cannot open video file: {video_path}")
            return
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        with tqdm_cls(total=total_frames, desc=f"Extracting {os.path.basename(video_path)}", unit="frame", leave=False) as pbar:
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                if frame_count % frame_interval == 0:
                    if frame is None:
                        continue

                    # Apply the same Unicode fix here
                    ext = ".png" if lossless else ".jpg"
                    filename_base = f"{os.path.basename(output_dir)}_frame_{frame_count:04d}"
                    full_path = os.path.join(output_dir, f"{filename_base}{ext}")

                    result, buffer = cv2.imencode(ext, frame)
                    if result:
                        with open(full_path, 'wb') as f:
                            f.write(buffer)

                frame_count += 1
                pbar.update(1)
                
        cap.release()
    except Exception:
        print(f"🔴🔴🔴 An exception occurred while processing {video_path}! 🔴🔴🔴")
        traceback.print_exc()

if __name__ == "__main__":
    freeze_support() 
    parser = argparse.ArgumentParser(description="Extract frames from videos with a progress UI.")
    parser.add_argument("--video_folders_path", type=str, required=True, help="Path to the folder containing videos.")
    parser.add_argument("--frame_interval", type=int, default=30, help="Save a frame every n frames.")
    parser.add_argument('--no_multithread', action='store_true', help="Disable multiprocessing.")
    parser.add_argument('--lossy', action='store_true', help="Save frames in lossy format (JPG) instead of PNG.")

    args = parser.parse_args()

    save_frames_from_videos(
        videos_folder_path=args.video_folders_path,
        frame_interval=args.frame_interval,
        multithread=not args.no_multithread,
        lossless=not args.lossy
    )