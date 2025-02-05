import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class VideoPlayerApp:
    def __init__(self, root, concatenated_video, video_count, frames_per_video, scale=1):
        self.root = root
        self.concatenated_video = concatenated_video
        self.video_count = video_count
        self.frames_per_video = frames_per_video
        self.current_frame_index = 0
        self.current_video_index = 0  # Initialize the current video index
        self.scale = scale

        # Load the concatenated video
        self.cap = cv2.VideoCapture(self.concatenated_video)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # UI Setup
        self.video_label = tk.Label(root)
        self.video_label.pack(padx=10, pady=10)

        # Scrollbar for frame navigation
        self.frame_scrollbar = ttk.Scale(
            root, from_=0, to=self.frames_per_video - 1, orient="horizontal", command=self.on_frame_scroll
        )
        self.frame_scrollbar.pack(fill="x", padx=10, pady=5)

        # Scrollbar for video navigation
        self.video_scrollbar = ttk.Scale(
            root, from_=0, to=self.video_count - 1, orient="horizontal", command=self.on_video_scroll
        )
        self.video_scrollbar.pack(fill="x", padx=10, pady=5)

        # Display video info
        self.info_label = tk.Label(root, text="Video 1", font=("Arial", 14))
        self.info_label.pack(pady=5)

        # Bind the Escape key to quit the application
        root.bind("<Escape>", self.quit_app)

        # Update UI with the first frame
        self.update_frame_scrollbar_range()  # Initialize the frame scrollbar range
        self.update_frame()

    def on_video_scroll(self, value):
        """Handle video scrollbar movement."""
        new_video_index = int(float(value))  # New video index
        relative_frame_index = self.current_frame_index % self.frames_per_video  # Frame position within the current video

        # Update to the new video index
        self.current_video_index = new_video_index

        # Compute the new absolute frame index
        self.current_frame_index = (
            self.current_video_index * self.frames_per_video + relative_frame_index
        )

        # Update frame scrollbar range and position
        self.update_frame_scrollbar_range()

        # Update the displayed frame
        self.update_frame()

    def on_frame_scroll(self, value):
        """Handle frame scrollbar movement."""
        relative_frame_index = int(float(value))  # Frame within the selected video
        self.current_frame_index = (
            self.current_video_index * self.frames_per_video + relative_frame_index
        )  # Absolute frame index
        self.update_frame()  # Display the updated frame

    def update_frame_scrollbar_range(self):
        """Update the range of the frame scrollbar for the selected video."""
        self.frame_scrollbar.config(from_=0, to=self.frames_per_video - 1)
        relative_frame_index = self.current_frame_index % self.frames_per_video
        self.frame_scrollbar.set(relative_frame_index)  # Preserve current frame position

    def update_frame(self):
        """Display the current frame of the concatenated video."""
        try:
            # Set the video position to the current frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)
            ret, frame = self.cap.read()

            # Check if the frame was read successfully
            if not ret:
                print(f"Error: Could not read frame {self.current_frame_index}.")
                return

            # Resize the frame to fit within a specified dimension
            h, w, _ = frame.shape
            new_width = int(w / self.scale)
            new_height = int(h / self.scale)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

            # Convert the frame for tkinter display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            img = Image.fromarray(frame)  # Create a PIL image
            img_tk = ImageTk.PhotoImage(img)  # Convert to ImageTk format

            # Update the tkinter Label
            self.video_label.img_tk = img_tk  # Keep reference to avoid garbage collection
            self.video_label.config(image=img_tk)

            # Update the video title and frame info
            video_index = self.current_video_index + 1
            relative_frame_index = self.current_frame_index % self.frames_per_video + 1
            self.info_label.config(text=f"{video_index}0k steps({int(video_index)//3}h:{int(video_index%3)*20}m), Frame {relative_frame_index}")

        except Exception as e:
            print(f"Error: {e}")

    def quit_app(self, event=None):
        """Quit the application."""
        self.close()  # Release resources
        self.root.destroy()  # Close the tkinter window

    def close(self):
        """Release video resources on exit."""
        self.cap.release()

# Main Application
if __name__ == "__main__":
    concatenated_video = "/home/chanyoungs/Documents/SWAROBO/swarobo/renders/2_3_4-jpeg-colmap/300k/concatenated_video.mp4"  # Path to the concatenated video
    video_count = 30  # Number of videos
    frames_per_video = 2040  # Assuming each video has 300 frames (adjust accordingly)

    max_width, max_height = 640, 360

    root = tk.Tk()
    root.title("Optimized Video Player with Scrollbars")

    app = VideoPlayerApp(root, concatenated_video, video_count, frames_per_video, scale=2)

    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
