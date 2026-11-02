import SwiftUI

struct LearningPack: Decodable {
    let schemaVersion, id, title, description, language: String
    let sources: [Source]
    let lessons: [Lesson]
    struct Source: Decodable, Identifiable { let id, title, locator: String }
}
struct Lesson: Decodable, Identifiable {
    let id, title, concept: String
    let order, estimatedMinutes: Int
    let sourceRefs: [String]
    let questions: [Question]
}
struct Question: Decodable, Identifiable {
    let id, type, prompt, correctChoiceId, explanation: String
    let choices: [Choice]
    let sourceRefs: [String]
    struct Choice: Decodable, Identifiable { let id, text: String }
}

@main
struct ReverseLearningApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView().tint(.primary)
        }
    }
}

struct ContentView: View {
    private let pack: LearningPack? = {
        guard let url = Bundle.main.url(forResource: "sample.learning", withExtension: "json"),
              let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(LearningPack.self, from: data)
    }()
    @State private var xp = 0
    @State private var completed: Set<String> = []
    var body: some View {
        if let pack {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        Image(systemName: "book.closed.fill").font(.largeTitle)
                        Text("Your library").font(.largeTitle.bold())
                        Text("Your material. A little progress, every day.").foregroundStyle(.secondary)
                        Label("Offline demo · \(xp) XP this session", systemImage: "sparkles")
                            .font(.subheadline).padding().background(.quaternary, in: RoundedRectangle(cornerRadius: 18))
                        NavigationLink {
                            LessonPath(pack: pack, xp: $xp, completed: $completed)
                        } label: {
                            VStack(alignment: .leading, spacing: 8) {
                                Label(pack.title, systemImage: "book").font(.headline)
                                Text(pack.description).font(.subheadline)
                                Text("\(pack.lessons.count) lesson · 3 min").font(.caption)
                            }.frame(maxWidth: .infinity, alignment: .leading).padding()
                                .overlay(RoundedRectangle(cornerRadius: 18).stroke(.gray.opacity(0.4)))
                        }.buttonStyle(.plain)
                        VStack(alignment: .leading, spacing: 8) {
                            Label("Your AI", systemImage: "link").font(.headline)
                            Text("Bring your own endpoint and import materials in a future release. This demo uses a bundled learning pack.")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }.padding().background(.quaternary, in: RoundedRectangle(cornerRadius: 18))
                    }.padding(24)
                }.navigationTitle("Reverse Learning").navigationBarTitleDisplayMode(.inline)
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
    @State private var selected: String?
    @State private var submitted = false
    @State private var score = 0
    @State private var finished = false
    @State private var choices: [Question.Choice] = []
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                if finished {
                    Image(systemName: "checkmark.seal.fill").font(.system(size: 56))
                    Text("Lesson complete").font(.largeTitle.bold())
                    Text("\(score) of \(lesson.questions.count) correct · \(score * 20) XP scored")
                    Text("Every answer is a chance to learn. Come back for another round.").foregroundStyle(.secondary)
                    action("Back to path") { dismiss() }
                } else if !started {
                    Text(lesson.title).font(.largeTitle.bold())
                    Text(lesson.concept).font(.title3)
                    Text("Read this short idea, then check your understanding.").foregroundStyle(.secondary)
                    action("Start lesson") {
                        guard let first = lesson.questions.first else { return }
                        choices = first.choices.shuffled()
                        started = true
                    }
                } else {
                    let question = lesson.questions[index]
                    ProgressView(value: Double(index + 1), total: Double(lesson.questions.count)).tint(.primary)
                    Text("\(index + 1) OF \(lesson.questions.count)").font(.caption.bold()).foregroundStyle(.secondary)
                    Text(question.prompt).font(.largeTitle.bold())
                    ForEach(choices) { choice in
                        Button { selected = choice.id } label: {
                            HStack {
                                Text(choice.text).multilineTextAlignment(.leading)
                                Spacer()
                                if selected == choice.id { Image(systemName: "checkmark.circle.fill") }
                            }.padding().frame(maxWidth: .infinity, minHeight: 54, alignment: .leading)
                                .overlay(RoundedRectangle(cornerRadius: 16).stroke(selected == choice.id ? Color.primary : Color.gray.opacity(0.4), lineWidth: selected == choice.id ? 2 : 1))
                        }.buttonStyle(.plain).disabled(submitted)
                            .accessibilityAddTraits(selected == choice.id ? .isSelected : [])
                    }
                    if submitted {
                        VStack(alignment: .leading, spacing: 12) {
                            Text(selected == question.correctChoiceId ? "That's right." : "Keep learning.").font(.title2.bold())
                            Text(question.explanation)
                            ForEach(sources.filter { question.sourceRefs.contains($0.id) }) { source in
                                Label("\(source.title) · \(source.locator)", systemImage: "doc.text").font(.caption)
                            }
                        }.padding().background(.quaternary, in: RoundedRectangle(cornerRadius: 18))
                    }
                    action(submitted ? "Continue" : "Check answer") {
                        if !submitted {
                            if selected == question.correctChoiceId { score += 1 }
                            submitted = true
                        } else if index + 1 < lesson.questions.count {
                            index += 1
                            choices = lesson.questions[index].choices.shuffled()
                            selected = nil
                            submitted = false
                        } else {
                            finished = true
                            onComplete(score * 20)
                        }
                    }.disabled(selected == nil)
                }
            }.padding(24)
        }.navigationTitle("\(lesson.estimatedMinutes)-minute lesson").navigationBarTitleDisplayMode(.inline)
    }
    private func action(_ title: String, perform: @escaping () -> Void) -> some View {
        Button(action: perform) {
            Text(title).font(.headline).frame(maxWidth: .infinity).padding()
        }.buttonStyle(.borderedProminent).tint(.primary)
    }
}
