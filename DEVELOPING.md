# Developing AudioDrop

Use Windows x64, Python 3.12, and Inno Setup 6. Create a virtual environment, activate it, and run:

```powershell
python -m pip install -r requirements-build.txt
python bundle_tools.py
python audio_drop.py
python -m unittest discover -s tests -v
./build.ps1
```

`bundle_tools.py` downloads fixed FFmpeg and Node.js archives, checks their SHA-256 digests, and extracts the executables and notices into the ignored `vendor/` folder. No system PATH edits are made. Source execution can fall back to PATH when bundled tools are absent.

`build.ps1` builds a folder distribution, checks the packaged Node.js, FFmpeg and ffprobe with an empty PATH, converts a generated sample into all eight supported audio formats, and produces a portable ZIP and installer. Set `AUDIODROP_ISCC` to a custom Inno Setup compiler path, or pass `-SkipInstaller` for a ZIP-only development build.

Outputs: `dist/AudioDrop-Setup-1.1.0.exe` and `dist/AudioDrop-Windows.zip`. The EXE inside the app folder requires its adjacent `_internal` directory. Do not publish that EXE alone.

The Windows GitHub workflow builds, tests, and uploads both distributable files. Version tags (`v*`) create draft releases. Review the installer and portable artifact before publishing a draft. Update `installer.iss` and release notes when changing versions. Runtime updates require updating the URLs and SHA-256 digests in `bundle_tools.py`, rebuilding, and rerunning checks.

The original icon is in `assets/`; install Pillow and run `python make_icon.py` to regenerate it. Preferences are stored in `%LOCALAPPDATA%/AudioDrop/settings.json`. Downloads remain separate from installation files.
