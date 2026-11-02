import Foundation

struct LearningPack: Decodable, Identifiable {
    let schemaVersion, id, title, description, language: String
    let subject: String?
    let sources: [Source]
    let lessons: [Lesson]
    var subjectTitle: String {
        switch subject {
        case "language": return "Language learning"
        case "softwareEngineering": return "Software engineering"
        case "other": return "Other subjects"
        default: return "General study"
        }
    }
    struct Source: Decodable, Identifiable { let id, title, locator: String }
}
struct Lesson: Decodable, Identifiable {
    let id, title, concept: String
    let order, estimatedMinutes: Int
    let sourceRefs: [String]
    let questions: [Question]
}
struct Question: Decodable, Identifiable {
    enum Kind: String, Decodable {
        case multipleChoice, multipleSelect, trueFalse, shortAnswer, fillBlank
        case ordering, matching, flashcard, codeCompletion
    }
    let id, prompt, explanation: String
    let type: Kind
    let sourceRefs: [String]
    let choices: [Choice]?
    let correctChoiceId: String?
    let correctChoiceIds: [String]?
    let correctAnswer: Bool?
    let acceptedAnswers: [String]?
    let items: [Choice]?
    let correctOrder: [String]?
    let pairs: [Pair]?
    let answer, code, codeLanguage: String?
    struct Choice: Decodable, Identifiable { let id, text: String }
    struct Pair: Decodable, Identifiable { let id, left, right: String }

    func isCorrect(_ response: Response) -> Bool {
        switch type {
        case .multipleChoice: return response.selected == Set(correctChoiceId.map { [$0] } ?? [])
        case .multipleSelect: return response.selected == Set(correctChoiceIds ?? [])
        case .trueFalse: return response.boolean == correctAnswer
        case .shortAnswer, .fillBlank, .codeCompletion:
            return (acceptedAnswers ?? []).contains { normalize($0) == normalize(response.text) }
        case .ordering: return response.order == correctOrder
        case .matching: return (pairs ?? []).allSatisfy { response.matches[$0.id] == $0.id }
        case .flashcard: return response.remembered == true
        }
    }
    private func normalize(_ value: String) -> String {
        let trimmed = value.precomposedStringWithCanonicalMapping.trimmingCharacters(in: .whitespacesAndNewlines)
        if type == .codeCompletion { return trimmed }
        return trimmed.lowercased().split(whereSeparator: { $0.isWhitespace }).joined(separator: " ")
    }
    var referenceAnswer: String {
        switch type {
        case .multipleChoice: return choices?.first { $0.id == correctChoiceId }?.text ?? ""
        case .multipleSelect: return (choices ?? []).filter { (correctChoiceIds ?? []).contains($0.id) }.map(\.text).joined(separator: ", ")
        case .trueFalse: return correctAnswer == true ? "True" : "False"
        case .shortAnswer, .fillBlank, .codeCompletion: return acceptedAnswers?.first ?? ""
        case .ordering: return (correctOrder ?? []).compactMap { id in items?.first { $0.id == id }?.text }.joined(separator: " → ")
        case .matching: return (pairs ?? []).map { "\($0.left) → \($0.right)" }.joined(separator: "\n")
        case .flashcard: return answer ?? ""
        }
    }
}
struct Response {
    var selected: Set<String> = []
    var text = ""
    var boolean: Bool?
    var order: [String] = []
    var matches: [String: String] = [:]
    var remembered: Bool?
    func isReady(for question: Question) -> Bool {
        switch question.type {
        case .multipleChoice, .multipleSelect: return !selected.isEmpty
        case .trueFalse: return boolean != nil
        case .shortAnswer, .fillBlank, .codeCompletion: return !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        case .ordering: return order.count == question.items?.count
        case .matching: return matches.count == question.pairs?.count
        case .flashcard: return remembered != nil
        }
    }
}
