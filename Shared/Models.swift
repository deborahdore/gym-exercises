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

    var target: String { seconds > 0 ? "\(sets) × \(clock(seconds))" : "\(sets) × \(reps)" }
    var load: String { weight > 0 ? "\(weight.formatted()) kg" : "Bodyweight" }
}

struct Routine: Codable, Identifiable, Hashable {
    var id = UUID()
    var name = ""
    var weekdays: [Int] = []   // Calendar weekdays, 1 = Sunday
    var exercises: [Exercise] = []

    // Rough length of the session: about 40 s of work per set, plus the rests.
    var minutes: Int { exercises.reduce(0) { $0 + $1.sets * (max($1.seconds, 40) + $1.rest) } / 60 }
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
