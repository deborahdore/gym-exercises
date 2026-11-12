import SwiftUI

@main
struct GymLogWatchApp: App {
    @State private var store = Store()

    var body: some Scene {
        WindowGroup {
            NavigationStack {
                // Today's routines first.
                List(store.data.routines.filter(\.isToday) + store.data.routines.filter { !$0.isToday }) { routine in
                    NavigationLink {
                        WorkoutView(routine: routine)
                    } label: {
                        VStack(alignment: .leading) {
                            Text(routine.name).font(.headline)
                            Text(routine.isToday ? "Today · \(routine.exercises.count) exercises" : "\(routine.exercises.count) exercises")
                                .font(.footnote)
                                .foregroundStyle(routine.isToday ? Color.green : Color.secondary)
                        }
                    }
                    .disabled(routine.exercises.isEmpty)
                }
                .overlay {
                    if store.data.routines.isEmpty {
                        Text("Create a routine on your iPhone").multilineTextAlignment(.center).foregroundStyle(.secondary)
                    }
                }
                .navigationTitle("GymLog")
            }
            .environment(store)
        }
    }
}
