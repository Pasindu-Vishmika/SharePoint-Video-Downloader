import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
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

        
def update_download_label(save_name):
    download_label.config(text=f"Downloading {save_name}")

def update_progress_label(progress):
    progress_label.config(text=f"{progress:.2f}%")

def download_video():
    vlink = vlink_entry.get().strip()
    save_name = save_name_entry.get().strip() + ".mp4"
    update_download_label(save_name)
    new_filename = generate_filename()

    try:
        subprocess.run(["dependencies\\curl\\bin\\curl.exe", vlink, "-o", new_filename], check=True)
        output_text.insert(tk.END, "[+] Video manifest file downloaded\n")
        total_duration = get_video_duration(new_filename)
        if total_duration == 0:
            output_text.insert(tk.END, "[-] Error: Failed to get video duration.\n")
            return
        progress_bar['value'] = 0
        download_thread = threading.Thread(target=download_video_thread, args=(new_filename, total_duration, save_name))
        download_thread.start()
    except subprocess.CalledProcessError as e:
        output_text.insert(tk.END, "[-] Failed to download video manifest file.\n")
        if os.path.exists(new_filename):
            os.remove(new_filename)


def download_video_thread(new_filename, total_duration, save_name):
    try:
        cmd = ["dependencies\\ffmpeg\\bin\\ffmpeg.exe", "-protocol_whitelist", "file,http,https,tcp,tls", "-i", new_filename, "-codec", "copy", save_name]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

        for line in process.stdout:
            time_match = re.search(r"time=(\d+:\d+:\d+\.\d+)", line)
            if time_match:
                time_str = time_match.group(1)
                downloaded_duration = sum(x * 60 ** i for i, x in enumerate(map(float, reversed(time_str.split(":")))))
                progress = (downloaded_duration / total_duration) * 100
                update_progress_label(progress)
                progress_bar['value'] = progress
                root.update_idletasks()
        
        process.communicate()
        root.after(0, lambda: messagebox.showinfo("Success", f"{save_name} Video Downloaded Successfully. !"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to download {save_name}. Error: {str(e)}"))
        if os.path.exists(save_name):
            os.remove(save_name)

root = tk.Tk()
root.title("Video Downloader")

# Define and place the video manifest link label and entry field
vlink_label = ttk.Label(root, text="Enter video manifest link:")
vlink_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
vlink_entry = ttk.Entry(root, width=50)
vlink_entry.grid(row=0, column=1, padx=10, pady=10)

# Define and place the video name label and entry field
save_name_label = ttk.Label(root, text="Enter video name to save:")
save_name_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
save_name_entry = ttk.Entry(root, width=50)
save_name_entry.grid(row=1, column=1, padx=10, pady=10)

# Create a paste button next to the vlink_entry
paste_button = ttk.Button(root, text="Paste", command=paste_from_clipboard)
paste_button.grid(row=0, column=2, padx=10, pady=10)

download_button = ttk.Button(root, text="Download", command=download_video)
download_button.grid(row=2, column=0, columnspan=2, pady=20)

# New browse button to select download directory
browse_button = ttk.Button(root, text="Browse", command=select_download_directory)
browse_button.grid(row=1, column=2, padx=10, pady=10)

# Define and place the download button
download_button = ttk.Button(root, text="Download", command=download_video)
download_button.grid(row=2, column=0, columnspan=2, pady=20)

# Define and place the download status label
download_label = ttk.Label(root, text="Waiting for download...")
download_label.grid(row=3, column=0, columnspan=2, padx=10)

# Define and place the progress percentage label
progress_label = ttk.Label(root, text="")
progress_label.grid(row=4, column=0, columnspan=2, padx=10)

# Define and place the progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=2, padx=10)

# Define and place the scrolled text area for output logs
output_text = scrolledtext.ScrolledText(root, width=60, height=10)
output_text.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Start the GUI event loop
root.mainloop()
