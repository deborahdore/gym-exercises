import SwiftUI
import WidgetKit

// Watch-face complication / Smart Stack widget: one tap opens the workout.
struct GymEntry: TimelineEntry {
    let date = Date()
}

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> GymEntry { GymEntry() }
    func getSnapshot(in context: Context, completion: @escaping (GymEntry) -> Void) { completion(GymEntry()) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<GymEntry>) -> Void) {
        completion(Timeline(entries: [GymEntry()], policy: .never))
    }
}

struct GymWidgetView: View {
    @Environment(\.widgetFamily) private var family

    var body: some View {
        switch family {
        case .accessoryInline, .accessoryRectangular:
            Label("Start workout", systemImage: "dumbbell.fill")
        default:
            ZStack {
                AccessoryWidgetBackground()
                Image(systemName: "dumbbell.fill")
            }
        }
    }
}

@main
struct GymLogWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "GymLogWidget", provider: Provider()) { _ in
            GymWidgetView().containerBackground(.clear, for: .widget)
        }
        .configurationDisplayName("GymLog")
        .description("Open your workout.")
        .supportedFamilies([.accessoryCircular, .accessoryCorner, .accessoryInline, .accessoryRectangular])
    }
}
