package com.fitzone.service;

import com.fitzone.dto.WorkoutRequest;
import com.fitzone.model.*;
import com.fitzone.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class WorkoutService {

    private final WorkoutRepository workoutRepo;
    private final ExerciseRepository exerciseRepo;
    private final UserRepository userRepo;

    public WorkoutService(WorkoutRepository workoutRepo, ExerciseRepository exerciseRepo, UserRepository userRepo) {
        this.workoutRepo = workoutRepo;
        this.exerciseRepo = exerciseRepo;
        this.userRepo = userRepo;
    }

    @Transactional
    public Workout createWorkout(Long userId, WorkoutRequest request) {
        User user = userRepo.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Workout workout = new Workout();
        workout.setUser(user);
        workout.setName(request.getName());
        workout.setNotes(request.getNotes());
        workout.setStartedAt(LocalDateTime.now());

        // add each exercise to the workout
        if (request.getExercises() != null) {
            for (int i = 0; i < request.getExercises().size(); i++) {
                WorkoutRequest.ExerciseEntry entry = request.getExercises().get(i);
                Exercise exercise = exerciseRepo.findById(entry.getExerciseId())
                        .orElseThrow(() -> new RuntimeException("Exercise not found"));

                WorkoutExercise we = new WorkoutExercise();
                we.setWorkout(workout);
                we.setExercise(exercise);
                we.setSets(entry.getSets());
                we.setReps(entry.getReps());
                we.setWeightKg(entry.getWeightKg());
                we.setDurationSeconds(entry.getDurationSeconds());
                we.setDistanceMeters(entry.getDistanceMeters());
                we.setNotes(entry.getNotes());
                we.setOrderIndex(i);

                // calculate calories if we have the data
                if (exercise.getCaloriesPerMinute() != null && entry.getDurationSeconds() != null) {
                    we.setCaloriesBurned(exercise.getCaloriesPerMinute() * (entry.getDurationSeconds() / 60.0));
                }

                workout.getExercises().add(we);
            }
        }

        return workoutRepo.save(workout);
    }

    public List<Workout> getUserWorkouts(Long userId) {
        return workoutRepo.findByUserIdOrderByCreatedAtDesc(userId);
    }

    public Workout getWorkout(Long id) {
        return workoutRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Workout not found"));
    }

    // marks a workout as completed and calculates total stats
    @Transactional
    public Workout completeWorkout(Long workoutId) {
        Workout workout = getWorkout(workoutId);
        workout.setStatus(Workout.Status.COMPLETED);
        workout.setCompletedAt(LocalDateTime.now());

        // figure out how long the workout took
        if (workout.getStartedAt() != null) {
            long mins = java.time.Duration.between(workout.getStartedAt(), workout.getCompletedAt()).toMinutes();
            workout.setDurationMinutes((int) mins);
        }

        // add up all the calories from each exercise
        double totalCals = workout.getExercises().stream()
                .mapToDouble(we -> we.getCaloriesBurned() != null ? we.getCaloriesBurned() : 0)
                .sum();
        workout.setCaloriesBurned(totalCals);

        return workoutRepo.save(workout);
    }

    public List<Workout> getWorkoutsByDateRange(Long userId, LocalDateTime start, LocalDateTime end) {
        return workoutRepo.findByUserIdAndDateRange(userId, start, end);
    }
}
