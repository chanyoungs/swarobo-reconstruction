import os
import re
import time
import glob
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def sanitize_filename(name):
    """Cleans a string to be a valid filename, preserving hyphens."""
    base_name = os.path.basename(name)
    name_no_ext = os.path.splitext(base_name)[0]
    s = re.sub(r'[.\[\]\s\(\)]', '_', name_no_ext)
    s = re.sub(r'[^a-zA-Z0-9_-\uac00-\ud7a3]', '_', s)
    s = re.sub(r'__+', '_', s)
    s = s.strip('_')
    return s

def get_user_params():
    """Gets user input for save directory, frame step, and preset name."""
    root = tk.Tk()
    root.withdraw()

    save_dir = filedialog.askdirectory(title="Select a Folder to Save Frames")
    if not save_dir:
        return None, None, None

    frame_step = simpledialog.askinteger("Frame Step", "Export one frame every:", initialvalue=24, minvalue=1, parent=root)
    if not frame_step:
        return None, None, None
        
    preset_name = simpledialog.askstring("Render Preset", "Enter the EXACT name of your EXR render preset:", initialvalue="Linear_EXR", parent=root)
    if not preset_name:
        return None, None, None

    return save_dir, frame_step, preset_name

def confirm_color_space():
    """
    Asks the user to confirm they have set the correct linear color space.
    Returns True if they confirm, False otherwise.
    """
    root = tk.Tk()
    root.withdraw()
    
    confirmation = messagebox.askyesno(
        title="Color Space Confirmation",
        message="Is your render preset and project color management set up for a linear EXR export?\n\n(e.g., Project 'Output Color Space' is set to 'DaVinci Wide Gamut / Intermediate')"
    )
    
    if not confirmation:
        instructions = (
            "Action Canceled.\n\n"
            "Please ensure your Render Preset and Project Settings are configured for a linear workflow and run the script again."
        )
        messagebox.showinfo("Instructions", instructions)
        return False
        
    return True

def export_frames(save_dir, frame_step, preset_name):
    """Exports frames one-by-one by repeatedly loading a render preset."""
    print("--- Starting Export ---")
    resolve = app.GetResolve()
    project = resolve.GetProjectManager().GetCurrentProject()

    # Check if preset exists before starting
    if not project.LoadRenderPreset(preset_name):
        messagebox.showerror("Error", f"Render preset '{preset_name}' not found.\n\nPlease go to the Deliver page, create an EXR render setting, and save it as a preset with that name.")
        return
        
    timeline = project.GetCurrentTimeline()
    if not timeline:
        messagebox.showerror("Error", "No active timeline found.")
        return

    items = timeline.GetItemListInTrack("video", 1)
    if not items:
        messagebox.showinfo("Finished", "No video clips found on Video Track 1.")
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
            # Load the preset for each job
            project.LoadRenderPreset(preset_name)
            
            # Now, only set the per-frame overrides
            project.SetRenderSettings({
                "TargetDir": clip_dir,
                "CustomName": sanitized_name,
                "MarkIn": frame,
                "MarkOut": frame,
            })

            jobId = project.AddRenderJob()
            project.StartRendering([jobId]) # Render this single job

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
        if confirm_color_space():
            save_dir, frame_step, preset_name = get_user_params()
            if save_dir and frame_step and preset_name:
                export_frames(save_dir, frame_step, preset_name)
                print("\n--- Done! ---")
        else:
            print("--- Script Canceled by User (Color Space Not Confirmed) ---")