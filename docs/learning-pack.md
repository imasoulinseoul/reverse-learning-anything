# Learning pack v2

A pack is UTF-8 JSON conforming to `schemas/learning-pack.schema.json`. Version `2.0.0` adds `subject` and a strict union of question types. The file extension is `.learning.json`. Unknown properties are rejected. The validator continues accepting version `1.0.0` using `learning-pack-v1.schema.json`; producers should generate v2. Existing v1 packs can migrate by changing the version to 2.0.0 and adding `subject`, while keeping their existing multiple-choice questions.

## Shared structure

| Field | Meaning |
| --- | --- |
| schemaVersion | Exact supported format version |
| id | Stable pack ID |
| subject | `language`, `softwareEngineering`, `generalStudy`, or `other` |
| title, description, language | Metadata; `language` is the instructional language tag, such as en-AU, rather than the language being learned |
| sources | Local citation records: ID, title, locator such as page or section |
| lessons | Ordered lessons with concept text, duration, citations, and questions |

Every question requires `id`, `type`, `prompt`, `explanation`, and `sourceRefs`, plus exactly the fields for its variant below. IDs are globally unique in a pack, including choice, item, and pair IDs. All source references must resolve. Lesson order is contiguous from 1. Duration is an integer from 1–15 minutes. Choice/item/pair arrays contain 2–8 entries. Answers and grading are embedded locally; packs are learning resources, not secure examinations.

## Question types

| Type | Required variant fields | Grading / examples |
| --- | --- | --- |
| multipleChoice | choices: [{id,text}], correctChoiceId | Exactly one choice; vocabulary or code-output prediction |
| multipleSelect | choices: [{id,text}], correctChoiceIds: [id] | Exact set; no partial credit; select valid statements |
| trueFalse | correctAnswer: boolean | Boolean equality; misconceptions and conceptual checks |
| shortAnswer | acceptedAnswers: [string] | Explicit alternatives; translation, terminology, concise recall |
| fillBlank | acceptedAnswers: [string] | One `___` placeholder in prompt; grammar, equations, missing terms |
| ordering | items: [{id,text}], correctOrder: [id] | Exact permutation of every item; sentence construction or process steps |
| matching | pairs: [{id,left,right}] | Each left must match its paired right; definitions or translations |
| flashcard | answer: string | Reveal then self-assess; not automatically graded |
| codeCompletion | code: string, codeLanguage: string, acceptedAnswers: [string] | One `___` code placeholder; compare missing text, never execute |

Text answers normalize canonical Unicode, lowercase, and repeated whitespace, and trim surrounding whitespace. Accents, punctuation, and word order remain significant. Authors must enumerate legitimate alternatives; this is not semantic or LLM grading. Code completion only trims surrounding whitespace: case and internal formatting matter. Use multiple choice for code-reading and debugging explanations; executable coding tests need a future sandboxed design.

Matching labels must be unique after trimming and case folding on each side, to avoid visually ambiguous questions. The UI shuffles choices and matching meanings. Ordering starts shuffled and uses accessible up/down actions. A flashcard's remembered/not-yet response counts toward session scoring and is explicitly labeled self-assessment.

## Examples and limits

- `spanish-basics.learning.json`: vocabulary, cloze, phrase matching, sentence order, translation recall, flashcards.
- `python-foundations.learning.json`: code reading, multiple select, true/false, completion, terminology.
- `study-skills.learning.json`: retrieval practice, sequencing, self-assessed recall.
- `machine-learning.learning.json`: introductory single-choice compatibility example.

Citations are plain text metadata. The app must not fetch them automatically. Keep the original document locally; citation metadata does not replace the source. Packs contain no API endpoint, credentials, executable hooks, media URLs, or HTML. Arbitrary file import still needs complete validation before Swift decoding, size limits, and useful error reporting.

Audio, pronunciation, essays, image labeling, multi-blank questions, and runnable code are outside v2. Add them through a versioned schema and a corresponding renderer and grader. Run `scripts/validate_pack.py` before distributing a pack.
