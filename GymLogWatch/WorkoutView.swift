import SwiftUI
import WatchKit

struct WorkoutView: View {
    enum Phase { case work, timing, rest, review }

    @Environment(Store.self) private var store
    @Environment(\.dismiss) private var dismiss

    // Snapshot taken when the workout starts, so a sync from the phone cannot reshuffle it midway.
    @State private var exercises: [Exercise]
    @State private var index = 0
    @State private var setNumber = 1
    @State private var phase = Phase.work
    @State private var end: Date?            // when the running countdown (timed set or rest) fires
    @State private var weight = 0.0          // weight being chosen for next time
    @State private var done: Set<UUID> = []
    @State private var showExercises = false
    @State private var page = 1              // 0 figure, 1 workout, 2 details
    @State private var editing = false
    @State private var session = WorkoutSession()
    @State private var askStart = true       // asked when the routine opens
    @State private var askFinish = false     // asked when going back

    init(routine: Routine) {
        _exercises = State(initialValue: routine.exercises)
    }

    private var exercise: Exercise { exercises[index] }
    // The exercises done back to back with the current one; just itself outside a circuit.
    private var circuit: Range<Int> { exercises.circuit(at: index) }

    var body: some View {
        // Swipe left for the figure, right for the details; the middle page runs the workout.
        TabView(selection: $page) {
            ExerciseFigure(id: exercise.catalogID).padding().tag(0)
            main.tag(1)
            details.tag(2)
        }
        .tabViewStyle(.page)
        // Going back ends the workout, so it asks first.
        .navigationBarBackButtonHidden()
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Back", systemImage: "chevron.backward") { askFinish = true }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button("Exercises", systemImage: "list.bullet") { showExercises = true }
            }
        }
        .sheet(isPresented: $showExercises) {
            // Jump to any exercise, e.g. when the machine for the next one is taken.
            List(exercises.indices, id: \.self) { i in
                Button { start(i) } label: {
                    HStack {
                        if exercises[i].catalogID != nil { ExerciseFigure(id: exercises[i].catalogID).frame(width: 30) }
                        Text(exercises[i].name)
                        Spacer()
                        if done.contains(exercises[i].id) { Image(systemName: "checkmark").foregroundStyle(.green) }
                    }
                }
            }
        }
        .sheet(isPresented: $editing) {
            ExerciseEdit(exercise: exercise) { edited in
                exercises[index] = edited
                setNumber = min(setNumber, edited.sets)
                store.update(edited)
            }
        }
        .alert("Start workout?", isPresented: $askStart) {
            Button("Start") { Task { await session.start() } }
            Button("Not now", role: .cancel) { dismiss() }
        }
        .alert("Finish workout?", isPresented: $askFinish) {
            Button("Finish") { finish() }
            Button("Continue", role: .cancel) {}
        }
        .task(id: end) {
            guard let end else { return }
            try? await Task.sleep(for: .seconds(end.timeIntervalSinceNow))
            guard !Task.isCancelled else { return }
            WKInterfaceDevice.current().play(.notification)
            if phase == .timing { finishSet() } else { nextSet() }
        }
        .onDisappear { Task { await session.stop() } }
    }

    private var main: some View {
        VStack(spacing: 8) {
            switch phase {
            case .work, .timing:
                Text(exercise.name).font(.title3.weight(.semibold)).lineLimit(3).minimumScaleFactor(0.7).multilineTextAlignment(.center)
                Text(circuit.count > 1 ? "Round \(setNumber) of \(exercise.sets) · \(index - circuit.lowerBound + 1)/\(circuit.count)" : "Set \(setNumber) of \(exercise.sets)")
                    .font(.footnote).foregroundStyle(.secondary)
                if phase == .timing { countdown }
                Spacer(minLength: 0)
                if phase == .timing {
                    Button("Stop") { finishSet() }
                } else if exercise.seconds > 0 {
                    Button("Start") { phase = .timing; end = .now + Double(exercise.seconds) }.buttonStyle(.borderedProminent).tint(.green)
                } else {
                    Button("Set done") { finishSet() }.buttonStyle(.borderedProminent).tint(.green)
                }

            case .rest:
                Text("Rest").font(.footnote).foregroundStyle(.secondary)
                countdown
                Text("Next: \(circuit.count > 1 ? "round" : "set") \(setNumber + 1) of \(exercise.sets)").font(.footnote)
                Spacer(minLength: 0)
                HStack {
                    Button("+15 s") { end = (end ?? .now) + 15 }
                    Button("Skip") { nextSet() }.buttonStyle(.borderedProminent).tint(.green)
                }

            case .review:
                Text(exercise.name).font(.headline).lineLimit(1)
                Text("Weight for next time").font(.footnote).foregroundStyle(.secondary)
                HStack {
                    Button("Lighter", systemImage: "minus") { weight = max(0, weight - 2.5) }
                    Text(weight.formatted())
                        .font(.system(.title2, design: .rounded).bold())
                        .frame(maxWidth: .infinity)
                        .focusable()
                        .digitalCrownRotation($weight, from: 0, through: 500, by: 0.5, sensitivity: .low, isContinuous: false, isHapticFeedbackEnabled: true)
                    Button("Heavier", systemImage: "plus") { weight = min(500, weight + 2.5) }
                }
                .labelStyle(.iconOnly)
                Spacer(minLength: 0)
                Button("Save") { saveExercise() }.buttonStyle(.borderedProminent).tint(.green)
            }
        }
        .padding(.horizontal, 4)
    }

    private var details: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                detail(exercise.seconds > 0 ? "Time" : "Reps", exercise.target)
                detail("Weight", exercise.load, .green)
                detail("Rest", clock(exercise.rest))
                if let notes = exercise.notes { detail("Notes", notes, .yellow) }
                Button("Edit", systemImage: "pencil") { editing = true }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.horizontal, 8)
        }
    }

    private func detail(_ title: String, _ value: String, _ color: Color = .primary) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title).font(.footnote).foregroundStyle(.secondary)
            Text(value).font(.system(.title3, design: .rounded).weight(.semibold)).foregroundStyle(color)
        }
    }

    private var countdown: some View {
        Text(timerInterval: Date.now...max(end ?? .now, .now), countsDown: true)
            .font(.system(size: 44, weight: .semibold, design: .rounded))
            .monospacedDigit()
            .multilineTextAlignment(.center)
    }

    private func finishSet() {
        end = nil
        let circuit = circuit
        if index < circuit.upperBound - 1 {
            // Straight to the next exercise of the circuit; the rest comes after the last one.
            index += 1
            phase = .work
            page = 1
        } else if setNumber >= exercise.sets, circuit.count > 1 {
            // A circuit is logged as it was done, without asking a new weight for each exercise.
            for exercise in exercises[circuit] {
                store.record(LogEntry(exerciseID: exercise.id, name: exercise.name, weight: exercise.weight, target: exercise.target, next: exercise.weight))
                done.insert(exercise.id)
            }
            advance()
        } else if setNumber >= exercise.sets {
            weight = exercise.weight
            phase = .review
        } else if exercise.rest > 0 {
            phase = .rest
            end = .now + Double(exercise.rest)
        } else {
            nextSet()
        }
    }

    private func nextSet() {
        end = nil
        index = circuit.lowerBound
        setNumber += 1
        phase = .work
    }

    private func saveExercise() {
        store.record(LogEntry(exerciseID: exercise.id, name: exercise.name, weight: exercise.weight, target: exercise.target, next: weight))
        done.insert(exercise.id)
        advance()
    }

    private func advance() {
        if let next = exercises.firstIndex(where: { !done.contains($0.id) }) {
            start(next)
        } else {
            // Last exercise done: save the workout to Fitness and go back to the routines.
            WKInterfaceDevice.current().play(.success)
            finish()
        }
    }

    private func finish() {
        end = nil
        Task {
            await session.stop()
            dismiss()
        }
    }

    private func start(_ i: Int) {
        end = nil
        index = i
        setNumber = 1
        phase = .work
        page = 1
        showExercises = false
    }
}

// Change the plan from the wrist; the phone gets the same values.
struct ExerciseEdit: View {
    @Environment(\.dismiss) private var dismiss
    @State var exercise: Exercise
    let save: (Exercise) -> Void

    var body: some View {
        NavigationStack {
            List {
                // The rounds and the rest of a circuit belong to all its exercises: they are set on the phone.
                if exercise.circuit == nil {
                    Section("Sets") { Stepper("\(exercise.sets)", value: $exercise.sets, in: 1...20) }
                }
                if exercise.seconds > 0 {
                    Section("Time per set") { Stepper(clock(exercise.seconds), value: $exercise.seconds, in: 5...600, step: 5) }
                } else {
                    Section("Reps") { Stepper("\(exercise.reps)", value: $exercise.reps, in: 1...100) }
                }
                Section("Weight (kg)") { Stepper(exercise.weight.formatted(), value: $exercise.weight, in: 0...500, step: 2.5) }
                if exercise.circuit == nil {
                    Section("Rest") { Stepper(clock(exercise.rest), value: $exercise.rest, in: 0...600, step: 15) }
                }
                Section("Notes") {
                    TextField("Notes", text: Binding(get: { exercise.notes ?? "" }, set: { exercise.notes = $0.isEmpty ? nil : $0 }))
                }
            }
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save", systemImage: "checkmark") {
                        save(exercise)
                        dismiss()
                    }
                }
            }
        }
    }
}
