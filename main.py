import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import yt_dlp
import webbrowser
import platform

DEFAULT_FOLDER = "youtube_output"
current_folder = {"path": DEFAULT_FOLDER}
last_downloaded = {"path": None}
os.makedirs(DEFAULT_FOLDER, exist_ok=True)

cancel_flag = threading.Event()


def download_video(url, quality, progress_hook_fn=None):
    output_dir = current_folder["path"]
    options = {
        "noplaylist": True,
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook_fn] if progress_hook_fn else None
    }

    if quality == "Audio only":
        options.update({
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        })
    else:
        options["format"] = f"bestvideo[height<={quality.replace('p', '')}] + bestaudio/best"

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(info)
        last_downloaded["path"] = filename.rsplit(
            '.', 1)[0] + ('.mp3' if quality == "Audio only" else '.' + info['ext'])
        try:
            ydl.download([url])
        except yt_dlp.utils.DownloadError:
            part_file = filename + ".part"
            if os.path.exists(part_file):
                os.remove(part_file)
            raise


def handle_progress(info):
    if cancel_flag.is_set():
        raise yt_dlp.utils.DownloadError("Download canceled")
    if info['status'] == 'downloading':
        total_bytes = info.get('total_bytes') or info.get(
            'total_bytes_estimate')
        downloaded_bytes = info.get('downloaded_bytes', 0)
        if total_bytes:
            percent = downloaded_bytes / total_bytes * 100
            progress_bar['value'] = percent
            status_label.config(text=f"Downloading... {percent:.1f}%")
    elif info['status'] == 'finished':
        progress_bar['value'] = 100
        status_label.config(text="Download complete!")


def download_thread(url, quality):
    cancel_flag.clear()
    try:
        status_label.config(text="Starting download...")
        download_video(url, quality, progress_hook_fn=handle_progress)
        if not cancel_flag.is_set():
            status_label.config(text="Download complete!")
            open_button.config(state="normal")
    except yt_dlp.utils.DownloadError as e:
        status_label.config(
            text="Download canceled" if cancel_flag.is_set() else "Download failed")
        print(e)
    finally:
        download_button.config(state="normal")


def start_download():
    url = url_entry.get().strip()
    if not url:
        status_label.config(text="Enter a URL")
        return
    url = url.split("&")[0]
    quality = quality_var.get()
    download_button.config(state="disabled")
    open_button.config(state="disabled")
    progress_bar['value'] = 0
    status_label.config(text="Initializing...")
    threading.Thread(target=download_thread, args=(
        url, quality), daemon=True).start()


def cancel_download():
    cancel_flag.set()
    progress_bar['value'] = 0
    status_label.config(text="Canceling...")


def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        current_folder["path"] = folder
        status_label.config(text=f"Folder set to: {folder}")
    else:
        current_folder["path"] = DEFAULT_FOLDER
        status_label.config(
            text=f"No folder selected. Using default: {DEFAULT_FOLDER}")


def open_folder():
    path = last_downloaded["path"]
    if platform.system() == "Windows" and path and os.path.exists(path):
        os.system(f'explorer /select,"{path}"')
    else:
        webbrowser.open(os.path.abspath(current_folder["path"]))


def update_quality_options(url):
    def task():
        try:
            with yt_dlp.YoutubeDL({}) as ydl:
                info = ydl.extract_info(url, download=False)
                heights = sorted({f['height']
                                 for f in info['formats'] if f.get('height')})
                options = [f"{h}p" for h in heights]
                if any(f['vcodec'] == 'none' for f in info['formats']):
                    options.append("Audio only")
                quality_dropdown['values'] = options
                if options:
                    quality_dropdown.current(0)
        except yt_dlp.utils.DownloadError as e:
            print("Failed to fetch formats", e)
            quality_dropdown['values'] = ["Default"]
            quality_dropdown.current(0)
    threading.Thread(target=task, daemon=True).start()


# --- GUI SETUP ---
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("650x450")
root.minsize(450, 400)
root.resizable(True, True)

for i in range(9):
    root.rowconfigure(i, weight=1)
root.columnconfigure(0, weight=1)

ttk.Label(root, text="YouTube Downloader", font=(
    "Arial", 16)).grid(row=0, column=0, pady=10)

url_entry = ttk.Entry(root)
url_entry.grid(row=1, column=0, sticky="ew", pady=5)
url_entry.config(width=50)

quality_var = tk.StringVar()
quality_dropdown = ttk.Combobox(
    root, textvariable=quality_var, state="readonly", width=15)
quality_dropdown.grid(row=2, column=0, pady=5)
quality_dropdown['values'] = ["Select URL first"]

ttk.Button(root, text="Select Download Folder",
           command=choose_folder).grid(row=3, column=0, pady=5)

url_entry.last_url = ""


def on_url_change(_):
    url = url_entry.get().strip()
    if url != getattr(url_entry, "last_url", "") and url.startswith("http"):
        url_entry.last_url = url
        update_quality_options(url)


url_entry.bind("<KeyRelease>", on_url_change)

download_button = ttk.Button(root, text="Download", command=start_download)
download_button.grid(row=4, column=0, pady=5, ipadx=20, ipady=5)

progress_bar = ttk.Progressbar(root, mode='determinate')
progress_bar.grid(row=5, column=0, sticky="ew", padx=40, pady=5)

status_label = ttk.Label(root, text="Waiting...")
status_label.grid(row=6, column=0, pady=5)

open_button = ttk.Button(root, text="Open Folder",
                         command=open_folder, state="disabled")
open_button.grid(row=7, column=0, pady=5, ipadx=20, ipady=5)

cancel_button = ttk.Button(
    root, text="Cancel Download", command=cancel_download)
cancel_button.grid(row=8, column=0, pady=5, ipadx=20, ipady=5)

root.mainloop()
