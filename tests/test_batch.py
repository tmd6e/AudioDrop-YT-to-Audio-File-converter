import queue
import unittest
from unittest.mock import patch
from pathlib import Path
from audio_drop import AudioDrop, download_options
from youtube_search import SearchDialog


def video(index):
    return {'url': f'https://www.youtube.com/watch?v=abcdefghij{index}',
            'title': f'Video {index}', 'channel': 'Channel', 'duration': '1:00'}


class BatchTests(unittest.TestCase):
    def test_batch_continues_after_error_and_reports_one_summary(self):
        state = type('State', (), {'events': queue.Queue()})()
        with patch('yt_dlp.YoutubeDL') as factory:
            download = factory.return_value.__enter__.return_value.download
            download.side_effect = [0, RuntimeError('Unavailable video'), 0]
            options = download_options(Path('chosen folder'), 'MP3')
            AudioDrop.batch_worker(state, [video(1), video(2), video(3)], options)
            self.assertEqual(download.call_count, 3)
            self.assertEqual([call.args[0] for call in download.call_args_list],
                             [[video(i)['url']] for i in (1, 2, 3)])
            for call in factory.call_args_list:
                self.assertEqual(call.args[0]['paths']['home'], 'chosen folder')
                self.assertIn('%(id)s', call.args[0]['outtmpl'])
        events = list(state.events.queue)
        self.assertEqual([value for kind, value in events if kind == 'done'],
                         [{'succeeded': 2, 'failed': ['Video 2']}])
        self.assertEqual(len([kind for kind, value in events if kind == 'item']), 3)


class BatchUITests(unittest.TestCase):
    def setUp(self):
        self.app = AudioDrop()
        self.app.withdraw()

    def tearDown(self):
        for timer in self.app.tk.call('after', 'info'):
            self.app.after_cancel(timer)
        self.app.destroy()

    def test_multi_selection_reaches_queue_and_duplicates_are_ignored(self):
        dialog = SearchDialog(self.app, self.app.add_videos)
        dialog.results = [video(1), video(2), video(3)]
        for index, item in enumerate(dialog.results):
            dialog.table.insert('', 'end', iid=str(index), values=(item['title'], '', ''))
        dialog.table.selection_set('0', '2')
        dialog.use_selected()
        self.assertEqual(self.app.videos, [video(1), video(3)])
        self.app.add_videos([video(3), video(2)])
        self.assertEqual(self.app.videos, [video(1), video(3), video(2)])
        self.assertEqual(str(self.app.name_entry['state']), 'disabled')
        self.app.queue_table.selection_set('1', '2')
        self.app.remove_selected()
        self.assertEqual(self.app.videos, [video(1)])
        self.assertEqual(str(self.app.name_entry['state']), 'normal')
        self.app.clear_queue()
        self.assertEqual(self.app.videos, [])
        self.assertEqual(str(self.app.url_entry['state']), 'normal')

    def test_batch_start_snapshots_selected_folder_and_ignores_custom_name(self):
        import tempfile
        self.app.add_videos([video(1), video(2)])
        self.app.filename.set('single filename')
        with tempfile.TemporaryDirectory() as folder:
            self.app.folder.set(folder)
            with patch('audio_drop.CONFIG', Path(folder) / 'settings.json'), patch('audio_drop.tool_path', return_value='tool'), patch('audio_drop.threading.Thread') as thread:
                self.app.start()
                videos, options = thread.call_args.kwargs['args']
                self.assertEqual(videos, [video(1), video(2)])
                self.assertEqual(options['paths']['home'], str(Path(folder).resolve()))
                self.assertIn('%(title)', options['outtmpl'])
                self.assertNotIn('single filename', options['outtmpl'])
                thread.return_value.start.assert_called_once()
        self.app.events.put(('done', {'succeeded': 1, 'failed': ['Video 2']}))
        self.app.poll()
        self.assertFalse(self.app.busy)
        self.assertIn('1 completed, 1 failed', self.app.status.get())
        self.assertEqual(str(self.app.search_button['state']), 'normal')
