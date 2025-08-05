import cv2
import os
from tqdm import tqdm
from glob import glob
from multiprocessing import Pool
import argparse
import keyboard

def save_frames_from_videos(videos_folder_path, frame_interval, multithread=True, lossless=True):
    video_paths = list(glob(os.path.join(videos_folder_path, "*")))
    video_paths = [path for path in video_paths if path.lower().endswith((".mp4", ".mov"))]

    pool_args = [
        (
            video,
            frame_interval,
            os.path.join(
                videos_folder_path,
                "images",
                os.path.basename(video).split(".")[0]
            ),
            lossless
        ) for video in video_paths
    ]

    if multithread:
        with Pool() as pool:
            pool_result = pool.starmap_async(save_frames_from_video, pool_args)

            print("Press 'q' to stop the process.")
            while not pool_result.ready():
                if keyboard.is_pressed("q"):
                    pool.terminate()
                    print("Process terminated by user.")
                    break

            pool.close()
            pool.join()
    else:
        for n, (video_path, frame_interval, output_dir, lossless) in enumerate(pool_args):
            print(f"Processing video[{n+1}/{len(video_paths)}]: {video_path}")
            save_frames_from_video(video_path, frame_interval, output_dir, lossless)

def save_frames_from_video(video_path, frame_interval, output_dir=None, lossless=True):
    """
    Extract frames from an MP4 video and save them as JPG images.

    :param video_path: Path to the input video file.
    :param output_dir: Directory where the frames will be saved.
    :param frame_interval: Save a frame every "frame_interval" frames.
    """
    # Create the output directory if it doesn"t exist

    if output_dir is None:
        output_dir = ".".join(video_path.split(".")[:-1])

    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    # Get total number of frames for progress tracking
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    saved_frame_count = 0

    # Progress bar using tqdm
    with tqdm(total=total_frames, desc="Extracting frames", unit="frame") as pbar:
        while True:
            ret, frame = cap.read()

            # If no frame is read, we reached the end of the video
            if not ret:
                break

            # Save the frame at the specified interval
            if frame_count % frame_interval == 0:
                if lossless:
                    cv2.imwrite(
                        os.path.join(output_dir, f"{output_dir.split(os.sep)[-1]}_frame_{frame_count:04d}.png"),
                        frame,
                        [int(cv2.IMWRITE_PNG_COMPRESSION), 6]
                    )
                else:
                    cv2.imwrite(os.path.join(output_dir, f"{output_dir.split(os.sep)[-1]}_frame_{frame_count:04d}.jpg"), frame)
                saved_frame_count += 1
            frame_count += 1
            pbar.update(1)

    cap.release()
    print(f"Finished! Saved {saved_frame_count} frames to '{output_dir}'.")

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save every nth frame from a video.")
    parser.add_argument("--multithread", type=str, default=True)
    parser.add_argument("--video_folders_path", type=str, default=None, help="Path to the folder containing videos.")
    parser.add_argument("--video_path", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default=None, help="Directory to save the frames.")
    parser.add_argument("--frame_interval", type=int, default=30, help="Save a frame every n frames.")
    parser.add_argument("--lossless", type=bool, default=True, help="Save frames in lossless format (PNG).")

    args = parser.parse_args()

    if args.video_folders_path is None:
        save_frames_from_video(
            video_path=args.video_path,
            frame_interval=args.frame_interval,
            output_dir=args.output_dir,
            lossless=args.lossless
        )
    else:
        save_frames_from_videos(
            videos_folder_path=args.video_folders_path,
            frame_interval=args.frame_interval,
            multithread=args.multithread,
            lossless=args.lossless
        )