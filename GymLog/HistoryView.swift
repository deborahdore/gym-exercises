import Charts
import SwiftUI

struct HistoryView: View {
    @Environment(Store.self) private var store

    var body: some View {
        // One row per exercise, most recently trained first.
        let groups = Dictionary(grouping: store.data.log.sorted { $0.date < $1.date }, by: \.exerciseID).values
            .sorted { $0.last!.date > $1.last!.date }
        let figures = Dictionary(store.data.routines.flatMap(\.exercises).map { ($0.id, $0.catalogID) }, uniquingKeysWith: { first, _ in first })
        NavigationStack {
            List(groups, id: \.first!.exerciseID) { entries in
                let gain = entries.last!.weight - entries.first!.weight
                NavigationLink {
                    ExerciseHistory(entries: entries)
                } label: {
                    HStack(spacing: 12) {
                        ExerciseFigure(id: figures[entries.last!.exerciseID] ?? nil).frame(width: 52)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(entries.last!.name)
                            Text("\(entries.first!.weight.formatted()) → \(entries.last!.weight.formatted()) kg · \(entries.count) sessions")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }
                        Spacer()
                        if gain != 0 {
                            Text("\(gain > 0 ? "+" : "")\(gain.formatted()) kg")
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(gain > 0 ? Color.green : Color.secondary)
                        }
                    }
                }
            }
            .overlay {
                if groups.isEmpty {
                    ContentUnavailableView("No workouts yet", systemImage: "chart.line.uptrend.xyaxis", description: Text("Finish an exercise on your Apple Watch and it shows up here."))
                }
            }
            .navigationTitle("Progress")
        }
    }
}

struct ExerciseHistory: View {
    let entries: [LogEntry]

    var body: some View {
        List {
            Chart(entries) {
                LineMark(x: .value("Date", $0.date), y: .value("kg", $0.weight))
                PointMark(x: .value("Date", $0.date), y: .value("kg", $0.weight))
            }
            .chartYScale(domain: .automatic(includesZero: false))
            .frame(height: 220)
            .padding(.vertical)
            ForEach(entries.reversed()) { entry in
                LabeledContent(entry.date.formatted(date: .abbreviated, time: .omitted), value: "\(entry.target) · \(entry.weight.formatted()) kg")
            }
        }
        .navigationTitle(entries.last?.name ?? "")
        .navigationBarTitleDisplayMode(.inline)
    }
}
