# AudioDrop

**Find a YouTube video and save its audio to your computer.**

AudioDrop is a free Windows app with built-in video search, audio format choices, and a folder picker. Everything it needs is included. You do **not** need to install Python, FFmpeg, or Node.js.

## Get AudioDrop

**[Open the latest download page](https://github.com/tmd6e/AudioDrop-YT-to-Audio-File-converter/releases/latest)**

For 64-bit Windows 10 and Windows 11. An internet connection is needed to search and download videos.

### Recommended: use the installer

1. On the download page, open **Assets** if the download list is collapsed.
2. Download the file starting with **AudioDrop-Setup** and ending in **.exe**.
3. Open that file and follow the setup steps. The default options are fine.
4. Open **AudioDrop** from your desktop or the Windows Start menu.

Setup installs the app for your Windows account without administrator permission. It creates a Start menu entry and offers a desktop shortcut. You do not need any of the **Source code** downloads.

### Alternative: run without installing

1. Download **AudioDrop-Windows.zip** from the same page.
2. Right-click the ZIP and choose **Extract All**.
3. Open the extracted **AudioDrop** folder, then open **AudioDrop.exe**.

Keep all files in that folder together, including `_internal`. Do not run from inside the ZIP or move only the EXE out of the folder. For optional Desktop and Start menu shortcuts, double-click **Create shortcuts.bat** in the extracted folder.

## Save your first audio file

1. **Choose a video.** Paste a YouTube link into the URL box, or click **Search YouTube**, enter a title or artist, choose a result, and click **Use selected video**.
2. **Choose a format.** Pick **MP3** if you are unsure; it works with most music players.
3. **Choose a folder.** Click **Browse…** to pick where to save the file. The default is the **AudioDrop** folder inside your Windows **Downloads** folder.
4. **Name it if you want.** Enter a filename, or leave it blank to use the video's title. The app adds the file extension.
5. Click **Download audio** and wait for the saved message. Click **Open download folder** to find your file.

The app remembers your folder and format. Selecting a search result fills the URL; it does not download until you click the download button. Playlist links download one video.

## Keep it handy

- **Taskbar:** open AudioDrop, right-click its taskbar icon, and choose **Pin to taskbar**.
- **Start menu:** find AudioDrop in Start, right-click it, and choose **Pin to Start**.
- **Desktop:** keep the desktop shortcut option selected during setup.

## Which format should I choose?

| Format | Good for |
| --- | --- |
| MP3 | Everyday listening and most players |
| M4A or AAC | Players and devices that support AAC audio |
| Opus or OGG | Players that support these formats |
| WAV | Audio editing; files can be large |
| FLAC or ALAC | Lossless storage of the converted audio |

WAV, FLAC, and ALAC cannot improve the quality of the original YouTube audio.

## Updating or removing AudioDrop

**Installed version:** download the newer setup file and run it. To uninstall, open Windows **Settings → Apps → Installed apps**, find **AudioDrop**, and choose **Uninstall**. Your downloaded audio is kept.

**Portable version:** extract a newer ZIP to a new folder and open it there. Recreate shortcuts if you change its location. To remove it, delete the extracted app folder. Your downloaded audio is kept.

## If something goes wrong

- **“App files missing”:** reinstall, or extract the entire portable ZIP again. Keep `_internal` beside `AudioDrop.exe`.
- **Search or download fails:** check your connection and try again. Some private, age-restricted, deleted, or region-blocked videos are unavailable. The message area shows details.
- **A filename already exists:** choose another name to keep a separate copy. Existing audio is not overwritten.
- **Downloads stopped working:** check the release page for a newer version; YouTube changes sometimes require app updates.
- **Windows shows a publisher warning:** AudioDrop is currently unsigned. Verify that the file came from this repository's Releases page. Do not disable Windows security protection.

Still stuck? [Report a problem](https://github.com/tmd6e/AudioDrop-YT-to-Audio-File-converter/issues) and include the message shown in the app.

## For developers

See [DEVELOPING.md](DEVELOPING.md) for source setup, tests, builds, and release steps. The app uses the repository's GPL v2 license. Bundled components retain their own licenses; see [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt).
