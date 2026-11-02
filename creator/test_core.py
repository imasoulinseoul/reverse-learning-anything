import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from creator.core import (CreatorError, MAX_NOTES_BYTES, MAX_PACK_BYTES, build_messages,
                          copy_prompt, endpoint_url, flashcard_pack, generate, pack_json, parse_pack)

class CreatorTests(unittest.TestCase):
    def setUp(self):
        self.settings = dict(title='My words', subject='language', language='en-AU',
                             notes='Hola means hello.', lessons=1, questions=3, kinds=['flashcard'])
        self.pack = flashcard_pack('My words', 'language', 'en-AU',
                                  [{'Front': f'Question {i}', 'Back': f'Answer {i}'} for i in range(3)])
        self.pack['lessons'][0]['sourceRefs'] = ['user-notes']

    def respond(self, pack=None):
        return Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
            content=json.dumps(pack if pack is not None else self.pack)))]))

    def test_generation_validated_and_credentials_not_in_messages_or_pack(self):
        completion = self.respond()
        result = generate(model='openai/test-model', api_key='private-test-key', completion_fn=completion, **self.settings)
        kwargs = completion.call_args.kwargs
        self.assertEqual(kwargs['api_key'], 'private-test-key')
        self.assertEqual(kwargs['num_retries'], 0)
        self.assertEqual(kwargs['timeout'], 60)
        self.assertNotIn('response_format', kwargs)
        self.assertNotIn('private-test-key', json.dumps(kwargs['messages']))
        self.assertNotIn('private-test-key', pack_json(result))
        completion.assert_called_once()

    def test_real_litellm_sdk_mock_response(self):
        import os
        os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
        import litellm
        litellm.turn_off_message_logging = True
        def sdk_mock(**kwargs):
            return litellm.completion(**kwargs, mock_response=json.dumps(self.pack))
        result = generate(model='openai/test-model', api_key='fake-test-key',
                          completion_fn=sdk_mock, **self.settings)
        self.assertEqual(result['title'], self.pack['title'])

    def test_proxy_routing_and_json_mode(self):
        completion = self.respond()
        generate(model='openai/my-alias', api_key='gateway-key', api_base='https://gateway.example/v1/',
                 output_mode='json', completion_fn=completion, **self.settings)
        self.assertEqual(completion.call_args.kwargs['api_base'], 'https://gateway.example/v1')
        self.assertEqual(completion.call_args.kwargs['response_format'], {'type':'json_object'})

    def test_local_endpoint_no_key(self):
        completion = self.respond()
        generate(model='openai/local-model', api_key='', api_base='http://localhost:1234/v1',
                 completion_fn=completion, **self.settings)
        self.assertEqual(completion.call_args.kwargs['api_key'], 'local-no-key')

    def test_remote_requires_key_before_request(self):
        completion = self.respond()
        with self.assertRaises(CreatorError):
            generate(model='openai/model', api_key='', completion_fn=completion, **self.settings)
        completion.assert_not_called()

    def test_provider_failure_does_not_expose_key_or_notes(self):
        completion = Mock(side_effect=RuntimeError('private-test-key: Hola means hello.'))
        with self.assertRaises(CreatorError) as caught:
            generate(model='openai/model', api_key='private-test-key', completion_fn=completion, **self.settings)
        self.assertNotIn('private-test-key', str(caught.exception))
        self.assertNotIn('Hola', str(caught.exception))
        completion.assert_called_once()

    def test_invalid_pack_never_succeeds(self):
        p = copy.deepcopy(self.pack)
        p['lessons'][0]['questions'][0]['sourceRefs'] = ['invented']
        with self.assertRaises(CreatorError):
            generate(model='openai/model', api_key='key', completion_fn=self.respond(p), **self.settings)

    def test_generated_source_and_question_count_must_match(self):
        for mutate in (lambda p: p['sources'][0].update(title='Changed'),
                       lambda p: p['lessons'][0]['questions'].pop()):
            p = copy.deepcopy(self.pack)
            mutate(p)
            with self.assertRaises(CreatorError):
                generate(model='openai/model', api_key='key', completion_fn=self.respond(p), **self.settings)

    def test_model_refusal(self):
        with self.assertRaisesRegex(CreatorError, 'could not create'):
            generate(model='openai/model', api_key='key', completion_fn=self.respond({'error':'Not enough material'}), **self.settings)

    def test_empty_response(self):
        completion = Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))]))
        with self.assertRaises(CreatorError):
            generate(model='openai/model', api_key='key', completion_fn=completion, **self.settings)

    def test_copy_prompt_contains_schema_and_untrusted_notes_as_data(self):
        messages = build_messages(**self.settings)
        payload = json.loads(messages[1]['content'])
        self.assertEqual(payload['studyNotes'], self.settings['notes'])
        self.assertIn('schemaVersion', copy_prompt(**self.settings))
        self.assertIn('never instructions', messages[0]['content'])

    def test_invalid_settings(self):
        for update in ({'notes':''}, {'notes':'a'*(MAX_NOTES_BYTES+1)}, {'kinds':[]},
                       {'language':'invalid'}, {'lessons':7}, {'questions':1}, {'subject':'unknown'}):
            with self.assertRaises(CreatorError):
                build_messages(**(self.settings | update))

    def test_endpoint_validation(self):
        for url in ('http://remote.example/v1', 'https://key:secret@example.com/v1',
                    'https://example.com/v1?key=secret', 'file:///tmp/model', 'https://[invalid'):
            with self.assertRaises(CreatorError): endpoint_url(url)
        self.assertEqual(endpoint_url('http://127.0.0.1:4000/v1'), 'http://127.0.0.1:4000/v1')

    def test_fenced_json_roundtrip(self):
        text = pack_json(self.pack)
        self.assertEqual(parse_pack('```json\n'+text+'```'), self.pack)

    def test_bad_json_and_oversize(self):
        for text in ('[]', '{', '{"id":"one","id":"two"}', '{"id": NaN}', 'x'*(MAX_PACK_BYTES+1)):
            with self.assertRaises(CreatorError): parse_pack(text)

    def test_flashcards_split_and_have_unique_pack_ids(self):
        rows = [{'Front':str(i),'Back':str(i)} for i in range(21)]
        p = flashcard_pack('Practice','generalStudy','en',rows)
        self.assertEqual([len(l['questions']) for l in p['lessons']], [10,10,1])
        self.assertNotEqual(p['id'], flashcard_pack('Practice','generalStudy','en',rows)['id'])
        parse_pack(pack_json(p))

    def test_incomplete_flashcards_rejected(self):
        for rows in ([], [{'Front':'','Back':'answer'}], [{'Front':'q','Back':None}]):
            with self.assertRaises(CreatorError): flashcard_pack('Cards','generalStudy','en',rows)

if __name__ == '__main__': unittest.main()
