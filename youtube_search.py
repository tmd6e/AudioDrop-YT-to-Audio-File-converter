"""Search YouTube metadata without downloading media."""
import queue
import re
import threading
import tkinter as tk
from tkinter import ttk
from runtime_paths import runtime_options


def search_videos(query):
    from yt_dlp import YoutubeDL
    query = query.strip()
    if not query:
        return []
    with YoutubeDL({**runtime_options(), 'quiet': True, 'no_warnings': True, 'extract_flat': True,
                    'skip_download': True, 'socket_timeout': 20, 'retries': 1,
                    'extractor_retries': 1}) as downloader:
        data = downloader.extract_info('ytsearch10:' + query, download=False)
    results = []
    for entry in (data or {}).get('entries', []) or []:
        if not entry or not re.fullmatch(r'[A-Za-z0-9_-]{11}', str(entry.get('id', ''))):
            continue
        duration = entry.get('duration')
        duration = int(duration) if isinstance(duration, (int, float)) and duration >= 0 else None
        results.append({'title': entry.get('title') or 'Untitled video',
                        'channel': entry.get('channel') or entry.get('uploader') or 'Unknown channel',
                        'duration': f'{duration // 60}:{duration % 60:02}' if duration is not None else '—',
                        'url': 'https://www.youtube.com/watch?v=' + entry['id']})
    return results


class SearchDialog(tk.Toplevel):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.title('Search YouTube')
        self.geometry('760x440')
        self.minsize(560, 340)
        self.transient(parent)
        self.grab_set()
        self.on_select = on_select
        self.events = queue.Queue()
        self.results = []
        self.searching = False
        self.query = tk.StringVar()
        self.status = tk.StringVar(value='Search by video title, artist, or keywords.')
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        self.entry = ttk.Entry(frame, textvariable=self.query)
        self.entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        self.entry.bind('<Return>', lambda event: self.start_search())
        self.search_button = ttk.Button(frame, text='Search', command=self.start_search)
        self.search_button.grid(row=0, column=1)
        ttk.Label(frame, textvariable=self.status, wraplength=680).grid(row=1, column=0, columnspan=2, sticky='w', pady=12)
        self.table = ttk.Treeview(frame, columns=('title', 'channel', 'duration'), show='headings', selectmode='browse')
        for key, label, width in [('title', 'Video', 360), ('channel', 'Channel', 180), ('duration', 'Length', 65)]:
            self.table.heading(key, text=label)
            self.table.column(key, width=width, minwidth=50, stretch=key != 'duration')
        self.table.grid(row=2, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.table.yview)
        scrollbar.grid(row=2, column=1, sticky='nsw')
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.bind('<<TreeviewSelect>>', self.selection_changed)
        self.table.bind('<Double-1>', lambda event: self.use_selected())
        self.table.bind('<Return>', lambda event: self.use_selected())
        self.use_button = ttk.Button(frame, text='Use selected video', command=self.use_selected, state='disabled')
        self.use_button.grid(row=3, column=0, columnspan=2, sticky='e', pady=(14, 0))
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.bind('<Escape>', lambda event: self.close())
        self.timer = self.after(100, self.poll)
        self.entry.focus_set()

    def selection_changed(self, event=None):
        self.use_button.configure(state='normal' if self.table.selection() and not self.searching else 'disabled')

    def start_search(self):
        query = self.query.get().strip()
        if self.searching:
            return
        if not query:
            self.status.set('Enter a title, artist, or keywords first.')
            return
        self.searching = True
        self.results = []
        for item in self.table.get_children():
            self.table.delete(item)
        self.search_button.configure(state='disabled')
        self.use_button.configure(state='disabled')
        self.status.set('Searching YouTube…')
        threading.Thread(target=self.worker, args=(query,), daemon=True).start()

    def worker(self, query):
        try:
            self.events.put(('results', search_videos(query)))
        except Exception as exc:
            self.events.put(('error', str(exc)))

    def poll(self):
        try:
            kind, value = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            self.searching = False
            self.search_button.configure(state='normal')
            if kind == 'error':
                self.status.set('Search failed. Check your connection and try again. ' + value[:180])
            else:
                self.results = value
                for index, video in enumerate(value):
                    self.table.insert('', 'end', iid=str(index), values=(video['title'], video['channel'], video['duration']))
                self.status.set(f'{len(value)} results. Select a video to fill its URL.' if value else 'No videos found. Try different keywords.')
        self.timer = self.after(100, self.poll)

    def use_selected(self):
        selected = self.table.selection()
        if self.searching or not selected:
            return
        self.on_select(self.results[int(selected[0])]['url'])
        self.close()

    def close(self):
        self.after_cancel(self.timer)
        self.destroy()
