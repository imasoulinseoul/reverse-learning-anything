# Reverse Learning Anything — product direction

## Core journey
1. Add your own notes, text, or an existing learning pack.
2. If generating, select your own endpoint and review exactly what material will be sent.
3. Preview the generated curriculum and its source citations.
4. Complete a short lesson, see an explanation, and earn XP.
5. Return for review and continue along the path.

## Principles
Content belongs to the learner. AI providers are interchangeable. Imported packs can be used offline. A streak encourages a habit without blocking learning. Avoid paid hearts, punitive timers, and competitive pressure in the MVP.

## Prototype delivered
A monochrome three-screen design concept, a SwiftUI library/lesson/quiz flow with six bundled packs and nine question renderers, deterministic grading plus self-assessed flashcards, session XP, a versioned schema, a validator, and endpoint integration specifications. The library includes language learning, software engineering, general study, machine learning, GitHub Basics, and GitHub Advanced. Restarting the app resets progress.

## MVP backlog
- File importer for JSON packs, with size limits, schema + semantic validation, and actionable errors.
- Text and PDF ingestion with source IDs and page mapping; inspect extracted text first.
- Endpoint configuration, Keychain token storage, timeouts, cancellation, and generation preview.
- Persistent lesson progress and local calendar-day streaks with accessible non-color feedback.
- Review scheduling, VoiceOver audit, Dynamic Type QA, reduced motion, dark appearance.
- Native app icon derived from the selected concept, screenshots, tests on an iPhone simulator, and release signing.

## Future
The v2 format covers nine question types. Speech/listening, essays, media questions, multi-blank questions, and executable code challenges require future schema versions, renderers, and explicit grading designs. Sharing, accounts, remote storage, subscriptions, and hosted generation are outside the initial scope.

## Visual direction
Original open-book / ascending-step mark, black and white palette, strong typography and soft rounded surfaces. The concept board explores library, path, and quiz. Do not ship the whole concept image as an app icon. Review name and icon before App Store release.
