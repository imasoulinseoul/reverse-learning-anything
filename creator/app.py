"""Run from the repo root: python -m streamlit run creator/app.py"""
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import streamlit as st
from creator.core import (CreatorError, KINDS, SUBJECTS, MAX_NOTES_BYTES, MAX_PACK_BYTES,
                          copy_prompt, flashcard_pack, generate, pack_json, parse_pack)

st.set_page_config(page_title='Create a learning pack · Reverse Learning Anything', page_icon='📖', layout='centered')
st.title('Create your next little lesson')
st.write('Turn your material into a learning pack for Reverse Learning Anything.')
st.caption('Runs on your computer. AI generation sends your notes to the provider or gateway you choose. Other paths work without an API key.')


def read_text(upload, limit):
    data = upload.getvalue()
    if len(data) > limit:
        raise CreatorError('This file is too large. Choose a smaller excerpt or pack.')
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise CreatorError('Use a UTF-8 text file. PDF and Word extraction are not supported yet.') from None


def preview(pack, key):
    # Downloads are built only after schema and semantic validation.
    try:
        data = pack_json(pack)
    except CreatorError as error:
        st.error(str(error))
        return
    st.success('Format checks passed. Review the content before learning or sharing it.')
    st.subheader(pack['title'])
    st.text(pack['description'])
    st.caption(f"{len(pack['lessons'])} lessons · {sum(len(l['questions']) for l in pack['lessons'])} questions · {pack['language']}")
    for lesson in pack['lessons']:
        with st.expander(f"{lesson['order']}. {lesson['title']}"):
            st.text(lesson['concept'])
            for question in lesson['questions']:
                st.text(f"{KINDS[question['type']]}: {question['prompt']}")
                if 'code' in question:
                    st.code(question['code'], language='text')
                for choice in question.get('choices', question.get('items', [])):
                    st.text('• ' + choice['text'])
                for pair in question.get('pairs', []):
                    st.text(pair['left'] + ' → ' + pair['right'])
                labels = {item['id']: item['text'] for item in question.get('choices', question.get('items', []))}
                if 'correctChoiceId' in question:
                    answer = labels[question['correctChoiceId']]
                elif 'correctChoiceIds' in question:
                    answer = ', '.join(labels[id] for id in question['correctChoiceIds'])
                elif 'correctOrder' in question:
                    answer = ' → '.join(labels[id] for id in question['correctOrder'])
                elif 'correctAnswer' in question:
                    answer = 'True' if question['correctAnswer'] else 'False'
                else:
                    answer = question.get('answer', ', '.join(question.get('acceptedAnswers', ['See pairs above'])))
                st.text('Answer: ' + answer)
                st.text(question['explanation'])
    st.download_button('Download valid learning pack', data, file_name=pack['id']+'.learning.json', mime='application/json', key=key)
    st.caption('This is an app-format file. The iPhone PoC currently requires bundling it in Xcode; Files import is planned. See the creator guide for the exact steps.')


ai, manual, check = st.tabs(['Create with AI / copy prompt', 'Make flashcards — no AI', 'Check or edit JSON'])
with ai:
    st.subheader('1. Bring your study material')
    title = st.text_input('Course title', placeholder='For example: GitHub Basics', key='course_title')
    subject_name = st.selectbox('Subject', list(SUBJECTS), index=1, key='course_subject')
    language = st.text_input('Lesson language', value='en-AU', help='Instruction language tag: en, en-AU, es, fr…', key='course_language')
    notes = st.text_area('Paste your notes', height=180, placeholder='Paste a chapter, notes, or a short explanation. The AI will use only this material.', key='notes')
    upload = st.file_uploader('Or upload notes (replaces pasted notes)', type=['txt', 'md'], key='notes_file')
    lesson_count = st.slider('Number of bite-size lessons', 1, 6, 2)
    question_count = st.slider('Questions per lesson', 3, 5, 4)
    types = st.multiselect('Exercise types', list(KINDS), default=['multipleChoice','trueFalse','shortAnswer','flashcard'], format_func=lambda key: KINDS[key])
    settings = dict(title=title, subject=SUBJECTS[subject_name], language=language,
                    notes=notes, lessons=lesson_count, questions=question_count, kinds=types)
    try:
        if upload is not None:
            settings['notes'] = read_text(upload, MAX_NOTES_BYTES)
    except CreatorError as error:
        settings['notes'] = ''
        st.error(str(error))

    with st.expander('Use a chat app you already have — no API key'):
        st.write('Prepare a prompt, copy it into your preferred chat app, then paste its JSON into Check or edit JSON. This button makes no AI request.')
        if st.button('Prepare my copy-and-paste prompt'):
            try:
                st.session_state['copy_prompt'] = copy_prompt(**settings)
            except CreatorError as error:
                st.error(str(error))
        if 'copy_prompt' in st.session_state:
            st.caption('This prompt includes the notes and settings from when you clicked Prepare. Prepare again after edits.')
            st.code(st.session_state['copy_prompt'], language='text')
            st.download_button('Download prompt', st.session_state['copy_prompt'], file_name='learning-pack-prompt.txt', mime='text/plain')

    st.subheader('2. Connect your AI')
    connection = st.selectbox('Connection', ['Provider through LiteLLM', 'LiteLLM proxy / OpenAI-compatible endpoint', 'Local OpenAI-compatible server'])
    st.caption('Use the exact provider-prefixed model ID for your account. Model availability and output-mode support vary.')
    model = st.text_input('LiteLLM model ID', placeholder='provider/model-name', help='Direct: provider/model-name. Proxy or compatible server: openai/your-model-alias.')
    api_base = ''
    if connection != 'Provider through LiteLLM':
        api_base = st.text_input('API base URL', placeholder='https://your-gateway.example/v1' if connection.startswith('LiteLLM') else 'http://localhost:1234/v1')
        st.caption('Enter the base URL, not /chat/completions. For a gateway, use its model alias with the openai/ prefix.')
    api_key = st.text_input('API key', type='password', key='provider_key', help='Use your provider key or your LiteLLM gateway key. A key is optional only for a local endpoint.')
    def clear_key():
        st.session_state['provider_key'] = ''
    st.button('Clear API key', on_click=clear_key)
    mode = st.selectbox('Output mode', ['Prompt only (widest compatibility)', 'JSON object (provider must support it)'])
    st.caption('Your key stays in this local session. It is not included in prompts, downloads, Git, or saved configuration. Closing the process clears session memory.')
    st.subheader('3. Generate and review')
    st.write('When you click Generate, the creator sends the notes shown in step 1, course settings, and the learning-pack schema to your selected provider. Provider usage fees may apply. It makes one request with no automatic retry.')
    if api_base:
        st.text('Destination: ' + api_base)
    elif model:
        st.text('Provider routing: ' + model.split('/')[0])
    if st.button('Generate learning pack', type='primary'):
        st.session_state.pop('generated_pack', None)
        try:
            if connection != 'Provider through LiteLLM' and not api_base.strip():
                raise CreatorError('Enter the API base URL for this connection.')
            with st.spinner('Creating your lessons…'):
                st.session_state['generated_pack'] = generate(model=model, api_key=api_key, api_base=api_base,
                    output_mode='json' if mode.startswith('JSON') else 'prompt', **settings)
        except CreatorError as error:
            st.error(str(error))
    if 'generated_pack' in st.session_state:
        st.caption('Last successful generation. Generate again to apply changed notes or settings.')
        preview(st.session_state['generated_pack'], 'ai_download')

with manual:
    st.subheader('Write questions. Add answers. Download.')
    st.write('An easy offline route for vocabulary, definitions, or exam revision. Flashcards reveal the answer and ask the learner to self-assess.')
    card_title = st.text_input('Flashcard course title', value='My recall practice')
    card_subject = st.selectbox('Flashcard subject', list(SUBJECTS), index=2)
    card_language = st.text_input('Flashcard lesson language', value='en-AU')
    csv_file = st.file_uploader('Optional: start from CSV with Front,Back columns', type=['csv'])
    rows = [{'Front':'What is a GitHub pull request?', 'Back':'A proposal to merge changes from one branch into another.'},
            {'Front':'What does a README do?', 'Back':'Introduces a project and how to use it.'}]
    try:
        if csv_file is not None:
            rows = list(csv.DictReader(io.StringIO(read_text(csv_file, MAX_NOTES_BYTES))))
            if not rows or set(rows[0]) != {'Front','Back'}:
                raise CreatorError('Use a CSV with exactly Front,Back headers and at least one card.')
        edited = st.data_editor(rows, num_rows='dynamic', key='flashcard_rows')
        st.caption('Edit, add, or remove rows. Keep 1–100 complete cards; long sets are split into lessons of up to 10 cards.')
        if st.button('Create my flashcard pack'):
            st.session_state.pop('flashcard_pack', None)
            st.session_state['flashcard_pack'] = flashcard_pack(card_title, SUBJECTS[card_subject], card_language, edited)
    except CreatorError as error:
        st.error(str(error))
    if 'flashcard_pack' in st.session_state:
        st.caption('Last created flashcard pack. Click Create again after editing the table.')
        preview(st.session_state['flashcard_pack'], 'card_download')

with check:
    st.subheader('Check an existing pack or AI reply')
    st.write('Paste JSON, or upload a pack. You can also edit any example from the repo. Nothing is sent to an AI provider.')
    raw = st.text_area('Learning-pack JSON', height=250, key='pack_json')
    json_file = st.file_uploader('Or upload a learning pack (replaces pasted JSON)', type=['json'])
    if st.button('Validate and prepare download'):
        st.session_state.pop('checked_pack', None)
        try:
            if json_file is not None:
                raw = read_text(json_file, MAX_PACK_BYTES)
            st.session_state['checked_pack'] = parse_pack(raw)
        except CreatorError as error:
            st.error(str(error))
    if 'checked_pack' in st.session_state:
        st.caption('Last validated input. Validate again after making changes.')
        preview(st.session_state['checked_pack'], 'check_download')
