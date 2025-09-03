import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import threading
import queue
import os
import re
import sys

class BatchProcessorApp:
    """
    A GUI application to drag and drop folders and process them sequentially
    with a given batch script.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Folder Processor")
        self.root.geometry("700x600")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        # --- Configuration ---
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.batch_script_path = os.path.join(script_dir, "train_postshot.bat")
        
        # --- Status Tracking ---
        self.folder_items = [] # Will store {'path': str, 'status': str, 'error': str|None, 'progress_text': str, 'log_history': list}
        self.STATUS_ICONS = {
            "pending": "⚪",
            "processing": "⚙️",
            "done": "✅",
            "error": "❌"
        }
        self.last_log_message = ""
        self.log_view_index = None # Tracks which item's logs are visible
        self.currently_processing_index = None # Tracks the index of the item being processed

        self.log_queue = queue.Queue()
        self.create_widgets()

        self.folder_listbox.drop_target_register(DND_FILES)
        self.folder_listbox.dnd_bind('<<Drop>>', self.on_drop)
        self.root.after(100, self.process_log_queue)

    def create_widgets(self):
        """Creates and arranges all the GUI widgets in the main window."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        main_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="Drag and Drop Folders Below:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")

        list_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.folder_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, bg="#f0f0f0", relief="solid", borderwidth=1, font=("Consolas", 9))
        self.folder_listbox.grid(row=0, column=0, sticky="nsew")
        self.folder_listbox.bind('<<ListboxSelect>>', self.on_listbox_click)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.folder_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.folder_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.start_button = ttk.Button(button_frame, text="Start Processing", command=self.start_processing_thread, style="Accent.TButton")
        self.start_button.pack(side="left", expand=True, fill="x", padx=5)

        self.clear_button = ttk.Button(button_frame, text="Clear List", command=self.clear_list)
        self.clear_button.pack(side="left", expand=True, fill="x", padx=5)
        
        log_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        log_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(log_frame, text="Logs:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", height=10, bg="#2b2b2b", fg="white", font=("Consolas", 9), relief="solid", borderwidth=1)
        self.log_text.grid(row=1, column=0, sticky="nsew")
        
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), foreground="white", background="#0078d4", relief="flat")
        style.map("Accent.TButton", background=[('active', '#005a9e')])

    def on_drop(self, event):
        path_string = event.data
        paths = re.findall(r'\{[^{}]+\}|\S+', path_string)
        for path in paths:
            clean_path = path.strip('{} ').strip()
            if os.path.isdir(clean_path):
                item = {'path': clean_path, 'status': 'pending', 'error': None, 'progress_text': '', 'log_history': []}
                self.folder_items.append(item)
                self.update_listbox_item(len(self.folder_items) - 1, 'pending')

    def clear_list(self):
        self.folder_listbox.delete(0, tk.END)
        self.folder_items.clear()
        self.last_log_message = ""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def start_processing_thread(self):
        if not self.folder_items:
            self.log("No folders in the list to process.")
            return
        if not os.path.isfile(self.batch_script_path):
            self.log(f"ERROR: '{os.path.basename(self.batch_script_path)}' not found.")
            return

        for i in range(len(self.folder_items)):
            self.folder_items[i]['status'] = 'pending'
            self.folder_items[i]['error'] = None
            self.folder_items[i]['progress_text'] = ''
            self.folder_items[i]['log_history'] = []
            self.update_listbox_item(i, 'pending')
            
        self.start_button.config(state="disabled")
        self.clear_button.config(state="disabled")

        thread = threading.Thread(target=self.processing_worker, args=(self.folder_items[:],), daemon=True)
        thread.start()

    def processing_worker(self, folders_to_process):
        self.log("--- Starting Batch Process ---")
        for i, item in enumerate(folders_to_process):
            folder_path = item['path']
            self.log_queue.put(('SELECT_AND_CLEAR_LOG', i))
            self.log_queue.put(('UPDATE_STATUS', i, 'processing'))
            self.log(f"\n({i+1}/{len(folders_to_process)}) Processing: {os.path.basename(folder_path)}", i)
            
            command = [self.batch_script_path, folder_path]
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    self.log(line, i)
                    self._parse_progress_from_line(i, line)
                
                process.stdout.close()
                return_code = process.wait()
                stderr_output = process.stderr.read().strip()

                if return_code != 0:
                    error_header = f"Script finished with exit code {return_code}."
                    if stderr_output: 
                        error_header += f"\n\n--- Error Stream ---\n{stderr_output}"
                    
                    self.log_queue.put(('UPDATE_ERROR', i, error_header))
                else:
                    self.log(f"Finished processing: {os.path.basename(folder_path)}", i)
                    self.log_queue.put(('UPDATE_PROGRESS', i, ''))
                    self.log_queue.put(('UPDATE_STATUS', i, 'done'))

            except Exception as e:
                self.log_queue.put(('UPDATE_ERROR', i, f"An exception occurred: {e}"))
        
        self.log("\n--- All folders have been processed. ---")
        self.log_queue.put("TASK_COMPLETE")

    def _parse_progress_from_line(self, index, line):
        """Parses log lines for progress updates and queues them."""
        # Camera Tracking Step n/4
        match_cam = re.match(r"Camera Tracking Step (\d+/\d+):", line)
        if match_cam:
            progress_text = f"📷 {match_cam.group(1)}"
            self.log_queue.put(('UPDATE_PROGRESS', index, progress_text))
            return

        # Training Radiance Field: n%
        match_rad = re.match(r"Training Radiance Field: (\d+)%", line)
        if match_rad:
            percent = int(match_rad.group(1))
            progress_bar = self._create_progress_bar(percent)
            self.log_queue.put(('UPDATE_PROGRESS', index, progress_bar))
            return

    def _create_progress_bar(self, percentage, width=10):
        """Creates a text-based progress bar string."""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '─' * (width - filled)
        return f"[{bar}] {percentage}%"

    def log(self, message, index=None):
        self.log_queue.put((message, index))

    def _get_progress_prefix(self, msg):
        if not isinstance(msg, str): return None
        if msg.startswith("Training Radiance Field:"): return "Training Radiance Field:"
        match = re.match(r"(Camera Tracking Step \d+/\d+:)", msg)
        if match: return match.group(1)
        return None

    def on_listbox_click(self, event):
        """Shows the stored logs for the selected item."""
        selection = self.folder_listbox.curselection()
        if not selection: return
        
        index = selection[0]
        self.log_view_index = index # Track that user is viewing this index
        item = self.folder_items[index]
            
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        
        # Display the stored history for the selected item
        if item['log_history']:
            log_content = "\n".join(item['log_history'])
            if item['status'] == 'error' and item['error']:
                log_content = f"ERROR: {item['error']}\n\n--- Full Log ---\n{log_content}"
            self.log_text.insert(tk.END, log_content)
        
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        # Reset last log message to ensure line replacement works correctly on this view
        self.last_log_message = item['log_history'][-1] if item['log_history'] else ""

    def update_listbox_item(self, index, new_status=None):
        """Updates the text and color of an item in the listbox."""
        if not (0 <= index < len(self.folder_items)): return

        if new_status: self.folder_items[index]['status'] = new_status
        item = self.folder_items[index]
        status = item['status']
        
        icon = self.STATUS_ICONS.get(status, "❓")
        progress = item.get('progress_text', '')
        # Format with padding for alignment
        display_text = f"{icon} {progress:<18} {item['path']}"
        
        # Check if item exists before deleting
        if self.folder_listbox.size() > index:
             self.folder_listbox.delete(index)
        self.folder_listbox.insert(index, display_text)
        
        color_map = {"done": "green", "processing": "#0078d4", "error": "red"}
        self.folder_listbox.itemconfig(index, {'fg': color_map.get(status, 'black')})

    def _switch_log_view(self, index):
        """Selects an item and prepares the log view for its content."""
        if index is None: return
        self.folder_listbox.selection_clear(0, tk.END)
        self.folder_listbox.selection_set(index)
        
        item = self.folder_items[index]
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        
        # Display the history so far
        if item['log_history']:
            self.log_text.insert(tk.END, "\n".join(item['log_history']))
            
        self.log_text.config(state="disabled")
        self.last_log_message = item['log_history'][-1] if item['log_history'] else ""
        self.log_view_index = index

    def process_log_queue(self):
        try:
            while True:
                message_obj = self.log_queue.get_nowait()
                if message_obj == "TASK_COMPLETE":
                    self.start_button.config(state="normal")
                    self.clear_button.config(state="normal")
                    self.last_log_message = ""
                    self.currently_processing_index = None
                
                elif isinstance(message_obj, tuple):
                    # Handle special commands
                    if isinstance(message_obj[0], str) and message_obj[0].isupper():
                        msg_type, index, *payload = message_obj
                        if msg_type == 'UPDATE_STATUS':
                            self.update_listbox_item(index, new_status=payload[0])
                        elif msg_type == 'UPDATE_PROGRESS':
                            self.folder_items[index]['progress_text'] = payload[0]
                            self.update_listbox_item(index)
                        elif msg_type == 'UPDATE_ERROR':
                            self.folder_items[index]['error'] = payload[0]
                            self.folder_items[index]['progress_text'] = "ERROR"
                            self.update_listbox_item(index, new_status='error')
                        elif msg_type == 'SELECT_AND_CLEAR_LOG':
                            # Auto-switch view only if user was viewing the previously processing item
                            should_auto_switch = (self.log_view_index is None or self.log_view_index == self.currently_processing_index)
                            self.currently_processing_index = index
                            if should_auto_switch:
                                self._switch_log_view(index)

                    # Handle log messages
                    else:
                        log_message, index = message_obj
                        
                        # Store log in history, cleaning it in the process
                        if index is not None and 0 <= index < len(self.folder_items):
                            history = self.folder_items[index]['log_history']
                            if history:
                                last_line = history[-1]
                                current_prefix = self._get_progress_prefix(log_message)
                                previous_prefix = self._get_progress_prefix(last_line)
                                if current_prefix is not None and current_prefix == previous_prefix:
                                    history.pop() # Remove previous line
                            history.append(log_message)
                        
                        # Display log if currently viewed
                        if index == self.log_view_index:
                            current_prefix = self._get_progress_prefix(log_message)
                            previous_prefix = self._get_progress_prefix(self.last_log_message)
                            self.log_text.config(state="normal")
                            if current_prefix is not None and current_prefix == previous_prefix:
                                self.log_text.delete("end-2l", "end-1l")
                            self.log_text.insert(tk.END, log_message + "\n")
                            self.log_text.see(tk.END)
                            self.log_text.config(state="disabled")
                            self.last_log_message = log_message

        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

if __name__ == "__main__":
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
    except ImportError:
        root = tk.Tk()
        root.withdraw() 
        messagebox.showerror("Dependency Missing", "The 'tkinterdnd2' library is required.\n\nPlease run: pip install tkinterdnd2")
        exit()

    root = TkinterDnD.Tk()
    app = BatchProcessorApp(root)
    root.mainloop()

