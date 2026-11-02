# Reverse Learning Anything

An early iPhone app concept for turning your own learning material into short, playful lessons using your own AI provider.

**Status: visual PoC + offline SwiftUI starter.** Import, live AI generation, saved progress, and secure endpoint settings are planned; the starter currently loads four bundled packs and runs nine question types locally across language, software engineering, and study packs.

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

## Create a learning pack

Use [the JSON Schema](schemas/learning-pack.schema.json), [the sample pack](examples/machine-learning.learning.json), and [the format guide](docs/learning-pack.md). Version 2 supports nine question types and subject metadata; the validator also accepts existing v1 multiple-choice packs. It rejects unknown properties and requires source citations, explanations, stable IDs, and explicit order.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_pack.py examples/*.learning.json
```

The validator checks JSON Schema plus ID uniqueness, references, answers, and sequence. The demo uses the bundled validated sample; validation of arbitrary imported files remains future work.

## Learn across subjects

| Use case | Example exercises |
| --- | --- |
| Language learning | Vocabulary choice, translation recall, sentence ordering, phrase matching, fill-in-the-blank, flashcards |
| Software engineering | Read code, select valid statements, complete a code blank, explain terminology, order steps |
| General study | Recall definitions, true/false, matching, sequence a process, self-assessed flashcards |

All nine types have native demo renderers: `multipleChoice`, `multipleSelect`, `trueFalse`, `shortAnswer`, `fillBlank`, `ordering`, `matching`, `flashcard`, `codeCompletion`. Code completion compares text without execution. Open-ended essays, speech/listening assessment, and executable coding challenges are future extensions, not supported pack types.

Short text answers match explicit accepted answers after Unicode normalization, case folding to lowercase, and whitespace normalization; accents and punctuation remain significant. Code answers only trim surrounding whitespace and remain case-sensitive. Flashcards use learner self-assessment, which counts toward session XP. All other question types use deterministic grading.

## Architecture and next steps

- SwiftUI app with local quiz flow and session XP in `ios/ReverseLearning`.
- Provider-neutral content format in `schemas` and `examples`.
- [AI endpoint contract and generation prompt](docs/ai-endpoint.md).
- [Product scope and roadmap](docs/product.md).

No provider credentials, user documents, or private project assets belong in this public repository.

## Validation

All sample packs and validator rejection tests are checked by CI. Foundation-only Swift grading tests also run on macOS. Locally, format validation, grading tests, project generation, and Swift syntax checks pass. Xcode compilation and simulator visual QA require full Xcode; they were not available in the initial authoring environment.

## License

MIT. Supply only material you have permission to use. Generated content should be reviewed before learning or sharing it.
