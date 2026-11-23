import queue
import unittest
from unittest.mock import patch
from audio_drop import AudioDrop
from youtube_search import playlist_url, search_videos


class PlaylistTests(unittest.TestCase):
    def test_watch_link_normalizes_to_playlist(self):
        self.assertEqual(playlist_url('https://www.youtube.com/watch?v=abc&list=PL123'),
                         'https://www.youtube.com/playlist?list=PL123')
        self.assertIsNone(playlist_url('https://youtu.be/abc'))

    def test_playlist_search_keeps_playlist_results(self):
        with patch('yt_dlp.YoutubeDL') as factory:
            factory.return_value.__enter__.return_value.extract_info.return_value = {
                'entries': [{'id': 'PL123', 'title': 'Collection',
                             'url': 'https://www.youtube.com/playlist?list=PL123'}]}
            results = search_videos('collection', 'Playlists', 100)
            self.assertEqual(results[0]['duration'], 'Playlist')
            self.assertEqual(factory.call_args.args[0]['playlistend'], 100)

    def test_expansion_deduplicates_and_continues_after_failed_playlist(self):
        state = type('State', (), {'events': queue.Queue()})()
        video = {'title': 'Song', 'url': 'https://youtu.be/abcdefghijk'}
        playlists = [{'title': 'A', 'url': 'https://www.youtube.com/playlist?list=A'},
                     {'title': 'B', 'url': 'https://www.youtube.com/playlist?list=B'}, video]
        with patch('audio_drop.playlist_videos', side_effect=[[video], RuntimeError('Unavailable')]), patch.object(AudioDrop, 'worker', return_value=0) as worker:
            AudioDrop.batch_worker(state, playlists, {})
            worker.assert_called_once()
        self.assertEqual(list(state.events.queue)[-1], ('done', {'succeeded': 1, 'failed': ['B']}))
