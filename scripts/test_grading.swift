import Foundation

@main
struct GradingTests {
    static func main() throws {
        var kinds = Set<String>()
        let paths = try FileManager.default.contentsOfDirectory(atPath: "examples").filter { $0.hasSuffix(".learning.json") }
        for path in paths {
            let pack = try JSONDecoder().decode(LearningPack.self, from: Data(contentsOf: URL(fileURLWithPath: "examples/" + path)))
            for question in pack.lessons.flatMap(\.questions) {
                kinds.insert(question.type.rawValue)
                var response = Response()
                switch question.type {
                case .multipleChoice: response.selected = [question.correctChoiceId!]
                case .multipleSelect: response.selected = Set(question.correctChoiceIds!)
                case .trueFalse: response.boolean = question.correctAnswer
                case .shortAnswer, .fillBlank: response.text = "  " + question.acceptedAnswers!.first!.uppercased() + "  "
                case .codeCompletion: response.text = "  " + question.acceptedAnswers!.first! + "  "
                case .ordering: response.order = question.correctOrder!
                case .matching: response.matches = Dictionary(uniqueKeysWithValues: question.pairs!.map { ($0.id, $0.id) })
                case .flashcard: response.remembered = true
                }
                precondition(response.isReady(for: question), "Ready state failed: \(question.id)")
                precondition(question.isCorrect(response), "Correct answer failed: \(question.id)")
                switch question.type {
                case .multipleChoice, .multipleSelect: response.selected = ["invalid-choice"]
                case .trueFalse: response.boolean = !(question.correctAnswer!)
                case .shortAnswer, .fillBlank, .codeCompletion: response.text = "definitely incorrect"
                case .ordering: response.order.reverse()
                case .matching: response.matches = [:]
                case .flashcard: response.remembered = false
                }
                precondition(!question.isCorrect(response), "Wrong answer accepted: \(question.id)")
                if question.type == .codeCompletion {
                    response.text = question.acceptedAnswers!.first!.uppercased()
                    precondition(!question.isCorrect(response), "Code must be case-sensitive")
                }
            }
        }
        precondition(kinds.count == 9, "Missing exercise type")
        print("Swift decoding and correct/incorrect grading passed for all nine types.")
    }
}
