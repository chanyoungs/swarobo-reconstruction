import os
import re
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def sanitize_filename(name):
    """
    Cleans a string to be a valid filename by:
    1. Removing the file extension.
    2. Replacing problematic characters (spaces, periods, brackets, braces) with underscores.
    3. Whitelisting safe characters (letters, numbers, underscores, hyphens, Korean).
    4. Collapsing multiple consecutive underscores into a single one.
    5. Removing any leading or trailing underscores.
    """
    base_name = os.path.basename(name)
    name_no_ext = os.path.splitext(base_name)[0]
    
    # Replace specific problematic characters (including round braces) with underscores
    s = re.sub(r'[.\[\]\s\(\)]', '_', name_no_ext)
    
    # Whitelist safe characters: letters, numbers, underscore, hyphen, and Korean Hangul syllables.
    # Anything NOT in this set will be replaced with an underscore.
    s = re.sub(r'[^a-zA-Z0-9_-_\uac00-\ud7a3]', '_', s)
    
    # Collapse 2 or more consecutive underscores into a single underscore
    s = re.sub(r'__+', '_', s)
    
    # Remove any leading or trailing underscores
    s = s.strip('_')
    
    return s

# --- GUI for parameters ---
def get_user_params():
    root = tk.Tk()
    root.withdraw()

    save_dir = filedialog.askdirectory(title="Select a Folder to Save Frames")
    if not save_dir:
        return None, None

    frame_step = simpledialog.askinteger("Frame Step", "Export one frame every:", initialvalue=24, minvalue=1, parent=root)
    if not frame_step:
        return None, None

    return save_dir, frame_step

# --- Main extraction logic ---
def export_frames(save_dir, frame_step):
    print("--- Starting Export ---")
    resolve = app.GetResolve()
    project = resolve.GetProjectManager().GetCurrentProject()
    timeline = project.GetCurrentTimeline()
    
    if not timeline:
        messagebox.showerror("Error", "No active timeline found.")
        return

    items = timeline.GetItemListInTrack("video", 1)
    if not items:
        messagebox.showinfo("Finished", "No video clips found on track 1.")
        return

    print(f"Found {len(items)} clips to process...")

    for item in items:
        media_pool_item = item.GetMediaPoolItem()
        if not media_pool_item:
            continue

        original_name = media_pool_item.GetName()
        sanitized_name = sanitize_filename(original_name)
        
        clip_dir = os.path.join(save_dir, sanitized_name)
        os.makedirs(clip_dir, exist_ok=True)
        print(f"\nProcessing clip: '{original_name}' -> Saving as '{sanitized_name}'")

        start_frame = item.GetStart()
        end_frame = item.GetEnd()

        for frame in range(start_frame, end_frame, frame_step):
            timeline.SetCurrentTimecode(str(frame))

            padded_frame_number = f"{frame:04d}"

            filename = os.path.join(
                clip_dir,
                f"{sanitized_name}_{padded_frame_number}.png"
            )

            success = project.ExportCurrentFrameAsStill(filename)
            
            if not success:
                print(f"  - Failed to save frame {frame} for {sanitized_name}")
            else:
                print(f"  - Saved {filename}")
            
    messagebox.showinfo("Finished", "Frame extraction is complete!")

if __name__ == "__main__":
    try:
        app.GetResolve()
    except NameError:
        messagebox.showerror("Error", "This script must be run from DaVinci Resolve's 'Workspace > Scripts' menu.")
    else:
        save_dir, frame_step = get_user_params()
        if save_dir and frame_step:
            export_frames(save_dir, frame_step)
            print("\n--- Done! ---")