import SwiftUI

struct RoutinesView: View {
    @Environment(Store.self) private var store
    @State private var path: [UUID] = []

    var body: some View {
        @Bindable var store = store
        NavigationStack(path: $path) {
            List {
                ForEach(store.data.routines) { routine in
                    NavigationLink(value: routine.id) {
                        HStack {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(routine.name.isEmpty ? "New routine" : routine.name).font(.headline)
                                Text([routine.days, "\(routine.exercises.count) exercises", routine.exercises.isEmpty ? "" : "about \(routine.minutes) min"].filter { !$0.isEmpty }.joined(separator: " · "))
                                    .font(.subheadline)
                                    .foregroundStyle(Color.secondary)
                            }
                            Spacer()
                            if routine.isToday {
                                Text("Today")
                                    .font(.caption.weight(.semibold))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.accentColor.opacity(0.15), in: Capsule())
                                    .foregroundStyle(Color.accentColor)
                            }
                        }
                    }
                }
                .onDelete { store.data.routines.remove(atOffsets: $0) }
                .onMove { store.data.routines.move(fromOffsets: $0, toOffset: $1) }
            }
            .overlay {
                if store.data.routines.isEmpty {
                    ContentUnavailableView("No routines yet", systemImage: "dumbbell", description: Text("Tap + to plan your first training day."))
                }
            }
            .navigationTitle("Routines")
            .navigationDestination(for: UUID.self) { id in
                if let routine = $store.data.routines.first(where: { $0.wrappedValue.id == id }) {
                    RoutineEditor(routine: routine)
                }
            }
            .toolbar {
                ToolbarItem(placement: .topBarLeading) { EditButton() }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Add routine", systemImage: "plus") {
                        let routine = Routine()
                        store.data.routines.append(routine)
                        path.append(routine.id)
                    }
                }
            }
        }
    }
}

struct RoutineEditor: View {
    @Environment(\.dismiss) private var dismiss
    @Binding var routine: Routine
    @State private var picking = false
    @State private var pickingCircuit = false

    var body: some View {
        Form {
            Section {
                TextField("Name, e.g. Push day", text: $routine.name)
                HStack {
                    ForEach(mondayFirst, id: \.self) { day in
                        let on = routine.weekdays.contains(day)
                        Button {
                            if on { routine.weekdays.removeAll { $0 == day } } else { routine.weekdays.append(day) }
                        } label: {
                            Text(Calendar.current.veryShortWeekdaySymbols[day - 1])
                                .frame(width: 34, height: 34)
                                .background(on ? Color.accentColor : Color.gray.opacity(0.2), in: Circle())
                                .foregroundStyle(on ? Color.white : Color.primary)
                        }
                        .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderless)
            }
            Section("Exercises") {
                ForEach($routine.exercises) { $exercise in
                    let first = routine.exercises.firstIndex { $0.id == exercise.id }.map { $0 == routine.exercises.circuit(at: $0).lowerBound } ?? false
                    NavigationLink {
                        ExerciseEditor(exercise: $exercise)
                    } label: {
                        HStack(spacing: 12) {
                            if exercise.circuit != nil { Capsule().fill(Color.orange).frame(width: 4) }
                            ExerciseFigure(id: exercise.catalogID).frame(width: 52)
                            VStack(alignment: .leading, spacing: 2) {
                                if exercise.circuit != nil, first {
                                    Text("Circuit · \(exercise.sets) rounds · rest \(clock(exercise.rest))")
                                        .font(.caption.weight(.semibold)).foregroundStyle(.orange)
                                }
                                Text(exercise.name.isEmpty ? "New exercise" : exercise.name)
                                Text(exercise.circuit != nil ? "\(exercise.amount) · \(exercise.load)" : "\(exercise.target) · \(exercise.load) · rest \(clock(exercise.rest))")
                                    .font(.subheadline).foregroundStyle(.secondary)
                                if let notes = exercise.notes {
                                    Label(notes, systemImage: "note.text")
                                        .font(.footnote).foregroundStyle(.secondary).lineLimit(2)
                                }
                            }
                        }
                    }
                }
                .onDelete { routine.exercises.remove(atOffsets: $0) }
                .onMove { routine.exercises.move(fromOffsets: $0, toOffset: $1) }
                Button("Add exercises", systemImage: "plus") { picking = true }
                Button("Add a circuit", systemImage: "arrow.triangle.2.circlepath") { pickingCircuit = true }
            }
        }
        .sheet(isPresented: $picking) {
            ExercisePicker { routine.exercises += $0 }
        }
        .sheet(isPresented: $pickingCircuit) {
            // The picked exercises are done back to back, with one rest after the last.
            ExercisePicker { picked in
                let id = UUID()
                routine.exercises += picked.map { exercise in
                    var exercise = exercise
                    exercise.circuit = id
                    exercise.sets = 3
                    exercise.rest = 60
                    return exercise
                }
            }
        }
        .navigationTitle(routine.name.isEmpty ? "New routine" : routine.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) { EditButton() }
            ToolbarItem(placement: .confirmationAction) {
                Button("Done", systemImage: "checkmark") { dismiss() }
            }
        }
    }
}

struct ExerciseEditor: View {
    @Environment(Store.self) private var store
    @Environment(\.dismiss) private var dismiss
    @Binding var exercise: Exercise
    @FocusState private var typing: Int?

    // Where the exercise just before this one sits in its routine, if there is one.
    private var above: (routine: Int, exercise: Int)? {
        for r in store.data.routines.indices {
            if let e = store.data.routines[r].exercises.firstIndex(where: { $0.id == exercise.id }), e > 0 { return (r, e - 1) }
        }
        return nil
    }

    private func joinCircuit() {
        guard let above else { return }
        let id = store.data.routines[above.routine].exercises[above.exercise].circuit ?? UUID()
        store.data.routines[above.routine].exercises[above.exercise].circuit = id
        exercise.circuit = id
        exercise.sets = store.data.routines[above.routine].exercises[above.exercise].sets
        exercise.rest = store.data.routines[above.routine].exercises[above.exercise].rest
    }

    var body: some View {
        Form {
            if exercise.catalogID != nil {
                Section {
                    ExerciseFigure(id: exercise.catalogID).frame(maxWidth: 220).frame(maxWidth: .infinity)
                }
                .listRowBackground(Color.clear)
            }
            Section {
                TextField("Name, e.g. Bench press", text: $exercise.name).focused($typing, equals: 0)
                if let last = store.data.log.last(where: { $0.exerciseID == exercise.id }) {
                    LabeledContent("Last workout", value: "\(last.target) · \(last.weight.formatted()) kg · \(last.date.formatted(date: .abbreviated, time: .omitted))")
                }
            }
            Section("Notes") {
                TextField("e.g. seat on 4, wide grip, slow on the way down",
                          text: Binding(get: { exercise.notes ?? "" }, set: { exercise.notes = $0.isEmpty ? nil : $0 }),
                          axis: .vertical)
                    .lineLimit(2...8)
                    .focused($typing, equals: 1)
            }
            Section(exercise.circuit == nil ? "Sets" : "In each round") {
                if exercise.circuit == nil {
                    Stepper("\(exercise.sets) sets", value: $exercise.sets, in: 1...20)
                }
                Toggle("Timed sets", isOn: Binding(get: { exercise.seconds > 0 }, set: { exercise.seconds = $0 ? 30 : 0 }))
                if exercise.seconds > 0 {
                    Stepper("\(clock(exercise.seconds)) per set", value: $exercise.seconds, in: 5...600, step: 5)
                } else {
                    Stepper("\(exercise.reps) reps per set", value: $exercise.reps, in: 1...100)
                }
            }
            Section("Weight") {
                HStack {
                    TextField("0", value: $exercise.weight, format: .number).keyboardType(.decimalPad).focused($typing, equals: 2)
                    Text("kg").foregroundStyle(.secondary)
                    Stepper("Weight", value: $exercise.weight, in: 0...500, step: 2.5).labelsHidden()
                }
            }
            if let circuit = exercise.circuit {
                Section {
                    Stepper("\(exercise.sets) rounds", value: Binding(get: { exercise.sets }, set: { sets in store.updateCircuit(circuit) { $0.sets = sets } }), in: 1...20)
                    Stepper("\(clock(exercise.rest)) rest after each round", value: Binding(get: { exercise.rest }, set: { rest in store.updateCircuit(circuit) { $0.rest = rest } }), in: 0...600, step: 15)
                    Button("Remove from the circuit", role: .destructive) { exercise.circuit = nil }
                } header: {
                    Text("Circuit")
                } footer: {
                    Text("The exercises of a circuit are done one after the other, then you rest. Rounds and rest are the same for all of them.")
                }
            } else {
                Section("Rest timer") {
                    Stepper("\(clock(exercise.rest)) between sets", value: $exercise.rest, in: 0...600, step: 15)
                }
                if above != nil {
                    Section {
                        Button("Make a circuit with the exercise above", systemImage: "arrow.triangle.2.circlepath") { joinCircuit() }
                    }
                }
            }
        }
        .navigationTitle(exercise.name.isEmpty ? "New exercise" : exercise.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("Done", systemImage: "checkmark") { dismiss() }
            }
            // The weight keypad has no return key, so it needs its own way to close.
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Done") { typing = nil }.bold()
            }
        }
    }
}
