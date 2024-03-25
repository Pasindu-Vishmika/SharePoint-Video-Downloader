import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext ,PhotoImage
import subprocess
import os
from datetime import datetime
import re
import threading

# Helper functions
def generate_filename():
    filename = f"response_{datetime.now().timestamp()}.txt"
    return filename

def get_video_duration(filename):
    result = subprocess.run(["dependencies\\ffmpeg\\bin\\ffmpeg.exe", "-i", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    duration_match = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", result.stdout)
    if duration_match:
        duration_str = duration_match.group(1)
        duration = sum(x * 60 ** i for i, x in enumerate(map(float, reversed(duration_str.split(":")))))
        return duration
    return 0

def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()
        vlink_entry.delete(0, tk.END)
        vlink_entry.insert(0, clipboard_text)
    except tk.TclError:
        output_text.insert(tk.END, "[-] There's nothing to paste from the clipboard.\n")
        
# New global variable to hold the selected download path
download_path = os.path.join(os.getcwd(), "Downloads")

def select_download_directory():
    global download_path
    chosen_directory = filedialog.askdirectory()
    if chosen_directory:  # If the user chose a directory
        download_path = chosen_directory
        output_text.insert(tk.END, f"[+] Download location set to: {download_path}\n")

        
def update_download_label(save_name, progress=None):
    if progress is not None:
        download_label.config(text=f"Downloading {save_name} {progress:.2f}%")
    else:
        download_label.config(text=f"Downloading {save_name}")

def update_progress_label(progress):
    progress_label.config(text=f"{progress:.2f}%")

def download_video():
    global download_path
    vlink = vlink_entry.get().strip()
    save_name = save_name_entry.get().strip() + ".mp4"
    update_download_label(save_name)
    
    # Ensure download_path exists. If not, create it.
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        output_text.insert(tk.END, f"[+] Created directory: {download_path}\n")

    new_filename = os.path.join(download_path, generate_filename())

    try:
        subprocess.run(["dependencies\\curl\\bin\\curl.exe", vlink, "-o", new_filename], check=True)
        output_text.tag_configure('sucesss', font="Lexend", foreground='#1877F2')
        output_text.insert(tk.END, f"[+] Video manifest file {generate_filename()} downloaded\n","sucesss")
        # ... rest of your existing code

        total_duration = get_video_duration(new_filename)
        if total_duration == 0:
            output_text.insert(tk.END, "[-] Error: Failed to get video duration.\n")
            return
        progress_bar['value'] = 0
        download_thread = threading.Thread(target=download_video_thread, args=(new_filename, total_duration, save_name))
        download_thread.start()
    except subprocess.CalledProcessError as e:
        output_text.tag_configure('error', font="Lexend", foreground='red')
        output_text.insert(tk.END, "[-] Failed to download video manifest file.\n","error")
        if os.path.exists(new_filename):
            os.remove(new_filename)


def download_video_thread(new_filename, total_duration, save_name):
    global download_path
    try:
        # Ensure the download path exists, create if it does not
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Construct the full path to save the video
        save_path = os.path.join(download_path, save_name)

        # Command to execute ffmpeg, which will handle the download
        cmd = [
            "dependencies\\ffmpeg\\bin\\ffmpeg.exe",
            "-protocol_whitelist", "file,http,https,tcp,tls",
            "-i", new_filename,
            "-codec", "copy",
            save_path
        ]

        # Run the command and process its output
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, universal_newlines=True
        )

        # Monitor ffmpeg output for progress
        for line in process.stdout:
            time_match = re.search(r"time=(\d+:\d+:\d+\.\d+)", line)
            if time_match:
                time_str = time_match.group(1)
                downloaded_duration = sum(
                    x * 60 ** i for i, x in enumerate(map(float, reversed(time_str.split(":"))))
                )
                progress = (downloaded_duration / total_duration) * 100
                update_progress_label(progress)
                progress_bar['value'] = progress
                root.update_idletasks()

        # Wait for the subprocess to finish
        process.communicate()

        # Check for ffmpeg process return code
        if process.returncode != 0:
            raise Exception(f"ffmpeg exited with return code {process.returncode}")

        # Notify user of success
        root.after(0, lambda: messagebox.showinfo("Success", f"{save_name} Video Downloaded Successfully."))

    except Exception as e:
        # Log any errors to the GUI and remove partially downloaded files
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to download {save_name}. Error: {str(e)}"))
        output_text.insert(tk.END, f"[-] Failed to download {save_name}. Error: {str(e)}\n")

        # Check if the file exists and remove it to avoid incomplete downloads
        if os.path.exists(save_path):
            os.remove(save_path)

    finally:
        # Cleanup: Delete the temporary manifest file regardless of success or failure
        if os.path.exists(new_filename):
            os.remove(new_filename)
            output_text.insert(tk.END, f"[+] Temporary file {new_filename} deleted.\n")



# UI Customizations
LARGE_FONT = ("Manrope", 12)
SMALL_FONT = ("Verdana", 8)
BUTTON_FONT = ("Manrope", 10)
BUTTON_STYLE = {"padx": 10, "pady": 5, "borderwidth": 0}
LABEL_STYLE = {"padx": 10, "pady": 5}
ENTRY_WIDTH = 50
PROGRESSBAR_STYLE = {"length": 300, "style": "green.Horizontal.TProgressbar"}
button_width = 10


# Configure the main window
root = tk.Tk()
root.title("Video Downloader")
root.iconbitmap('dependencies\\images\\mainicon.ico')

window_width = 871
window_height = 480
root.geometry(f"{window_width}x{window_height}")
root.resizable(False, False)

# Configure style
style = ttk.Style()
style.configure("TLabel", font=LARGE_FONT, anchor="center")
style.configure("TEntry", font=('Manrope', 12))
style.configure("TButton", font=('Manrope', 10))
style.configure("TProgressbar", thickness=20, anchor="center")
style.configure("Rounded.TEntry", padding=5, relief=tk.FLAT, background="white", foreground="black")


def styled_button(parent, text, command):
    return tk.Button(parent, text=text, fg="white", bg="#1877F2", font=BUTTON_FONT,
                     padx=BUTTON_STYLE["padx"], pady=BUTTON_STYLE["pady"],
                     borderwidth=BUTTON_STYLE["borderwidth"], command=command)
    


# Content Frame
content_frame = ttk.Frame(root)
content_frame.place(relx=0.5, rely=0.5, anchor="center")

progress_label = ttk.Label(content_frame, text="0%", style="TLabel")
progress_label.grid(row=4, column=0, columnspan=3, pady=10)  # Adjust row and column to fit your layout
#download_button.grid(row=2, column=0, columnspan=3, padx=10, pady=20, sticky='ew')

# Place widgets within the content frame
vlink_label = ttk.Label(content_frame, text="Enter video manifest link:")
vlink_label.grid(row=0, column=0, padx=10, pady=5)

vlink_entry = ttk.Entry(content_frame, width=ENTRY_WIDTH, style="Rounded.TEntry")
vlink_entry.grid(row=0, column=1, pady=8)

save_name_label = ttk.Label(content_frame, text="Enter video name to save:")
save_name_label.grid(row=1, column=0, padx=10, pady=5)

save_name_entry = ttk.Entry(content_frame, width=ENTRY_WIDTH, style="Rounded.TEntry")
save_name_entry.grid(row=1, column=1, pady=5)


paste_button = styled_button(content_frame, "Paste", paste_from_clipboard)
paste_button.config(width=button_width)
paste_button.grid(row=0, column=2, padx=10, pady=5, sticky='ew')


browse_button = styled_button(content_frame, "Browse", select_download_directory)
browse_button.config(width=button_width)
browse_button.grid(row=1, column=2, padx=10, pady=5, sticky='ew')

download_button = styled_button(content_frame, "Download", download_video)
download_button.grid(row=2, column=0, columnspan=3, padx=10, pady=20, sticky='ew')


progress_bar = ttk.Progressbar(content_frame, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

download_label = ttk.Label(content_frame, text="Waiting for download...")
download_label.grid(row=4, column=0, columnspan=3, pady=5)

output_text = scrolledtext.ScrolledText(content_frame, width=80, height=10)
output_text.grid(row=5, column=0, columnspan=3, pady=10)

bottom_frame = ttk.Frame(root)
bottom_frame.pack(side="bottom", fill="x", expand=False)

# Disclaimer label
disclaimer_label = ttk.Label(
    bottom_frame,
    text=("DISCLAIMER: This application is developed for educational purposes only. "
          "The developer does not assume any responsibility for the misuse of this "
          "application by any other parties or Organization. The user of this application"
          "is solely responsible for any consequences resulting from its use."),
    font=('Abel', 8),
    anchor="center",
    justify="center",
    foreground="red",
    wraplength=window_width  # Adjust wraplength to the width of your window for proper text wrapping
)
disclaimer_label.pack(side="top", fill="x", padx=10, pady=(5, 0))

# Copyright label
copyright_label = ttk.Label(
    bottom_frame,
    text="© All rights reserved Pasindu Vishmika",
    font=('Segoe UI', 8, 'bold'),
    anchor="center"
)
copyright_label.pack(side="top", fill="x", padx=10)

# Contact Us button
contact_us_button = ttk.Button(
    bottom_frame,
    text="Contact Us",
    command=lambda: messagebox.showinfo("Contact", "Contact Us clicked!")
)
contact_us_button.pack(side="top", pady=(4, 10))

# Start the main loop
root.mainloop()