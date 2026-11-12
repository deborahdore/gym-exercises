import SwiftUI

@main
struct GymLogApp: App {
    @State private var store = Store()

    var body: some Scene {
        WindowGroup {
            TabView {
                RoutinesView().tabItem { Label("Routines", systemImage: "dumbbell") }
                HistoryView().tabItem { Label("Progress", systemImage: "chart.line.uptrend.xyaxis") }
            }
            .environment(store)
            .onChange(of: store.data.routines) { store.save() }
        }
    }
}
