# youtube-downloader

source code for a program that uses yt dlp to download youtube videos as a video or music file

## to use
pretty straightforward: git clone or make a `main.py` file and copy-paste the source code. make sure to pip install any imports that don’t come with python and ensure ffmpeg is installed and added to your system path. after that, just run it.

## extra stuff
- **folder selection:** if you select a folder, the downloaded file goes there. if no folder is selected, it makes a default folder called `youtube_output`. if you pick a root directory (like `C:`), the file just downloads there.  
- **audio only:** choosing audio only automatically converts the video to mp3 using ffmpeg.  
- **canceling downloads:** click cancel to stop a download; it will delete any partial files to keep the folder clean (if you cancel right as the download finishes it freezes but i cba to fix it).  
- **opening folder:** after download, the open folder button highlights the file, though it opens slightly above it, so you might need to scroll a bit.
