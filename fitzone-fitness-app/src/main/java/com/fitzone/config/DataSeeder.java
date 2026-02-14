package com.fitzone.config;

import com.fitzone.model.*;
import com.fitzone.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Random;

// puts some sample data in the database so the app isn't empty on startup
@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner seedDatabase(UserRepository userRepo, ExerciseRepository exerciseRepo,
                                   WorkoutRepository workoutRepo, ActivityLogRepository activityRepo,
                                   PasswordEncoder passwordEncoder) {
        return args -> {
            // don't re-seed if data already exists
            if (userRepo.count() > 0) return;

            Random rand = new Random(42);

            // --- create some test users ---
            User admin = new User("Admin", "admin@fitzone.com", passwordEncoder.encode("admin123"));
            admin.setRole(User.Role.ADMIN);
            admin.setFitnessGoal("Maintain overall fitness");
            admin.setHeight(180.0);
            admin.setWeight(80.0);
            admin = userRepo.save(admin);

            User user1 = new User("John Doe", "john@test.com", passwordEncoder.encode("password123"));
            user1.setFitnessGoal("Build muscle");
            user1.setHeight(175.0);
            user1.setWeight(75.0);
            user1 = userRepo.save(user1);

            User user2 = new User("Jane Smith", "jane@test.com", passwordEncoder.encode("password123"));
            user2.setFitnessGoal("Lose weight");
            user2.setHeight(165.0);
            user2.setWeight(65.0);
            user2 = userRepo.save(user2);

            System.out.println("Seeded 3 users (admin@fitzone.com / admin123)");

            // bunch of exercises to populate the exercise library
            List<Exercise> exercises = List.of(
                createExercise("Bench Press", "Flat barbell bench press", Exercise.MuscleGroup.CHEST, Exercise.Category.STRENGTH, 8.0, "Intermediate"),
                createExercise("Push-ups", "Standard push-ups", Exercise.MuscleGroup.CHEST, Exercise.Category.STRENGTH, 7.0, "Beginner"),
                createExercise("Deadlift", "Conventional deadlift", Exercise.MuscleGroup.BACK, Exercise.Category.STRENGTH, 10.0, "Advanced"),
                createExercise("Pull-ups", "Bodyweight pull-ups", Exercise.MuscleGroup.BACK, Exercise.Category.STRENGTH, 8.0, "Intermediate"),
                createExercise("Lat Pulldown", "Cable lat pulldown", Exercise.MuscleGroup.BACK, Exercise.Category.STRENGTH, 6.0, "Beginner"),
                createExercise("Overhead Press", "Standing barbell press", Exercise.MuscleGroup.SHOULDERS, Exercise.Category.STRENGTH, 7.0, "Intermediate"),
                createExercise("Lateral Raises", "Dumbbell lateral raises", Exercise.MuscleGroup.SHOULDERS, Exercise.Category.STRENGTH, 5.0, "Beginner"),
                createExercise("Bicep Curls", "Dumbbell bicep curls", Exercise.MuscleGroup.ARMS, Exercise.Category.STRENGTH, 5.0, "Beginner"),
                createExercise("Tricep Dips", "Parallel bar dips", Exercise.MuscleGroup.ARMS, Exercise.Category.STRENGTH, 6.0, "Intermediate"),
                createExercise("Squats", "Barbell back squats", Exercise.MuscleGroup.LEGS, Exercise.Category.STRENGTH, 10.0, "Intermediate"),
                createExercise("Lunges", "Walking lunges", Exercise.MuscleGroup.LEGS, Exercise.Category.STRENGTH, 7.0, "Beginner"),
                createExercise("Leg Press", "Machine leg press", Exercise.MuscleGroup.LEGS, Exercise.Category.STRENGTH, 8.0, "Beginner"),
                createExercise("Plank", "Standard plank hold", Exercise.MuscleGroup.CORE, Exercise.Category.STRENGTH, 4.0, "Beginner"),
                createExercise("Crunches", "Standard crunches", Exercise.MuscleGroup.CORE, Exercise.Category.STRENGTH, 5.0, "Beginner"),
                createExercise("Running", "Treadmill or outdoor running", Exercise.MuscleGroup.CARDIO, Exercise.Category.CARDIO, 12.0, "Beginner"),
                createExercise("Cycling", "Stationary bike cycling", Exercise.MuscleGroup.CARDIO, Exercise.Category.CARDIO, 10.0, "Beginner"),
                createExercise("Jump Rope", "Speed rope skipping", Exercise.MuscleGroup.FULL_BODY, Exercise.Category.CARDIO, 14.0, "Intermediate"),
                createExercise("Burpees", "Full burpees with jump", Exercise.MuscleGroup.FULL_BODY, Exercise.Category.HIIT, 12.0, "Advanced"),
                createExercise("Mountain Climbers", "Fast mountain climbers", Exercise.MuscleGroup.FULL_BODY, Exercise.Category.HIIT, 11.0, "Intermediate"),
                createExercise("Yoga Flow", "Sun salutation sequence", Exercise.MuscleGroup.FULL_BODY, Exercise.Category.FLEXIBILITY, 4.0, "Beginner")
            );
            List<Exercise> savedExercises = exerciseRepo.saveAll(exercises);
            System.out.println("Seeded " + savedExercises.size() + " exercises");

            // generate some fake workouts for both users
            for (User user : List.of(user1, user2)) {
                for (int w = 0; w < 8; w++) {
                    Workout workout = new Workout();
                    workout.setUser(user);
                    workout.setName(w % 2 == 0 ? "Upper Body Day" : "Lower Body Day");
                    workout.setStartedAt(LocalDateTime.now().minusDays(w * 2));
                    workout.setCompletedAt(workout.getStartedAt().plusMinutes(45 + rand.nextInt(30)));
                    workout.setDurationMinutes(45 + rand.nextInt(30));
                    workout.setStatus(Workout.Status.COMPLETED);

                    double totalCal = 0;
                    int exCount = 3 + rand.nextInt(3); // 3-5 exercises per workout
                    for (int e = 0; e < exCount; e++) {
                        Exercise ex = savedExercises.get(rand.nextInt(savedExercises.size()));
                        WorkoutExercise we = new WorkoutExercise();
                        we.setWorkout(workout);
                        we.setExercise(ex);
                        we.setSets(3 + rand.nextInt(3));
                        we.setReps(8 + rand.nextInt(8));
                        we.setWeightKg(20.0 + rand.nextInt(60));
                        we.setDurationSeconds(120 + rand.nextInt(300));
                        double cal = ex.getCaloriesPerMinute() * (we.getDurationSeconds() / 60.0);
                        we.setCaloriesBurned(Math.round(cal * 10) / 10.0);
                        we.setOrderIndex(e);
                        totalCal += cal;
                        workout.getExercises().add(we);
                    }
                    workout.setCaloriesBurned(Math.round(totalCal * 10) / 10.0);
                    workoutRepo.save(workout);
                }

                // activity logs for the past 2 weeks
                for (int d = 0; d < 14; d++) {
                    ActivityLog log = new ActivityLog();
                    log.setUser(user);
                    log.setLogDate(LocalDate.now().minusDays(d));
                    log.setSteps(4000 + rand.nextInt(10000));
                    log.setCaloriesConsumed(1800 + rand.nextInt(800));
                    log.setCaloriesBurned(200.0 + rand.nextInt(500));
                    log.setWaterMl(1500 + rand.nextInt(2000));
                    log.setSleepHours(5.5 + rand.nextDouble() * 3.0);
                    log.setWeightKg(user.getWeight() - 0.5 + rand.nextDouble());
                    String[] moods = {"great", "good", "okay", "tired", "energized"};
                    log.setMood(moods[rand.nextInt(moods.length)]);
                    activityRepo.save(log);
                }
            }

            System.out.println("Seeded workouts and activity logs for 2 users");
            System.out.println("FitZone database seeding complete!");
        };
    }

    // helper to make exercise creation less repetitive
    private Exercise createExercise(String name, String desc, Exercise.MuscleGroup mg, Exercise.Category cat, double calPerMin, String diff) {
        Exercise e = new Exercise(name, mg, cat);
        e.setDescription(desc);
        e.setCaloriesPerMinute(calPerMin);
        e.setDifficulty(diff);
        return e;
    }
}
