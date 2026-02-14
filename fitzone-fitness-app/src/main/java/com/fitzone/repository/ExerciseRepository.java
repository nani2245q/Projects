package com.fitzone.repository;

import com.fitzone.model.Exercise;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ExerciseRepository extends JpaRepository<Exercise, Long> {
    List<Exercise> findByMuscleGroup(Exercise.MuscleGroup muscleGroup);
    List<Exercise> findByCategory(Exercise.Category category);
    List<Exercise> findByNameContainingIgnoreCase(String name);
}
