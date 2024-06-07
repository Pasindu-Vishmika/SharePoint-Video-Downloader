# SharePoint Video Downloader

This is a simple GUI application developed using Python and Tkinter to download Microsoft SharePoint videos. The tool allows users to input a video manifest link and specify a download location and filename. It uses `ffmpeg` and `curl` for downloading and processing the video files.

## Features

- User-friendly interface with Tkinter
- Option to paste video link directly from the clipboard
- Select and set a custom download directory
- Real-time download progress monitoring
- Automatically delete temporary files after download
- Contact information and GitHub links for developers

## Disclaimer

This application is developed for educational purposes only. The developer does not assume any responsibility for the misuse of this application by any other parties or organizations. The user of this application is solely responsible for any consequences resulting from its use.

## Installation

### Prerequisites

- Python 3.x
- `pip` (Python package installer)

### Clone the Repository

```bash
git clone https://github.com/Pasindu-Vishmika/SharePoint-Video-Downloader.git
cd SharePoint-Video-Downloader
```

### Setup Dependencies

Use the provided bash script to install and set up the necessary dependencies.

1. Create a file named `setup.sh` in your project directory.
2. Copy and paste the following script into the `setup.sh` file:

    ```bash
    #!/bin/bash

    # Function to check if a command exists
    command_exists() {
        command -v "$1" >/dev/null 2>&1
    }

    # Install Python dependencies
    echo "Installing Python dependencies..."
    pip install tkinter

    # Create dependencies directory if not exists
    mkdir -p dependencies

    # Download and set up ffmpeg
    if command_exists ffmpeg; then
        echo "ffmpeg is already installed."
    else
        echo "Downloading ffmpeg..."
        mkdir -p dependencies/ffmpeg
        cd dependencies/ffmpeg
        curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz -o ffmpeg-release.tar.xz
        tar -xf ffmpeg-release.tar.xz --strip-components=1
        cd ../..
        echo "ffmpeg installed successfully."
    fi

    # Download and set up curl
    if command_exists curl; then
        echo "curl is already installed."
    else
        echo "Downloading curl..."
        mkdir -p dependencies/curl
        cd dependencies/curl
        curl -LO https://curl.se/download/curl-7.76.1-win64-mingw.zip
        unzip curl-7.76.1-win64-mingw.zip -d .
        cd ../..
        echo "curl installed successfully."
    fi
    echo "All dependencies installed successfully."
    ```

3. Make the script executable and run it:

    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

### Run the Application

```bash
python video_downloader.py
```
This project is licensed under the MIT License.
