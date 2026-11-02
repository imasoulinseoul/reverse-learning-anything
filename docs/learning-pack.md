# Learning pack v1

A pack is UTF-8 JSON conforming to `schemas/learning-pack.schema.json`. The canonical schema version is `1.0.0`; the file extension recommendation is `.learning.json`. Unknown properties are rejected to expose typos and prevent accidental credential storage.

| Field | Meaning |
| --- | --- |
| schemaVersion | Exact supported format version |
| id | Stable pack ID |
| title, description, language | Learner-facing metadata; language is a language tag such as en-AU |
| sources | Local citation records: ID, title, and locator such as page or section |
| lessons | Ordered short lessons with concept text, duration, citations, and questions |
| questions | Multiple-choice exercises with stable choice IDs, one correct ID, explanation and citations |

IDs must be unique across all objects. Lesson order must be contiguous from 1. Every source reference must resolve. Each correct choice must exist in that question. `estimatedMinutes` is an integer from 1–15. Citations are plain text metadata: the app must never automatically fetch them. Packs contain no API endpoint, credentials, executable content, or HTML.

Example citation: a source with `id: notes-p4` and `locator: Page 4` can be referenced by `sourceRefs: ["notes-p4"]`. Keep the original document on the user's device; citation metadata is not a replacement for the source.

Version 1 intentionally has one exercise type. Adding matching, free text grading, media, or new fields requires an explicit version and migration policy. Run the validator before distributing a pack. The starter decodes the bundled pack with Swift Codable; production import needs full validation before decoding.
