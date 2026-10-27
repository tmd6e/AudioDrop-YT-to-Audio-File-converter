"""Find private bundled tools before considering a developer's PATH."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent


def tool_path(name):
    bundled = ROOT / 'vendor' / (name + '.exe')
    return str(bundled) if bundled.is_file() else shutil.which(name)


def runtime_options():
    options = {}
    ffmpeg = tool_path('ffmpeg')
    node = tool_path('node')
    if ffmpeg:
        options['ffmpeg_location'] = str(Path(ffmpeg).parent)
    if node:
        options['js_runtimes'] = {'node': {'path': node}}
    return options
