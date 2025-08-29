import time
import glob
import os
import sys
import argparse

def print_progress_bar(current, total, bar_length=40):
    """Print a simple progress bar."""
    progress = min(current / total, 1.0)  # Clamp to 1.0
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percent = progress * 100
    sys.stdout.write(f"\r|{bar}| {percent:6.2f}% ({current}/{total})")
    sys.stdout.flush()


def track_png_progress(directory, total_files, interval):
    """Track progress by counting .png files in a directory recursively."""
    try:
        while True:
            # Recursive glob search for PNG files
            files = glob.glob(os.path.join(directory, "**", "*.png"), recursive=True)
            count = len(files)

            # Print progress bar
            print_progress_bar(count, total_files)

            # Stop if we've reached or exceeded total
            if count >= total_files:
                print("\n✅ Target reached!")
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n⏹ Stopped by user.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track PNG creation progress.")
    parser.add_argument(
        "-d", "--directory", type=str, default=".",
        help="Directory to scan for PNG files (default: current directory)"
    )
    parser.add_argument(
        "-t", "--total", type=int, required=True,
        help="Total number of PNG files expected"
    )
    parser.add_argument(
        "-i", "--interval", type=float, default=1,
        help="Interval in seconds between scans (default: 1)"
    )

    args = parser.parse_args()

    track_png_progress(args.directory, args.total, args.interval)
