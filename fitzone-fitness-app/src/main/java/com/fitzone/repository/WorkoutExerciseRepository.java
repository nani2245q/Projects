package com.fitzone.repository;

import com.fitzone.model.WorkoutExercise;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface WorkoutExerciseRepository extends JpaRepository<WorkoutExercise, Long> {
    List<WorkoutExercise> findByWorkoutIdOrderByOrderIndex(Long workoutId);
}
