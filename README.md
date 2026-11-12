# GymLog

iPhone app to plan gym routines and track weight progress, with a standalone Apple Watch
app to run the workout (phone stays in the locker) and a programmable rest timer.

## Design

- **iPhone** (`GymLog/`): create routines, assign weekdays, and for each exercise set
  sets, reps (or seconds for timed sets), weight and rest time. The Progress tab charts the
  weight lifted per exercise over time.
- **Exercise catalog** (`Shared/Catalog.swift`, `catalog/`): "Add exercises" opens a searchable
  list of 48 common exercises, filtered by muscle group and by equipment (machines, free
  weights, bodyweight); several can be added at once, and custom ones are still possible.
  Only the names ship with the app. Each exercise has a small figure in `catalog/images`,
  which the app downloads from this repository (raw.githubusercontent.com, so the repository
  must be public) the first time the figure is shown, and then keeps on the device.
  The figures are drawn by `python3 catalog/figures.py` (needs Pillow); to add an exercise,
  add a pose there and a line in `Catalog.swift` with the same id.
- **Apple Watch** (`GymLogWatch/`): pick a routine (today's is listed first), then for each
  exercise it shows set number, reps and weight. "Set done" starts the rest countdown
  programmed for that exercise (+15 s / Skip), a haptic marks the end and the next set
  appears. After the last set you choose the weight for next time (Digital Crown ±0.5 kg,
  buttons ±2.5 kg). The list button jumps to another exercise if a machine is taken.
- **Complication** (`GymLogWidget/`): watch-face / Smart Stack shortcut that opens the app.
- **Sync** (`Shared/Store.swift`): WatchConnectivity, no account or server. The phone owns
  routines and history; the watch keeps its own copy, so it works with no phone nearby and
  sends finished exercises back when the phone is reachable again.
- The watch runs a HealthKit strength-training session during a workout. This keeps the
  app alive with the wrist down, so the timer still buzzes, and saves the workout to Health.

## Build

Needs Xcode 15+ (iOS 17, watchOS 10).

    brew install xcodegen
    xcodegen
    open GymLog.xcodeproj

Set your Team ID as `DEVELOPMENT_TEAM` in `project.yml` (or pick the team for the three
targets in Signing & Capabilities), then run the `GymLog` scheme on your iPhone; the watch
app installs with it. A free Apple ID works, but apps then expire after 7 days.
