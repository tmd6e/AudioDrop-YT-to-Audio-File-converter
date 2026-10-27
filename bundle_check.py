"""Smoke-test the packaged application with no external runtime on PATH."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from runtime_paths import tool_path, runtime_options


def check(output):
    os.environ['PATH'] = ''
    report = {}
    for name in ('node', 'ffmpeg', 'ffprobe'):
        executable = tool_path(name)
        if not executable:
            raise RuntimeError('Missing bundled ' + name)
        result = subprocess.run([executable, '--version' if name == 'node' else '-version'],
            check=True, capture_output=True, text=True, creationflags=0x08000000)
        report[name] = result.stdout.splitlines()[0]
    from yt_dlp import YoutubeDL
    from yt_dlp.postprocessor.ffmpeg import FFmpegExtractAudioPP
    with tempfile.TemporaryDirectory() as temp:
        with YoutubeDL({**runtime_options(), 'quiet': True}) as downloader:
            for codec in ('mp3', 'wav', 'flac', 'm4a', 'aac', 'vorbis', 'opus', 'alac'):
                path = Path(temp) / (codec + '.wav')
                subprocess.run([tool_path('ffmpeg'), '-v', 'error', '-f', 'lavfi', '-i',
                    'sine=frequency=440:duration=0.2', str(path)], check=True, capture_output=True, creationflags=0x08000000)
                _, info = FFmpegExtractAudioPP(downloader, preferredcodec=codec, preferredquality='0').run(
                    {'filepath': str(path), 'ext': 'wav', 'vcodec': 'none', 'acodec': 'pcm_s16le'})
                assert Path(info['filepath']).is_file()
    report['formats_tested'] = 8
    report['path'] = os.environ['PATH']
    Path(output).write_text(json.dumps(report, indent=2), encoding='utf-8')
