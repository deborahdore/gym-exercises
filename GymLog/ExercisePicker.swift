import SwiftUI

// Pick one or more exercises from the catalog: search, filter by muscle and by equipment.
// Selecting an exercise downloads its figure.
struct ExercisePicker: View {
    @Environment(Store.self) private var store
    @Environment(\.dismiss) private var dismiss
    let add: ([Exercise]) -> Void

    @State private var search = ""
    @State private var muscle = "All"
    @State private var kind = "All"
    @State private var picked: [Exercise] = []

    // Exercises already planned in a routine keep their sets, weight and rest when reused.
    private var mine: [String: Exercise] {
        var mine: [String: Exercise] = [:]
        for exercise in store.data.routines.flatMap(\.exercises) {
            if let id = exercise.catalogID, mine[id] == nil { mine[id] = exercise }
        }
        return mine
    }

    private var shown: [CatalogExercise] {
        catalog.filter {
            (search.isEmpty || $0.name.localizedCaseInsensitiveContains(search))
                && (muscle == "All" || $0.muscle == muscle)
                && (kind == "All" || $0.kind == kind)
        }
    }

    var body: some View {
        let mine = mine
        let shown = shown
        NavigationStack {
            List {
                ForEach(muscles, id: \.self) { group in
                    let items = shown.filter { $0.muscle == group }
                    if !items.isEmpty {
                        Section(group) {
                            ForEach(items) { row($0, mine[$0.id]) }
                        }
                    }
                }
                Section {
                    Button(search.isEmpty ? "Create a custom exercise" : "Create “\(search)”", systemImage: "plus") {
                        add(picked + [Exercise(name: search)])
                        dismiss()
                    }
                } footer: {
                    Text("Custom exercises have no figure.")
                }
            }
            .searchable(text: $search, placement: .navigationBarDrawer(displayMode: .always), prompt: "Search exercises")
            .safeAreaInset(edge: .top, spacing: 0) { filters }
            .navigationTitle("Add exercises")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Cancel") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button(picked.isEmpty ? "Add" : "Add \(picked.count)") {
                        add(picked)
                        dismiss()
                    }
                    .disabled(picked.isEmpty)
                }
            }
        }
    }

    private var filters: some View {
        VStack(spacing: 10) {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(["All"] + muscles, id: \.self) { name in
                        Button { muscle = name } label: {
                            Text(name)
                                .font(.subheadline.weight(.medium))
                                .padding(.horizontal, 14)
                                .frame(minHeight: 36)
                                .background(muscle == name ? Color.accentColor : Color(.tertiarySystemFill), in: Capsule())
                                .foregroundStyle(muscle == name ? Color.white : Color.primary)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal)
            }
            Picker("Equipment", selection: $kind) {
                ForEach(["All", "Machines", "Free weights", "Bodyweight"], id: \.self) { Text($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
        }
        .padding(.vertical, 10)
        .background(.bar)
    }

    private func row(_ item: CatalogExercise, _ planned: Exercise?) -> some View {
        let on = picked.contains { $0.catalogID == item.id }
        return Button {
            if on {
                picked.removeAll { $0.catalogID == item.id }
            } else {
                var exercise = planned ?? item.exercise
                exercise.id = UUID()
                picked.append(exercise)
            }
        } label: {
            HStack(spacing: 12) {
                ExerciseFigure(id: item.id, download: on).frame(width: 52)
                VStack(alignment: .leading, spacing: 2) {
                    Text(item.name).foregroundStyle(Color.primary)
                    Text(planned.map { "\(item.equipment) · in your routines, \($0.load)" } ?? item.equipment)
                        .font(.subheadline).foregroundStyle(Color.secondary)
                }
                Spacer()
                Image(systemName: on ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .foregroundStyle(on ? Color.accentColor : Color.secondary)
            }
        }
        .accessibilityAddTraits(on ? .isSelected : [])
    }
}
