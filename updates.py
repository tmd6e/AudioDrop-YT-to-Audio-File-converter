import json
import urllib.request
import webbrowser

VERSION = '1.4.0'
LATEST = 'https://api.github.com/repos/tmd6e/AudioDrop-YT-to-Audio-File-converter/releases/latest'

def latest_update():
    request = urllib.request.Request(LATEST, headers={'User-Agent': 'AudioDrop', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=20) as response:
        release = json.load(response)
    version = release['tag_name'].lstrip('v')
    current = tuple(int(n) for n in VERSION.split('.'))
    available = tuple(int(n) for n in version.split('.'))
    return version, available > current

def open_download():
    webbrowser.open('https://github.com/tmd6e/AudioDrop-YT-to-Audio-File-converter/releases/latest')
