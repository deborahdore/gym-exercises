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
                        VStack(alignment: .leading, spacing: 2) {
                            Text(routine.name.isEmpty ? "New routine" : routine.name).font(.headline)
                            Text([routine.days, "\(routine.exercises.count) exercises"].filter { !$0.isEmpty }.joined(separator: " — "))
                                .font(.subheadline)
                                .foregroundStyle(routine.isToday ? Color.accentColor : Color.secondary)
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
    @Binding var routine: Routine

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
                    NavigationLink {
                        ExerciseEditor(exercise: $exercise)
                    } label: {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(exercise.name.isEmpty ? "New exercise" : exercise.name)
                            Text("\(exercise.target) · \(exercise.load) · rest \(clock(exercise.rest))")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }
                    }
                }
                .onDelete { routine.exercises.remove(atOffsets: $0) }
                .onMove { routine.exercises.move(fromOffsets: $0, toOffset: $1) }
                Button("Add exercise", systemImage: "plus") { routine.exercises.append(Exercise()) }
            }
        }
        .navigationTitle(routine.name.isEmpty ? "New routine" : routine.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar { EditButton() }
    }
}

struct ExerciseEditor: View {
    @Binding var exercise: Exercise

    var body: some View {
        Form {
            TextField("Name, e.g. Bench press", text: $exercise.name)
            Section("Sets") {
                Stepper("\(exercise.sets) sets", value: $exercise.sets, in: 1...20)
                Toggle("Timed sets", isOn: Binding(get: { exercise.seconds > 0 }, set: { exercise.seconds = $0 ? 30 : 0 }))
                if exercise.seconds > 0 {
                    Stepper("\(clock(exercise.seconds)) per set", value: $exercise.seconds, in: 5...600, step: 5)
                } else {
                    Stepper("\(exercise.reps) reps per set", value: $exercise.reps, in: 1...100)
                }
            }
            Section("Weight") {
                HStack {
                    TextField("0", value: $exercise.weight, format: .number).keyboardType(.decimalPad)
                    Text("kg").foregroundStyle(.secondary)
                    Stepper("Weight", value: $exercise.weight, in: 0...500, step: 2.5).labelsHidden()
                }
            }
            Section("Rest timer") {
                Stepper("\(clock(exercise.rest)) between sets", value: $exercise.rest, in: 0...600, step: 15)
            }
        }
        .navigationTitle(exercise.name.isEmpty ? "New exercise" : exercise.name)
        .navigationBarTitleDisplayMode(.inline)
    }
}
