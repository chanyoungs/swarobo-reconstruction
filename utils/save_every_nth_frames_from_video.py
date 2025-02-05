import cv2
import os
from tqdm import tqdm

def save_frames_from_video(video_path, output_dir, frame_interval):
    """
    Extract frames from an MP4 video and save them as JPG images.

    :param video_path: Path to the input video file.
    :param output_dir: Directory where the frames will be saved.
    :param frame_interval: Save a frame every 'frame_interval' frames.
    """
    # Create the output directory if it doesn't exist
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
                filename = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
                cv2.imwrite(filename, frame)
                saved_frame_count += 1

            frame_count += 1
            pbar.update(1)

    cap.release()
    print(f"Finished! Saved {saved_frame_count} frames to '{output_dir}'.")

# Example usage
if __name__ == "__main__":
    video_path = "/media/chanyoungs/DATA1/SWAROBO-Data/241220-인천드론시험비행장-수동촬영테스트/REC_0002.mp4"  # Path to your MP4 video file
    output_dir = "/media/chanyoungs/DATA1/SWAROBO-Data/241220-인천드론시험비행장-수동촬영테스트/REC_0002"  # Directory to save the extracted frames
    frame_interval = 30  # Save a frame every 30 frames (1 frame per second for 30 FPS video)

    save_frames_from_video(video_path, output_dir, frame_interval)
