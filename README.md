# Reverse Learning Anything

An early iPhone app concept for turning your own learning material into short, playful lessons using your own AI provider.

**Status: visual PoC + offline SwiftUI starter.** The local creator supports AI generation through LiteLLM; iPhone file import, in-app AI generation, saved progress, and secure endpoint settings are planned; the starter currently loads six bundled packs and runs nine question types locally across language, software engineering, and study packs.

![iPhone concept](docs/design/iphone-concept-v2.png)

## The idea

Bring notes or documents, connect your own LLM endpoint, and generate a structured learning pack. Learn in three-minute sessions with a lesson path, explanations tied to source material, and XP. Importing a prebuilt pack should also work without AI.

The visual direction is monochrome: white surfaces, black actions, quiet gray borders, and simple icons. The supplied concept is an AI-generated design exploration; the native starter is a smaller implementation, not a pixel-identical reproduction. Dashmigo's original assets were unavailable, so the design follows the described black-and-white direction.

## Run the iPhone starter

Requires full Xcode with iOS 17+ SDK and [XcodeGen](https://github.com/yonaskolb/XcodeGen).

```sh
cd ios
xcodegen generate
open ReverseLearning.xcodeproj
```

Select an iPhone simulator and run. Device signing requires your own development team. The app does not contact a network service or require an API key.

## Make your own learning materials

Start with the **[Learning Pack Creator →](creator/README.md)**. It runs on your computer and checks every pack before download.

| Easy route | What to do |
| --- | --- |
| **Bring your API key** | Paste notes, connect a provider or LiteLLM gateway, choose question types, and generate |
| **Use a chat app you already have** | Download a ready-made prompt, paste the AI reply back, and validate |
| **Skip AI completely** | Fill in a Front/Back flashcard table or upload CSV |
| **Reuse a pack** | Upload or paste an existing learning pack, edit it, and check it |

With Python 3.11–3.14 installed, run from the repo folder:

```sh
python3 -m venv .venv-creator
.venv-creator/bin/python -m pip install -r creator/requirements.txt
.venv-creator/bin/python -m streamlit run creator/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

The API key stays in the local session; generated downloads contain no endpoint settings. The first route sends your notes to your selected AI service only when you click Generate. The other routes make no AI calls. [Setup, LiteLLM connections, no-key options, and troubleshooting](creator/README.md).

**Using the download:** the current iPhone PoC needs packs bundled in Xcode; a Files importer is planned. The [creator guide](creator/README.md#use-the-downloaded-pack-in-the-iphone-poc) explains the exact steps.

For developers, the [JSON Schema](schemas/learning-pack.schema.json), [format guide](docs/learning-pack.md), and `scripts/validate_pack.py` define and validate the contract. Version 2 supports nine question types and subject metadata; the validator also accepts existing v1 multiple-choice packs.

## Learn across subjects

| Use case | Example exercises |
| --- | --- |
| Language learning | Vocabulary choice, translation recall, sentence ordering, phrase matching, fill-in-the-blank, flashcards |
| Software engineering | Read code, select valid statements, complete a code blank, explain terminology, order steps |
| General study | Recall definitions, true/false, matching, sequence a process, self-assessed flashcards |

All nine types have native demo renderers: `multipleChoice`, `multipleSelect`, `trueFalse`, `shortAnswer`, `fillBlank`, `ordering`, `matching`, `flashcard`, `codeCompletion`. Code completion compares text without execution. Open-ended essays, speech/listening assessment, and executable coding challenges are future extensions, not supported pack types.

Short text answers match explicit accepted answers after Unicode normalization, case folding to lowercase, and whitespace normalization; accents and punctuation remain significant. Code answers only trim surrounding whitespace and remain case-sensitive. Flashcards use learner self-assessment, which counts toward session XP. All other question types use deterministic grading.

## GitHub PoC courses

| Course | Content | Size |
| --- | --- | --- |
| [GitHub Basics](examples/github-basics.learning.json) | Repositories, history, branches, pull requests, forks, clones, issues | 3 lessons · 12 exercises · ~9 minutes |
| [GitHub Advanced](examples/github-advanced.learning.json) | Reviews, branch protection, merge strategies, conflicts, Actions, token permissions | 4 lessons · 16 exercises · ~12 minutes |

Both are bundled in the app library and work offline. Their [Basics notes](examples/github-basics-notes.md) and [Advanced notes](examples/github-advanced-notes.md) include official GitHub documentation links, prerequisites, and optional practice. Pack citations are plain text references; studying a pack never executes commands, calls GitHub, or changes a repository. The two courses collectively demonstrate all nine supported question types.

## Architecture and next steps

- SwiftUI app with local quiz flow and session XP in `ios/ReverseLearning`.
- Local material creator with LiteLLM, copy-prompt, flashcards, and JSON validation in `creator`.
- Provider-neutral content format in `schemas` and `examples`.
- [AI endpoint contract and generation prompt](docs/ai-endpoint.md).
- [Product scope and roadmap](docs/product.md).

No provider credentials, user documents, or private project assets belong in this public repository.

## Validation

The creator has offline unit and UI tests, including mocked API responses; no paid provider call is made by the tests. All sample packs and validator rejection tests are checked by CI. Foundation-only Swift grading tests also run on macOS. Locally, format validation, grading tests, project generation, and Swift syntax checks pass. Xcode compilation and simulator visual QA require full Xcode; they were not available in the initial authoring environment.

## License

MIT. Supply only material you have permission to use. Generated content should be reviewed before learning or sharing it.
