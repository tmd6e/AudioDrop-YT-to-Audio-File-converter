import queue
import unittest
from unittest.mock import patch
from youtube_search import search_videos, SearchDialog


class SearchTests(unittest.TestCase):
    def test_search_normalizes_results_and_never_downloads(self):
        with patch('yt_dlp.YoutubeDL') as cls:
            downloader = cls.return_value.__enter__.return_value
            downloader.extract_info.return_value = {'entries': [None,
                {'id': 'abcdefghijk', 'title': 'A song', 'channel': 'Artist', 'duration': 125},
                {'id': 'invalid'}, {'id': '12345678901'}]}
            results = search_videos('  some music  ')
            downloader.extract_info.assert_called_once_with('ytsearch10:some music', download=False)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], 'https://www.youtube.com/watch?v=abcdefghijk')
        self.assertEqual(results[0]['duration'], '2:05')
        self.assertEqual(results[1]['channel'], 'Unknown channel')

    def test_empty_query_does_not_connect(self):
        with patch('yt_dlp.YoutubeDL') as cls:
            self.assertEqual(search_videos('  '), [])
            cls.assert_not_called()

    def test_no_results(self):
        with patch('yt_dlp.YoutubeDL') as cls:
            cls.return_value.__enter__.return_value.extract_info.return_value = None
            self.assertEqual(search_videos('nothing'), [])

    def test_failure_returns_to_ui_queue(self):
        state = type('State', (), {'events': queue.Queue()})()
        with patch('youtube_search.search_videos', side_effect=RuntimeError('Offline')):
            SearchDialog.worker(state, 'query')
        self.assertEqual(state.events.get(), ('error', 'Offline'))
