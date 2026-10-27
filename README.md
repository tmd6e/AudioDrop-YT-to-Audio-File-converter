# AudioDrop

A small Windows desktop app that turns a YouTube video URL into audio. Paste a link, choose a format and destination folder, then click **Download audio**.

Use the optional **Filename** field to name your download. Leave it blank to use the video title and ID. The selected format supplies the extension automatically. Existing files are not overwritten; choose another name to keep a separate copy.

Supports MP3, WAV, FLAC, M4A, AAC, OGG/Vorbis, Opus, and ALAC. Includes progress messages, a folder browser, saved preferences, and an Open download folder button. Playlist URLs download a single video.

## Run on Windows

1. Install FFmpeg (including ffprobe) and Node.js, and add their executable folders to PATH. Restart the app after installation.
2. Download `AudioDrop.exe` from a GitHub release and double-click it. Python is included in the executable; FFmpeg and Node.js are separate prerequisites.
3. Paste a YouTube URL, choose a format, browse to a folder, and download.

Downloads default to `%USERPROFILE%\Downloads\AudioDrop`. Preferences are stored in `%LOCALAPPDATA%\AudioDrop\settings.json`. WAV and FLAC cannot restore quality missing from the original audio. Private, age-restricted, or blocked videos may fail; the app shows the downloader error.

## Run from source

Install Python 3.10 or newer (3.12 recommended), FFmpeg, and Node.js. Double-click `Launch AudioDrop.bat`, or run:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python audio_drop.py
```

`Update downloader.bat` updates a source installation when YouTube changes. Executable users need a rebuilt release. After updating dependencies, test and update the version pin before releasing.

## Build and test

On Windows, in an activated Python virtual environment:

```powershell
./build.ps1
python -m unittest discover -s tests -v
```

The executable is written to `dist/AudioDrop.exe`. Before publishing, launch it on Windows, select a folder, download a video you can access, and verify playback. Unit tests mock network downloads; they do not verify live YouTube availability.

## Publish on GitHub

Create an empty GitHub repository, then run these commands from this folder, substituting your repository URL:

```powershell
git init -b main
git add .
git commit -m "Initial AudioDrop app"
git remote add origin https://github.com/YOUR-ACCOUNT/AudioDrop.git
git push -u origin main
```

The Windows workflow builds an executable on pushes to main, pull requests, and manual runs. Download it from the workflow's **AudioDrop-Windows** artifact.

To prepare a release:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

The workflow creates a **draft** GitHub release with the executable attached. Test the artifact and publish the draft in GitHub. This is a desktop app distributed through GitHub Releases; it is not a GitHub Pages website.

## Dependencies

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) downloads and extracts audio.
- [FFmpeg](https://ffmpeg.org/) converts audio.
- [Node.js](https://nodejs.org/) runs YouTube JavaScript challenges.
- [PyInstaller](https://pyinstaller.org/) packages the Windows application.

Third-party components retain their respective licenses. Choose a license for your own application before inviting reuse or contributions.
