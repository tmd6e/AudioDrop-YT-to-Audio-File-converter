from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import runtime_paths


class RuntimeTests(unittest.TestCase):
    def test_bundled_tools_win_over_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'vendor').mkdir()
            for name in ('node', 'ffmpeg', 'ffprobe'):
                (root / 'vendor' / (name + '.exe')).touch()
            with patch.object(runtime_paths, 'ROOT', root), patch('shutil.which', return_value='wrong'):
                options = runtime_paths.runtime_options()
                self.assertEqual(options['ffmpeg_location'], str(root / 'vendor'))
                self.assertEqual(options['js_runtimes']['node']['path'], str(root / 'vendor/node.exe'))

    def test_missing_tools_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(runtime_paths, 'ROOT', Path(directory)), patch('shutil.which', return_value=None):
                self.assertIsNone(runtime_paths.tool_path('node'))
                self.assertEqual(runtime_paths.runtime_options(), {})
