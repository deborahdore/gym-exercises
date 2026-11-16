import Foundation

struct Exercise: Codable, Identifiable, Hashable {
    var id = UUID()
    var name = ""
    var sets = 3
    var reps = 10
    var seconds = 0      // > 0 makes it a timed set (plank, wall sit…) and reps are ignored
    var weight = 0.0     // kg, 0 = bodyweight
    var rest = 90        // seconds between sets
    var catalogID: String?   // built-in exercise it was picked from (see Catalog.swift); nil for custom ones
    var notes: String?       // free text, e.g. machine settings; optional so older saved data still loads
    var circuit: UUID?       // exercises next to each other with the same value are done back to back (see circuit(at:))

    var target: String { seconds > 0 ? "\(sets) × \(clock(seconds))" : "\(sets) × \(reps)" }
    var amount: String { seconds > 0 ? clock(seconds) : "\(reps) reps" }
    var load: String { weight > 0 ? "\(weight.formatted()) kg" : "Bodyweight" }
}

// A circuit: its exercises are done one after the other without rest, then comes the rest,
// and the whole thing is repeated. Its exercises share the number of sets (the rounds) and the rest.
extension Array where Element == Exercise {
    func circuit(at i: Int) -> Range<Int> {
        guard let id = self[i].circuit else { return i..<i + 1 }
        var first = i, last = i
        while first > 0, self[first - 1].circuit == id { first -= 1 }
        while last + 1 < count, self[last + 1].circuit == id { last += 1 }
        return first..<last + 1
    }
}

struct Routine: Codable, Identifiable, Hashable {
    var id = UUID()
    var name = ""
    var weekdays: [Int] = []   // Calendar weekdays, 1 = Sunday
    var exercises: [Exercise] = []

    // Rough length of the session: about 40 s of work per set, plus the rests.
    var minutes: Int {
        exercises.indices.reduce(0) { total, i in
            let exercise = exercises[i], rests = i == exercises.circuit(at: i).upperBound - 1
            return total + exercise.sets * (max(exercise.seconds, 40) + (rests ? exercise.rest : 0))
        } / 60
    }
    var isToday: Bool { weekdays.contains(Calendar.current.component(.weekday, from: .now)) }
    var days: String {
        mondayFirst.filter { weekdays.contains($0) }.map { Calendar.current.shortWeekdaySymbols[$0 - 1] }.joined(separator: " · ")
    }
}

// One completed exercise: what was lifted, and the weight chosen for next time.
struct LogEntry: Codable, Identifiable, Hashable {
    var id = UUID()
    var date = Date()
    var exerciseID: UUID
    var name: String
    var weight: Double
    var target: String
    var next: Double
}

struct GymData: Codable {
    var routines: [Routine] = []
    var log: [LogEntry] = []
}

let mondayFirst = [2, 3, 4, 5, 6, 7, 1]

func clock(_ seconds: Int) -> String { String(format: "%d:%02d", seconds / 60, seconds % 60) }
