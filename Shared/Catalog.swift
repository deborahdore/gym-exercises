import SwiftUI
import UIKit

// The built-in exercise list. Only the names ship with the app: each figure lives in
// catalog/images on GitHub (drawn by catalog/figures.py) and is downloaded the first time
// its exercise is selected, then kept on the device.
struct CatalogExercise: Identifiable, Hashable {
    let id: String          // also the image file name
    let name: String
    let muscle: String
    let equipment: String
    var seconds = 0         // > 0 for timed holds

    var kind: String {
        switch equipment {
        case "Machine", "Cable": "Machines"
        case "Barbell", "Dumbbell": "Free weights"
        default: "Bodyweight"
        }
    }

    var exercise: Exercise {
        Exercise(name: name, seconds: seconds, rest: muscle == "Core" ? 60 : equipment == "Barbell" ? 120 : 90, catalogID: id)
    }
}

let muscles = ["Chest", "Back", "Shoulders", "Arms", "Legs", "Core"]

private func x(_ id: String, _ name: String, _ muscle: String, _ equipment: String, _ seconds: Int = 0) -> CatalogExercise {
    CatalogExercise(id: id, name: name, muscle: muscle, equipment: equipment, seconds: seconds)
}

let catalog: [CatalogExercise] = [
    x("bench_press", "Bench Press", "Chest", "Barbell"),
    x("incline_dumbbell_press", "Incline Dumbbell Press", "Chest", "Dumbbell"),
    x("dumbbell_fly", "Dumbbell Fly", "Chest", "Dumbbell"),
    x("chest_press_machine", "Chest Press Machine", "Chest", "Machine"),
    x("pec_deck", "Pec Deck", "Chest", "Machine"),
    x("cable_crossover", "Cable Crossover", "Chest", "Cable"),
    x("push_up", "Push-Up", "Chest", "Bodyweight"),
    x("dip", "Dip", "Chest", "Bodyweight"),

    x("pull_up", "Pull-Up", "Back", "Bodyweight"),
    x("lat_pulldown", "Lat Pulldown", "Back", "Machine"),
    x("seated_cable_row", "Seated Cable Row", "Back", "Cable"),
    x("barbell_row", "Barbell Row", "Back", "Barbell"),
    x("dumbbell_row", "Dumbbell Row", "Back", "Dumbbell"),
    x("deadlift", "Deadlift", "Back", "Barbell"),
    x("back_extension", "Back Extension", "Back", "Bodyweight"),

    x("overhead_press", "Overhead Press", "Shoulders", "Barbell"),
    x("dumbbell_shoulder_press", "Dumbbell Shoulder Press", "Shoulders", "Dumbbell"),
    x("shoulder_press_machine", "Shoulder Press Machine", "Shoulders", "Machine"),
    x("lateral_raise", "Lateral Raise", "Shoulders", "Dumbbell"),
    x("front_raise", "Front Raise", "Shoulders", "Dumbbell"),
    x("face_pull", "Face Pull", "Shoulders", "Cable"),

    x("barbell_curl", "Barbell Curl", "Arms", "Barbell"),
    x("dumbbell_curl", "Dumbbell Curl", "Arms", "Dumbbell"),
    x("hammer_curl", "Hammer Curl", "Arms", "Dumbbell"),
    x("preacher_curl", "Preacher Curl", "Arms", "Barbell"),
    x("triceps_pushdown", "Triceps Pushdown", "Arms", "Cable"),
    x("overhead_triceps_extension", "Overhead Triceps Extension", "Arms", "Dumbbell"),
    x("skull_crusher", "Skull Crusher", "Arms", "Barbell"),
    x("bench_dip", "Bench Dip", "Arms", "Bodyweight"),

    x("squat", "Squat", "Legs", "Barbell"),
    x("leg_press", "Leg Press", "Legs", "Machine"),
    x("leg_extension", "Leg Extension", "Legs", "Machine"),
    x("leg_curl", "Leg Curl", "Legs", "Machine"),
    x("lunge", "Lunge", "Legs", "Dumbbell"),
    x("bulgarian_split_squat", "Bulgarian Split Squat", "Legs", "Dumbbell"),
    x("romanian_deadlift", "Romanian Deadlift", "Legs", "Barbell"),
    x("hip_thrust", "Hip Thrust", "Legs", "Barbell"),
    x("hip_abduction_machine", "Hip Abduction Machine", "Legs", "Machine"),
    x("calf_raise", "Calf Raise", "Legs", "Dumbbell"),
    x("goblet_squat", "Goblet Squat", "Legs", "Dumbbell"),
    x("cable_kickback", "Cable Kickback", "Legs", "Cable"),

    x("plank", "Plank", "Core", "Bodyweight", 45),
    x("side_plank", "Side Plank", "Core", "Bodyweight", 30),
    x("crunch", "Crunch", "Core", "Bodyweight"),
    x("hanging_leg_raise", "Hanging Leg Raise", "Core", "Bodyweight"),
    x("russian_twist", "Russian Twist", "Core", "Dumbbell"),
    x("cable_crunch", "Cable Crunch", "Core", "Cable"),
    x("mountain_climber", "Mountain Climber", "Core", "Bodyweight", 30),
]

// Reads a figure from the device, or fetches it from GitHub when `download` is set.
func figure(_ id: String, download: Bool) async -> UIImage? {
    let folder = URL.applicationSupportDirectory.appending(path: "figures")
    let file = folder.appending(path: "\(id).png")
    if let data = try? Data(contentsOf: file) { return UIImage(data: data) }
    guard download,
          let url = URL(string: "https://raw.githubusercontent.com/deborahdore/gym-exercises/main/catalog/images/\(id).png"),
          let (data, response) = try? await URLSession.shared.data(from: url),
          (response as? HTTPURLResponse)?.statusCode == 200,
          let image = UIImage(data: data) else { return nil }
    try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
    try? data.write(to: file, options: .atomic)
    return image
}

// Square tile with the exercise figure. The figures are drawn for a light background,
// so the tile keeps the same colour in dark mode.
struct ExerciseFigure: View {
    var id: String?
    var download = true
    @State private var image: UIImage?

    var body: some View {
        ZStack {
            Color(red: 0.945, green: 0.961, blue: 0.976)
            if let image {
                Image(uiImage: image).resizable().scaledToFit()
            } else {
                Image(systemName: "dumbbell.fill").foregroundStyle(Color(red: 0.58, green: 0.64, blue: 0.72))
            }
        }
        .aspectRatio(1, contentMode: .fit)
        .clipShape(.rect(cornerRadius: 10))
        .accessibilityHidden(true)
        .task(id: "\(id ?? "") \(download)") {
            guard let id else { image = nil; return }
            image = await figure(id, download: download)
        }
    }
}
