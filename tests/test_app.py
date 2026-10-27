import queue
import unittest
from unittest.mock import patch
import audio_drop as app


class AppTests(unittest.TestCase):
    def test_custom_filename(self):
        self.assertEqual(app.filename_template('My song.mp3'), 'My song.%(ext)s')
        self.assertEqual(app.filename_template('100% music'), '100%% music.%(ext)s')
        self.assertIn('%(title)', app.filename_template(''))
        for name in ['../outside', 'C:\\outside', 'CON', 'bad?', 'trailing.']:
            with self.assertRaises(ValueError):
                app.filename_template(name)

    def test_url_boundaries(self):
        for url in ['https://youtu.be/abc', 'https://www.youtube.com/watch?v=abc',
                    'https://music.youtube.com/watch?v=abc']:
            self.assertTrue(app.validate_url(url))
        for url in ['file:///tmp/video', 'https://youtube.com.evil.test/watch?v=x',
                    'https://youtube.com@evil.test', 'not a URL']:
            self.assertFalse(app.validate_url(url))

    def test_worker_reports_failure(self):
        dummy = type('State', (), {'events': queue.Queue()})()
        with patch('yt_dlp.YoutubeDL', side_effect=RuntimeError('Connection failed')):
            app.AudioDrop.worker(dummy, 'https://youtu.be/abc', {})
        self.assertEqual(dummy.events.get(), ('line', 'Connection failed'))
        self.assertEqual(dummy.events.get(), ('done', 1))

    def test_worker_passes_url_and_reports_completion(self):
        dummy = type('State', (), {'events': queue.Queue()})()
        with patch('yt_dlp.YoutubeDL') as downloader:
            downloader.return_value.__enter__.return_value.download.return_value = 0
            app.AudioDrop.worker(dummy, 'https://youtu.be/abc', {})
            downloader.return_value.__enter__.return_value.download.assert_called_once_with(['https://youtu.be/abc'])
        self.assertEqual(dummy.events.get(), ('done', 0))


if __name__ == '__main__':
    unittest.main()
