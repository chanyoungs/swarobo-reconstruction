import os
import re
import time
import glob
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def sanitize_filename(name):
    """Cleans a string to be a valid filename."""
    base_name = os.path.basename(name)
    name_no_ext = os.path.splitext(base_name)[0]
    s = re.sub(r'[.\[\]\s\(\)]', '_', name_no_ext)
    s = re.sub(r'[^a-zA-Z0-9_-_\uac00-\ud7a3]', '_', s)
    s = re.sub(r'__+', '_', s)
    s = s.strip('_')
    return s

def get_user_params():
    """Gets user input for save directory and frame step."""
    root = tk.Tk()
    root.withdraw()
    save_dir = filedialog.askdirectory(title="Select a Folder to Save Frames")
    if not save_dir:
        return None, None
    frame_step = simpledialog.askinteger("Frame Step", "Export one frame every:", initialvalue=24, minvalue=1, parent=root)
    if not frame_step:
        return None, None
    return save_dir, frame_step

def confirm_color_space():
    """
    Asks the user to confirm they have set the correct linear color space.
    Returns True if they confirm, False otherwise.
    """
    root = tk.Tk()
    root.withdraw()
    
    confirmation = messagebox.askyesno(
        title="Color Space Confirmation",
        message="Have you set the project's 'Output Color Space' to a linear format (e.g., 'DaVinci Wide Gamut / Intermediate')?\n\nThis is required for a correct linear EXR export."
    )
    
    if not confirmation:
        instructions = (
            "Action Canceled.\n\n"
            "To set the correct color space:\n"
            "1. Go to File -> Project Settings -> Color Management.\n"
            "2. Set 'Color science' to 'DaVinci YRGB Color Managed'.\n"
            "3. Set 'Timeline color space' to 'DaVinci Wide Gamut / Intermediate'.\n"
            "4. IMPORTANT: Set 'Output color space' to the SAME value (e.g., 'DaVinci Wide Gamut / Intermediate').\n\n"
            "Please apply these settings and run the script again."
        )
        messagebox.showinfo("Instructions", instructions)
        return False
        
    return True

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
        messagebox.showinfo("Finished", "No video clips found on the specified track.")
        return

    print(f"Found {len(items)} clips to process...")
    project.DeleteAllRenderJobs()

    for item in items:
        media_pool_item = item.GetMediaPoolItem()
        if not media_pool_item:
            continue

        original_name = media_pool_item.GetName()
        sanitized_name = sanitize_filename(original_name)
        
        clip_dir = os.path.join(save_dir, sanitized_name)
        os.makedirs(clip_dir, exist_ok=True)
        print(f"\nProcessing clip: '{original_name}' -> Saving to '{clip_dir}'")

        start_frame = item.GetStart()
        end_frame = item.GetEnd()

        output_frame_counter = 1

        for frame in range(start_frame, end_frame, frame_step):
            project.SetRenderSettings({
                "TargetDir": clip_dir,
                "CustomName": sanitized_name,
                "Format": "exr",
                "Codec": "Linear",
                "MarkIn": frame,
                "MarkOut": frame,
            })

            jobId = project.AddRenderJob()
            project.StartRendering([jobId])

            while project.IsRenderingInProgress():
                time.sleep(0.5)

            status = project.GetRenderJobStatus(jobId)
            
            if status.get('JobStatus') == 'Complete':
                try:
                    list_of_files = glob.glob(os.path.join(clip_dir, f'{sanitized_name}*.exr'))
                    if not list_of_files:
                        print(f"  - Rendered frame {frame}, but could not find output file to rename.")
                        continue
                    
                    source_filepath = max(list_of_files, key=os.path.getctime)
                    
                    dest_filename = f"{sanitized_name}_{output_frame_counter:04d}.exr"
                    dest_filepath = os.path.join(clip_dir, dest_filename)

                    os.rename(source_filepath, dest_filepath)
                    print(f"  - Saved {dest_filename}")

                except (OSError, ValueError) as e:
                    print(f"  - Error renaming file for frame {frame}: {e}")
            else:
                print(f"  - FAILED to save frame {frame}. Status: {status.get('JobStatus')}")
            
            project.DeleteRenderJob(jobId)
            
            output_frame_counter += frame_step

    messagebox.showinfo("Finished", "Frame extraction is complete!")
    project.DeleteAllRenderJobs()

if __name__ == "__main__":
    try:
        app.GetResolve()
    except NameError:
        messagebox.showerror("Error", "This script must be run from DaVinci Resolve's 'Workspace > Scripts' menu.")
    else:
        # --- NEW LOGIC IS HERE ---
        # First, confirm the color space settings with the user.
        if confirm_color_space():
            # If they click "Yes", then get the other parameters and run the export.
            save_dir, frame_step = get_user_params()
            if save_dir and frame_step:
                export_frames(save_dir, frame_step)
                print("\n--- Done! ---")
        else:
            # If they click "No", the script will have shown instructions and will now end.
            print("--- Script Canceled by User (Color Space Not Set) ---")