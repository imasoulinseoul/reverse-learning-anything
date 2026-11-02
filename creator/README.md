# Create your own learning materials

You do not need to write JSON by hand. This local creator turns notes into validated learning packs for **Reverse Learning Anything**.

| Choose this | What you need |
| --- | --- |
| **Generate with AI** | Study notes, an API key, and a LiteLLM model ID |
| **Use your existing chat app** | Study notes; copy the prepared prompt into your chat app and validate its reply |
| **Make flashcards yourself** | Questions and answers in a simple editable table or CSV; no AI or API key |
| **Check or edit a pack** | JSON from a model, a shared pack, or an example from this repo |

## Start the creator

Install Python **3.11–3.14**, open a terminal in the repository folder, and run:

```sh
python3 -m venv .venv-creator
.venv-creator/bin/python -m pip install -r creator/requirements.txt
.venv-creator/bin/python -m streamlit run creator/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open the local address printed in the terminal, usually **http://127.0.0.1:8501**. Leave the terminal open. Press **Ctrl+C** to stop. After installation, macOS/Linux users can relaunch with `bash creator/run.sh`.

On Windows, replace `.venv-creator/bin/python` with `.venv-creator\Scripts\python.exe`. If `python3` is older than 3.11, use the command for your newer Python installation, such as `python3.12`.

The creator binds to your computer's loopback address. It is a local utility, not a hosted service. Do not publish an unauthenticated creator that accepts API keys from other people.

## Generate a pack with your own API key

1. Enter a course title, subject, and the language used to teach the lessons.
2. Paste your source notes or upload a UTF-8 `.txt` or `.md` file. An uploaded file replaces pasted notes. Start with a short chapter; the limit is 100 KB. PDF and Word extraction are not yet included.
3. Choose 1–6 lessons, 3–5 questions per lesson, and suitable question types. A few varied types usually work better than requesting every type at once.
4. Select a connection, enter the model ID and key, and enter an API base URL if using a gateway or local server.
5. Click **Generate learning pack**. This sends your notes, selected settings, and the format schema to your chosen provider. Provider charges can apply. There is one request, a 60-second request timeout, and no automatic retry or automatic repair call.
6. Review the lessons and answers, then click **Download valid learning pack**.

Your key is held in the local session and passed to the SDK for authentication. The creator does not write it to a file, add it to the prompt, or put it in a pack. Use **Clear API key** when finished and stop the process to clear session memory. The selected provider or gateway processes your notes under its own policies. The creator does not enable request logging integrations.

### LiteLLM connections

The creator uses the [LiteLLM Python SDK](https://docs.litellm.ai/docs/completion/input), which accepts per-request model, key, and endpoint settings. Enter a model available in your own account; the examples below are patterns, not guaranteed model names.

| Connection | Model ID | API base | Key |
| --- | --- | --- | --- |
| Provider directly | `provider/model-name` using the provider prefix from LiteLLM's docs | Leave blank | Provider API key |
| LiteLLM proxy | `openai/your-proxy-model-alias` | Your gateway URL, often ending in `/v1` | Gateway virtual key |
| Other OpenAI-compatible endpoint | `openai/your-server-model-id` | The server's API base URL | Server API key |
| Local compatible server | `openai/your-local-model-id` | For example `http://localhost:1234/v1` | Optional if the local server needs none |

For a direct provider, use its own prefix rather than `openai/`. See the [LiteLLM provider catalogue](https://docs.litellm.ai/docs/providers). For gateways and compatible servers, LiteLLM routes `openai/` models to the supplied API base; see [OpenAI-compatible endpoints](https://docs.litellm.ai/docs/providers/openai_compatible). Do not append `/chat/completions` to the base URL. Remote bases must use HTTPS; HTTP is accepted only for localhost/loopback. Providers requiring extra cloud credentials or parameters beyond model/key/base are not configured by this UI.

**Prompt only** is the default output mode: the prompt contains the exact schema, and the reply is validated locally. **JSON object** additionally sends `response_format: {"type":"json_object"}` and requires model support. It is not a promise of schema compliance. See [LiteLLM JSON mode](https://docs.litellm.ai/docs/completion/json_mode). If a model rejects the mode or produces invalid data, no pack download is created. Adjust the settings, use fewer lessons, or use the chat-app route. Format validity does not prove factual correctness.

## No API key? Use a chat app

1. Fill in the notes and course settings in the first tab.
2. Open **Use a chat app you already have — no API key** and click **Prepare my copy-and-paste prompt**.
3. Copy or download the prompt and submit it in your chosen chat app. It includes your notes and the schema, so review the content before sharing it there.
4. Paste the returned JSON into **Check or edit JSON**, then click **Validate and prepare download**.
5. Fix any reported fields, or ask your chat app to correct them, then validate again.

Preparing the prompt and validating JSON make no AI requests. A single JSON code fence is accepted. Duplicate JSON properties, invalid answer references, unsupported versions, and oversized files are rejected.

## No AI at all? Make flashcards

Use **Make flashcards — no AI**. Enter a title and edit the Front/Back table. Add rows or upload a UTF-8 CSV with exactly these headers:

```csv
Front,Back
What is a pull request?,A proposal to merge changes between branches.
What does a README do?,Introduces a project and how to use it.
```

Create the pack and download it. Sets of up to 100 cards are split into lessons of up to ten cards. Flashcards ask learners to reveal the answer and self-assess; they do not use automated answer grading. This route never calls an AI provider.

## Use the downloaded pack in the iPhone PoC

The download is a `.learning.json` file in the app's v2 format. **The current iPhone PoC does not yet have a Files importer.** To try your material now:

1. Copy the downloaded file into `ios/ReverseLearning/`. Keep its unique filename, for example `my-course.learning.json`.
2. In `ContentView` in `ios/ReverseLearning/ReverseLearningApp.swift`, add the filename prefix to the `packs` array. For `my-course.learning.json`, add `"my-course"`.
3. Run `xcodegen generate --spec ios/project.yml` from the repo root. Open `ios/ReverseLearning.xcodeproj`, build, and run with full Xcode.

Imported/generated material should stay local unless you intend to share it publicly. The creator only offers browser downloads; it does not automatically write study material into the repository. See [the format guide](../docs/learning-pack.md) for all nine question types and [the GitHub sample courses](../examples) for larger examples.

## Test without spending API credits

```sh
.venv-creator/bin/python -m unittest discover -s creator -p 'test_*.py'
```

The tests use mocked completions and offline UI tests. A paid provider call is not required. Provider-specific live generation has to be checked with your own selected account and model.
