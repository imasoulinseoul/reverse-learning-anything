import copy
import json
import unittest
from pathlib import Path
from validate_pack import validate, ROOT

class PackValidationTests(unittest.TestCase):
    def setUp(self):
        self.pack = json.loads((ROOT / 'examples/python-foundations.learning.json').read_text())

    def reject(self, mutate):
        p = copy.deepcopy(self.pack)
        mutate(p)
        with self.assertRaises(Exception):
            validate(p)

    def test_examples_cover_every_type(self):
        types = set()
        for path in (ROOT / 'examples').glob('*.learning.json'):
            p = json.loads(path.read_text())
            validate(p)
            types.update(q['type'] for l in p['lessons'] for q in l['questions'])
        self.assertEqual(types, {'multipleChoice', 'multipleSelect', 'trueFalse', 'shortAnswer',
                                'fillBlank', 'ordering', 'matching', 'flashcard', 'codeCompletion'})

    def test_v1_compatibility(self):
        p = json.loads((ROOT / 'examples/machine-learning.learning.json').read_text())
        p['schemaVersion'] = '1.0.0'
        del p['subject']
        validate(p)

    def test_bad_choice_reference(self):
        self.reject(lambda p: p['lessons'][0]['questions'][0].update(correctChoiceId='missing'))

    def test_bad_multiple_select_reference(self):
        self.reject(lambda p: p['lessons'][0]['questions'][1].update(correctChoiceIds=['missing']))

    def test_duplicate_id(self):
        self.reject(lambda p: p['lessons'][0].update(id=p['id']))

    def test_wrong_variant_fields(self):
        self.reject(lambda p: p['lessons'][0]['questions'][2].update(acceptedAnswers=['True']))

    def test_bad_code_blank(self):
        self.reject(lambda p: p['lessons'][0]['questions'][3].update(code='len(items)'))

    def test_unknown_source(self):
        self.reject(lambda p: p['lessons'][0].update(sourceRefs=['missing']))

    def test_order_omission_and_ambiguous_match(self):
        p = json.loads((ROOT / 'examples/spanish-basics.learning.json').read_text())
        p['lessons'][0]['questions'][3]['correctOrder'].pop()
        with self.assertRaises(ValueError): validate(p)
        p = json.loads((ROOT / 'examples/spanish-basics.learning.json').read_text())
        p['lessons'][0]['questions'][2]['pairs'][1]['right'] = 'Hello'
        with self.assertRaises(ValueError): validate(p)

if __name__ == '__main__':
    unittest.main()
