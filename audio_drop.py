"""AudioDrop: a small YouTube audio downloader for Windows."""
import json
import os
from pathlib import Path
import queue
import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse
from youtube_search import SearchDialog

BASE = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
FORMATS = {'MP3': 'mp3', 'WAV': 'wav', 'FLAC': 'flac', 'M4A': 'm4a',
           'AAC': 'aac', 'OGG': 'vorbis', 'Opus': 'opus', 'ALAC': 'alac'}
CONFIG = Path(os.environ.get('LOCALAPPDATA', str(BASE))) / 'AudioDrop' / 'settings.json'


def validate_url(value):
    parsed = urlparse(value)
    host = (parsed.hostname or '').lower()
    return parsed.scheme in ('https', 'http') and (host == 'youtu.be' or
        host == 'youtube.com' or host.endswith('.youtube.com'))


def filename_template(name):
    name = name.strip()
    if not name:
        return '%(title).160B [%(id)s].%(ext)s'
    if (len(name) > 160 or any(c in '<>:"/\\|?*' or ord(c) < 32 for c in name)
            or name.endswith('.') or name.split('.')[0].upper() in
            {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)),
             *(f'LPT{i}' for i in range(1, 10))}):
        raise ValueError('Use a filename of up to 160 characters, without path separators or Windows reserved characters/names.')
    if Path(name).suffix.lower() in {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus', '.alac'}:
        name = str(Path(name).with_suffix(''))
    return name.replace('%', '%%') + '.%(ext)s'


def download_options(folder, fmt, name=''):
    options = {'noplaylist': True, 'windowsfilenames': True, 'overwrites': False,
        'socket_timeout': 30, 'retries': 3, 'format': 'bestaudio/best',
        'paths': {'home': str(folder)}, 'outtmpl': filename_template(name),
        'nocolor': True, 'postprocessors': [{'key': 'FFmpegExtractAudio',
            'preferredcodec': FORMATS[fmt], 'preferredquality': '0'}]}
    if shutil.which('node'):
        options['js_runtimes'] = {'node': {}}
    return options


class AudioDrop(tk.Tk):
    def __init__(self):
        super().__init__()
        icon = Path(__file__).resolve().parent / 'assets' / 'audiodrop.ico'
        if icon.exists():
            self.iconbitmap(str(icon))
        self.title('AudioDrop • YouTube to audio')
        self.geometry('720x660')
        self.minsize(640, 620)
        self.configure(bg='#101827')
        self.busy = False
        self.events = queue.Queue()
        self.protocol('WM_DELETE_WINDOW', self.close)
        settings = {}
        try:
            settings = json.loads(CONFIG.read_text(encoding='utf-8'))
            if not isinstance(settings, dict):
                settings = {}
        except (OSError, ValueError):
            pass
        self.url = tk.StringVar()
        self.filename = tk.StringVar()
        self.folder = tk.StringVar(value=settings.get('folder', str(Path.home() / 'Downloads' / 'AudioDrop')))
        self.fmt = tk.StringVar(value=settings.get('format', 'MP3'))
        if self.fmt.get() not in FORMATS:
            self.fmt.set('MP3')
        self.status = tk.StringVar(value='Ready when you are.')
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#101827')
        style.configure('TLabel', background='#101827', foreground='#dce6f5', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=9)
        style.configure('TEntry', padding=9)
        style.configure('TCombobox', padding=7)
        outer = ttk.Frame(self, padding=28)
        outer.pack(fill='both', expand=True)
        outer.columnconfigure(0, weight=1)
        ttk.Label(outer, text='AudioDrop', font=('Segoe UI', 27, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(outer, text='A link. A format. Your audio.', foreground='#8fa7c5').grid(row=1, column=0, sticky='w', pady=(2, 24))
        ttk.Label(outer, text='YOUTUBE URL').grid(row=2, column=0, sticky='w')
        url_row = ttk.Frame(outer)
        url_row.grid(row=3, column=0, sticky='ew', pady=(7, 17))
        url_row.columnconfigure(0, weight=1)
        self.url_entry = ttk.Entry(url_row, textvariable=self.url)
        self.url_entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        self.search_button = ttk.Button(url_row, text='Search YouTube', command=self.open_search)
        self.search_button.grid(row=0, column=1)
        options = ttk.Frame(outer)
        options.grid(row=4, column=0, sticky='ew')
        options.columnconfigure(1, weight=1)
        ttk.Label(options, text='FORMAT').grid(row=0, column=0, sticky='w')
        ttk.Label(options, text='SAVE TO').grid(row=0, column=1, sticky='w', padx=(16, 0))
        self.format_box = ttk.Combobox(options, textvariable=self.fmt, values=list(FORMATS), state='readonly', width=8)
        self.format_box.grid(row=1, column=0, pady=7)
        self.path_entry = ttk.Entry(options, textvariable=self.folder)
        self.path_entry.grid(row=1, column=1, sticky='ew', padx=(16, 8))
        self.browse_button = ttk.Button(options, text='Browse…', command=self.browse)
        self.browse_button.grid(row=1, column=2)
        ttk.Label(options, text='FILENAME (optional; leave blank to use the video title)').grid(row=2, column=0, columnspan=3, sticky='w', pady=(10, 4))
        self.name_entry = ttk.Entry(options, textvariable=self.filename)
        self.name_entry.grid(row=3, column=0, columnspan=3, sticky='ew')
        self.download = tk.Button(outer, text='↓  Download audio', command=self.start,
            bg='#47ddbb', fg='#09231e', activebackground='#74edcf', relief='flat',
            font=('Segoe UI', 12, 'bold'), cursor='hand2', pady=12)
        self.download.grid(row=5, column=0, sticky='ew', pady=(16, 14))
        self.progress = ttk.Progressbar(outer, mode='indeterminate')
        self.progress.grid(row=6, column=0, sticky='ew')
        ttk.Label(outer, textvariable=self.status, wraplength=620).grid(row=7, column=0, sticky='w', pady=10)
        self.log = tk.Text(outer, height=6, bg='#192538', fg='#b8cae2', relief='flat',
                           font=('Consolas', 9), wrap='word', state='disabled')
        self.log.grid(row=8, column=0, sticky='nsew')
        outer.rowconfigure(8, weight=1)
        ttk.Button(outer, text='Open download folder', command=self.open_folder).grid(row=9, column=0, sticky='e', pady=(12, 0))
        self.after(100, self.poll)
        self.url_entry.focus_set()

    def browse(self):
        initial = Path(self.folder.get()).expanduser()
        selected = filedialog.askdirectory(initialdir=str(initial if initial.is_dir() else BASE))
        if selected:
            self.folder.set(selected)

    def open_search(self):
        if not self.busy:
            SearchDialog(self, self.url.set)

    def open_folder(self):
        folder = Path(self.folder.get()).expanduser()
        if folder.is_dir():
            os.startfile(str(folder.resolve()))
        else:
            messagebox.showinfo('Folder', 'This folder will be created when you download.')

    def start(self):
        if self.busy:
            return
        url = self.url.get().strip()
        if not validate_url(url):
            messagebox.showerror('Check the link', 'Paste a full YouTube video URL, starting with https://.')
            return
        if not self.folder.get().strip():
            messagebox.showerror('Choose a folder', 'Choose where to save your audio.')
            return
        try:
            filename_template(self.filename.get())
        except ValueError as exc:
            messagebox.showerror('Check the filename', str(exc))
            return
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            messagebox.showerror('FFmpeg required', 'Install FFmpeg and add its bin folder to PATH, then restart AudioDrop.')
            return
        try:
            folder = Path(self.folder.get()).expanduser().resolve()
            folder.mkdir(parents=True, exist_ok=True)
            CONFIG.parent.mkdir(parents=True, exist_ok=True)
            CONFIG.write_text(json.dumps({'folder': str(folder), 'format': self.fmt.get()}), encoding='utf-8')
        except OSError as exc:
            messagebox.showerror('Cannot use folder', str(exc))
            return
        self.busy = True
        for widget in (self.download, self.url_entry, self.path_entry, self.browse_button, self.format_box, self.name_entry, self.search_button):
            widget.configure(state='disabled')
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')
        self.status.set('Connecting to YouTube…')
        self.progress.start(12)
        threading.Thread(target=self.worker, args=(url, download_options(folder, self.fmt.get(), self.filename.get())), daemon=True).start()

    def worker(self, url, options):
        try:
            from yt_dlp import YoutubeDL
            events = self.events
            class Logger:
                def debug(self, message):
                    if not message.startswith('[debug]'):
                        events.put(('line', message))
                def warning(self, message):
                    events.put(('line', 'Warning: ' + message))
                def error(self, message):
                    events.put(('line', 'Error: ' + message))
            options['logger'] = Logger()
            with YoutubeDL(options) as downloader:
                result = downloader.download([url])
            self.events.put(('done', result))
        except Exception as exc:
            self.events.put(('line', str(exc)))
            self.events.put(('done', 1))

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'line':
                    self.log.configure(state='normal')
                    self.log.insert('end', value + '\n')
                    self.log.see('end')
                    self.log.configure(state='disabled')
                    if value.startswith('[download]'):
                        self.status.set(value.replace('[download]', '').strip())
                    elif value.startswith('[ExtractAudio]'):
                        self.status.set('Converting audio…')
                else:
                    self.busy = False
                    self.progress.stop()
                    for widget in (self.download, self.url_entry, self.path_entry, self.browse_button, self.name_entry, self.search_button):
                        widget.configure(state='normal')
                    self.format_box.configure(state='readonly')
                    self.status.set('Saved! Open the download folder to find your audio.' if value == 0 else
                                    'Download failed. See the details below; you can retry.')
        except queue.Empty:
            pass
        self.after(100, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo('Download in progress', 'Please let the download finish before closing AudioDrop.')
        else:
            self.destroy()


if __name__ == '__main__':
    if os.name == 'nt':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AudioDrop.Desktop')
    AudioDrop().mainloop()
