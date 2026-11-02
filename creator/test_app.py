import json
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

class CreatorUITests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT/'creator/app.py'), default_timeout=30).run()
        self.assertEqual(len(self.app.exception), 0)

    def button(self, label):
        return next(b for b in self.app.button if b.label == label)

    def test_manual_flashcard_flow(self):
        with patch('creator.core.generate', side_effect=AssertionError('No AI call expected')):
            self.button('Create my flashcard pack').click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertTrue(self.app.success)
        pack = self.app.session_state['flashcard_pack']
        self.assertEqual(len(pack['lessons'][0]['questions']), 2)
        self.assertEqual(len(self.app.get('download_button')), 1)

    def test_copy_prompt_requires_notes_and_then_works(self):
        self.button('Prepare my copy-and-paste prompt').click().run()
        self.assertTrue(self.app.error)
        self.app.text_input(key='course_title').set_value('GitHub')
        self.app.text_area(key='notes').set_value('Repositories contain project files and revision history.')
        self.button('Prepare my copy-and-paste prompt').click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertIn('studyNotes', self.app.session_state['copy_prompt'])

    def test_invalid_json_has_no_download(self):
        self.app.text_area(key='pack_json').set_value('{"not":"a pack"}')
        self.button('Validate and prepare download').click().run()
        self.assertTrue(self.app.error)
        self.assertEqual(len(self.app.get('download_button')), 0)

    def test_valid_pack_download(self):
        text = (ROOT/'examples/github-basics.learning.json').read_text()
        self.app.text_area(key='pack_json').set_value(text)
        self.button('Validate and prepare download').click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.app.session_state['checked_pack']['title'], 'GitHub Basics')
        self.assertEqual(len(self.app.get('download_button')), 1)

    def test_clear_key(self):
        self.app.text_input(key='provider_key').set_value('private-test-key').run()
        self.button('Clear API key').click().run()
        self.assertEqual(self.app.text_input(key='provider_key').value, '')

if __name__ == '__main__': unittest.main()
