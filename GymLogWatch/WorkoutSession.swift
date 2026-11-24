import HealthKit

// A HealthKit workout session keeps the app running (and in front on wrist raise) for the
// whole workout, so the rest timer still buzzes with the wrist down. It also saves the
// workout to Health. If it cannot start, the app works the same but only buzzes while on screen.
final class WorkoutSession {
    private let health = HKHealthStore()
    private var session: HKWorkoutSession?
    private var builder: HKLiveWorkoutBuilder?

    func start() async {
        guard HKHealthStore.isHealthDataAvailable(), session == nil else { return }
        let configuration = HKWorkoutConfiguration()
        configuration.activityType = .traditionalStrengthTraining
        configuration.locationType = .indoor
        do {
            // The builder only saves the samples it may write: without these the workout lands in
            // Fitness with no calories or heart rate.
            let samples: Set<HKSampleType> = [HKQuantityType(.activeEnergyBurned), HKQuantityType(.basalEnergyBurned), HKQuantityType(.heartRate)]
            try await health.requestAuthorization(toShare: samples.union([HKObjectType.workoutType()]), read: samples)
            let session = try HKWorkoutSession(healthStore: health, configuration: configuration)
            let builder = session.associatedWorkoutBuilder()
            builder.dataSource = HKLiveWorkoutDataSource(healthStore: health, workoutConfiguration: configuration)
            self.session = session
            self.builder = builder
            session.startActivity(with: .now)
            try await builder.beginCollection(at: .now)
        } catch {
            print("Workout session unavailable:", error)
        }
    }

    func stop() async {
        guard let session, let builder else { return }
        self.session = nil
        self.builder = nil
        session.end()
        do {
            try await builder.endCollection(at: .now)
            try await builder.finishWorkout()
        } catch {
            print("Workout not saved:", error)
        }
    }
}
