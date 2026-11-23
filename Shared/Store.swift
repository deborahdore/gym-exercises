import Foundation
import Observation
import WatchConnectivity

// The iPhone owns the routines and the history. It pushes routines to the watch as the
// application context (latest state wins); the watch sends back one LogEntry per finished
// exercise, and any exercise edited on the watch, with transferUserInfo, which is queued
// until the phone is reachable again.
@Observable
final class Store: NSObject, WCSessionDelegate {
    var data = GymData()

    @ObservationIgnored private let url = URL.documentsDirectory.appending(path: "gym.json")

    override init() {
        super.init()
        if let saved = try? Data(contentsOf: url), let decoded = try? JSONDecoder().decode(GymData.self, from: saved) {
            data = decoded
        }
        if WCSession.isSupported() {
            WCSession.default.delegate = self
            WCSession.default.activate()
        }
    }

    func save() {
        try? JSONEncoder().encode(data).write(to: url, options: .atomic)
        #if os(iOS)
        push()
        #endif
    }

    func record(_ entry: LogEntry) {
        guard !data.log.contains(where: { $0.id == entry.id }) else { return }
        for r in data.routines.indices {
            for e in data.routines[r].exercises.indices where data.routines[r].exercises[e].id == entry.exerciseID {
                data.routines[r].exercises[e].weight = entry.next
            }
        }
        #if os(iOS)
        data.log.append(entry)
        #else
        if let encoded = try? JSONEncoder().encode(entry) {
            WCSession.default.transferUserInfo(["entry": encoded])
        }
        #endif
        save()
    }

    // An exercise edited on either device. The watch also sends it to the phone, which then
    // pushes the routines back as the new application context.
    func update(_ exercise: Exercise) {
        for r in data.routines.indices {
            for e in data.routines[r].exercises.indices where data.routines[r].exercises[e].id == exercise.id {
                data.routines[r].exercises[e] = exercise
            }
        }
        #if os(watchOS)
        if let encoded = try? JSONEncoder().encode(exercise) {
            WCSession.default.transferUserInfo(["exercise": encoded])
        }
        #endif
        save()
    }

    // The exercises of a circuit share the rounds and the rest, so these are changed on all of them.
    func updateCircuit(_ id: UUID, _ change: (inout Exercise) -> Void) {
        for r in data.routines.indices {
            for e in data.routines[r].exercises.indices where data.routines[r].exercises[e].circuit == id {
                change(&data.routines[r].exercises[e])
            }
        }
    }

    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        if let error { print("WatchConnectivity activation failed:", error) }
        DispatchQueue.main.async {
            #if os(iOS)
            self.push()
            #else
            self.receive(session.receivedApplicationContext)
            self.refresh()
            #endif
        }
    }

    #if os(iOS)
    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) { session.activate() }

    func session(_ session: WCSession, didReceiveUserInfo userInfo: [String: Any] = [:]) {
        if let encoded = userInfo["entry"] as? Data, let entry = try? JSONDecoder().decode(LogEntry.self, from: encoded) {
            DispatchQueue.main.async { self.record(entry) }
        } else if let encoded = userInfo["exercise"] as? Data, let exercise = try? JSONDecoder().decode(Exercise.self, from: encoded) {
            DispatchQueue.main.async { self.update(exercise) }
        }
    }

    // The context cannot be set while the watch app is missing, so the routines are pushed
    // again when it gets installed (or a watch is paired) while the phone app is running.
    func sessionWatchStateDidChange(_ session: WCSession) {
        DispatchQueue.main.async { self.push() }
    }

    private func push() {
        let session = WCSession.default
        guard session.activationState == .activated, session.isWatchAppInstalled else { return }
        do {
            try session.updateApplicationContext(context())
        } catch {
            print("Could not send routines to the watch:", error)
        }
    }

    // The watch asks for the routines when its app opens (see refresh()), so it does not depend
    // on when the system gets round to delivering the application context.
    func session(_ session: WCSession, didReceiveMessage message: [String: Any], replyHandler: @escaping ([String: Any]) -> Void) {
        DispatchQueue.main.async { replyHandler(self.context()) }
    }

    private func context() -> [String: Any] {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .sortedKeys   // stable bytes, so the watch can tell an unchanged context apart
        guard let routines = try? encoder.encode(data.routines) else { return [:] }
        return ["routines": routines]
    }
    #else
    func session(_ session: WCSession, didReceiveApplicationContext applicationContext: [String: Any]) {
        DispatchQueue.main.async { self.receive(applicationContext) }
    }

    func sessionReachabilityDidChange(_ session: WCSession) {
        DispatchQueue.main.async { self.refresh() }
    }

    // Asks the phone for its current routines; it answers even when its app is in the background.
    func refresh() {
        let session = WCSession.default
        guard session.activationState == .activated, session.isReachable else { return }
        session.sendMessage(["want": "routines"], replyHandler: { reply in
            DispatchQueue.main.async { self.receive(reply) }
        }, errorHandler: { print("Could not ask the phone for routines:", $0) })
    }

    // A context already applied is skipped, so a weight changed on the watch is not
    // reverted by the phone's older copy while the log entry is still in transit.
    private func receive(_ context: [String: Any]) {
        guard let encoded = context["routines"] as? Data, encoded != UserDefaults.standard.data(forKey: "applied"),
              let routines = try? JSONDecoder().decode([Routine].self, from: encoded) else { return }
        UserDefaults.standard.set(encoded, forKey: "applied")
        data.routines = routines
        save()
    }
    #endif
}
