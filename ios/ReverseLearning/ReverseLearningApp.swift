import SwiftUI

@main
struct ReverseLearningApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView().tint(.primary)
        }
    }
}

struct ContentView: View {
    private let packs: [LearningPack] = ["sample", "spanish-basics", "python-foundations", "study-skills"].compactMap { name in
        guard let url = Bundle.main.url(forResource: name + ".learning", withExtension: "json"),
              let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(LearningPack.self, from: data)
    }
    @State private var xp = 0
    @State private var completed: Set<String> = []
    var body: some View {
        if !packs.isEmpty {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        Image(systemName: "book.closed.fill").font(.largeTitle)
                        Text("Your library").font(.largeTitle.bold())
                        Text("Your material. A little progress, every day.").foregroundStyle(.secondary)
                        Label("Offline demo · \(xp) XP this session", systemImage: "sparkles")
                            .font(.subheadline).padding().background(.quaternary, in: RoundedRectangle(cornerRadius: 18))
                        ForEach(packs) { pack in
                            NavigationLink {
                                LessonPath(pack: pack, xp: $xp, completed: $completed)
                            } label: {
                                VStack(alignment: .leading, spacing: 8) {
                                    Label(pack.title, systemImage: "book").font(.headline)
                                    Text(pack.description).font(.subheadline).lineLimit(2)
                                    Text("\(pack.lessons.count) lesson · \(pack.subjectTitle)").font(.caption)
                                }.frame(maxWidth: .infinity, alignment: .leading).padding()
                                    .overlay(RoundedRectangle(cornerRadius: 18).stroke(.gray.opacity(0.4)))
                            }.buttonStyle(.plain)
                        }
                        VStack(alignment: .leading, spacing: 8) {
                            Label("Your AI", systemImage: "link").font(.headline)
                            Text("Bring your own endpoint and import materials in a future release. This demo includes language, software engineering, and general study packs.")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }.padding().background(.quaternary, in: RoundedRectangle(cornerRadius: 18))
                    }.padding(24)
                }.navigationTitle("Reverse Learning Anything").navigationBarTitleDisplayMode(.inline)
            }
        } else {
            ContentUnavailableView("Sample unavailable", systemImage: "doc.badge.exclamationmark", description: Text("The bundled learning pack could not be loaded."))
        }
    }
}

struct LessonPath: View {
    let pack: LearningPack
    @Binding var xp: Int
    @Binding var completed: Set<String>
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Text("A little, every day.").font(.largeTitle.bold())
                Text("\(xp) XP this session").font(.headline)
                Text(pack.title).foregroundStyle(.secondary)
                ForEach(pack.lessons.sorted { $0.order < $1.order }) { lesson in
                    NavigationLink {
                        QuizView(lesson: lesson, sources: pack.sources) { earned in
                            if completed.insert(lesson.id).inserted { xp += earned }
                        }
                    } label: {
                        HStack(spacing: 18) {
                            Image(systemName: completed.contains(lesson.id) ? "checkmark.circle.fill" : "play.circle.fill").font(.largeTitle)
                            VStack(alignment: .leading, spacing: 6) {
                                Text(lesson.title).font(.headline)
                                Text("\(lesson.estimatedMinutes) min · \(lesson.questions.count) questions").font(.caption)
                            }
                            Spacer()
                        }.padding().background(.quaternary, in: RoundedRectangle(cornerRadius: 18))
                    }.buttonStyle(.plain)
                }
                Text("Complete a lesson to earn XP. Replays are always available; XP is awarded once per lesson per session.")
                    .font(.footnote).foregroundStyle(.secondary)
            }.padding(24)
        }.navigationTitle("Learn").navigationBarTitleDisplayMode(.inline)
    }
}

struct QuizView: View {
    let lesson: Lesson
    let sources: [LearningPack.Source]
    let onComplete: (Int) -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var started = false
    @State private var index = 0
    @State private var response = Response()
    @State private var submitted = false
    @State private var score = 0
    @State private var finished = false
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                if finished {
                    Image(systemName: "checkmark.seal.fill").font(.system(size: 56))
                    Text("Lesson complete").font(.largeTitle.bold())
                    Text("\(score) of \(lesson.questions.count) correct or recalled · \(score * 20) XP scored")
                    Text("Flashcards count your self-assessment. Every answer is a chance to learn.").foregroundStyle(.secondary)
                    action("Back to path") { dismiss() }
                } else if !started {
                    Text(lesson.title).font(.largeTitle.bold())
                    Text(lesson.concept).font(.title3)
                    Text("Read this short idea, then check your understanding.").foregroundStyle(.secondary)
                    action("Start lesson") {
                        guard let first = lesson.questions.first else { return }
                        prepare(first)
                        started = true
                    }
                } else {
                    let question = lesson.questions[index]
                    ProgressView(value: Double(index + 1), total: Double(lesson.questions.count)).tint(.primary)
                    Text("\(index + 1) OF \(lesson.questions.count)").font(.caption.bold()).foregroundStyle(.secondary)
                    Text(question.prompt).font(.title.bold())
                    QuestionInput(question: question, response: $response)
                        .id(question.id).disabled(submitted)
                    if submitted {
                        VStack(alignment: .leading, spacing: 12) {
                            Text(question.isCorrect(response) ? "Well done." : "Keep learning.").font(.title2.bold())
                            Text("Answer: \(question.referenceAnswer)")
                            Text(question.explanation)
                            ForEach(sources.filter { question.sourceRefs.contains($0.id) }) { source in
                                Label("\(source.title) · \(source.locator)", systemImage: "doc.text").font(.caption)
                            }
                        }.padding().background(.quaternary, in: RoundedRectangle(cornerRadius: 18))
                    }
                    action(submitted ? "Continue" : (question.type == .flashcard ? "Save self-assessment" : "Check answer")) {
                        if !submitted {
                            if question.isCorrect(response) { score += 1 }
                            submitted = true
                        } else if index + 1 < lesson.questions.count {
                            index += 1
                            prepare(lesson.questions[index])
                        } else {
                            finished = true
                            onComplete(score * 20)
                        }
                    }.disabled(!response.isReady(for: question))
                }
            }.padding(24)
        }.navigationTitle("\(lesson.estimatedMinutes)-minute lesson").navigationBarTitleDisplayMode(.inline)
    }
    private func prepare(_ question: Question) {
        response = Response()
        response.order = (question.items ?? []).shuffled().map(\.id)
        submitted = false
    }
    private func action(_ title: String, perform: @escaping () -> Void) -> some View {
        Button(action: perform) {
            Text(title).font(.headline).frame(maxWidth: .infinity).padding()
        }.buttonStyle(.borderedProminent).tint(.primary)
    }
}

struct QuestionInput: View {
    let question: Question
    @Binding var response: Response
    @State private var revealed = false
    @State private var choices: [Question.Choice] = []
    @State private var rightPairs: [Question.Pair] = []
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            switch question.type {
            case .multipleChoice, .multipleSelect:
                if question.type == .multipleSelect { Text("Select all that apply.").font(.caption) }
                ForEach(choices) { choice in
                    Button {
                        if question.type == .multipleChoice { response.selected = [choice.id] }
                        else if !response.selected.insert(choice.id).inserted { response.selected.remove(choice.id) }
                    } label: {
                        HStack {
                            Text(choice.text).multilineTextAlignment(.leading)
                            Spacer()
                            Image(systemName: response.selected.contains(choice.id) ? "checkmark.circle.fill" : "circle")
                        }.padding().frame(maxWidth: .infinity, minHeight: 54, alignment: .leading)
                            .overlay(RoundedRectangle(cornerRadius: 16).stroke(.gray.opacity(0.5)))
                    }.buttonStyle(.plain)
                        .accessibilityAddTraits(response.selected.contains(choice.id) ? .isSelected : [])
                }
            case .trueFalse:
                ForEach([true, false], id: \.self) { value in
                    Button { response.boolean = value } label: {
                        Label(value ? "True" : "False", systemImage: response.boolean == value ? "checkmark.circle.fill" : "circle")
                            .frame(maxWidth: .infinity, alignment: .leading).padding()
                    }.buttonStyle(.bordered)
                }
            case .shortAnswer, .fillBlank, .codeCompletion:
                if let code = question.code {
                    Text(question.codeLanguage ?? "Code").font(.caption)
                    Text(code).font(.system(.body, design: .monospaced)).textSelection(.enabled)
                    Text("Fill the blank. Code is checked as text and never executed.").font(.caption)
                }
                TextField("Your answer", text: $response.text, axis: .vertical)
                    .textFieldStyle(.roundedBorder).textInputAutocapitalization(.never).autocorrectionDisabled()
                Text(question.type == .codeCompletion ? "Case-sensitive; surrounding whitespace is ignored." : "Accepted answers ignore case and repeated whitespace; accents and punctuation matter.")
                    .font(.caption).foregroundStyle(.secondary)
            case .ordering:
                Text("Use the arrows to arrange the items from first to last.").font(.caption)
                ForEach(Array(response.order.enumerated()), id: \.element) { index, id in
                    HStack {
                        Text("\(index + 1). \(question.items?.first { $0.id == id }?.text ?? "")")
                        Spacer()
                        Button { response.order.swapAt(index, index - 1) } label: { Image(systemName: "arrow.up") }
                            .disabled(index == 0).accessibilityLabel("Move item \(index + 1) up")
                        Button { response.order.swapAt(index, index + 1) } label: { Image(systemName: "arrow.down") }
                            .disabled(index == response.order.count - 1).accessibilityLabel("Move item \(index + 1) down")
                    }.padding(.vertical, 8)
                }
            case .matching:
                Text("Choose one matching meaning per item. Use each meaning once.").font(.caption)
                ForEach(question.pairs ?? []) { pair in
                    Picker(pair.left, selection: Binding(get: { response.matches[pair.id] ?? "" }, set: { response.matches[pair.id] = $0.isEmpty ? nil : $0 })) {
                        Text("Choose…").tag("")
                        ForEach(rightPairs) { right in Text(right.right).tag(right.id) }
                    }.pickerStyle(.menu)
                }
            case .flashcard:
                if revealed {
                    Text(question.answer ?? "").font(.title2).textSelection(.enabled)
                    Text("Self-assessment: did you remember it before revealing?").font(.caption)
                    HStack {
                        Button("Remembered") { response.remembered = true }
                        Button("Needs practice") { response.remembered = false }
                    }.buttonStyle(.bordered)
                    if let remembered = response.remembered { Text(remembered ? "Marked as remembered" : "Marked for practice").font(.caption) }
                } else {
                    Button("Reveal answer") { revealed = true }.buttonStyle(.bordered)
                }
            }
        }.onAppear {
            choices = (question.choices ?? []).shuffled()
            rightPairs = (question.pairs ?? []).shuffled()
        }
    }
}
