package com.fitzone.controller;

import com.fitzone.model.Exercise;
import com.fitzone.repository.ExerciseRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

// exercise endpoints - mostly just reading from the DB
@RestController
@RequestMapping("/api/exercises")
public class ExerciseController {

    private final ExerciseRepository exerciseRepo;

    public ExerciseController(ExerciseRepository exerciseRepo) {
        this.exerciseRepo = exerciseRepo;
    }

    // get all exercises
    @GetMapping
    public ResponseEntity<List<Exercise>> getAll() {
        return ResponseEntity.ok(exerciseRepo.findAll());
    }

    @GetMapping("/muscle-group/{group}")
    public ResponseEntity<List<Exercise>> getByMuscleGroup(@PathVariable String group) {
        Exercise.MuscleGroup mg = Exercise.MuscleGroup.valueOf(group.toUpperCase());
        return ResponseEntity.ok(exerciseRepo.findByMuscleGroup(mg));
    }

    @GetMapping("/category/{category}")
    public ResponseEntity<List<Exercise>> getByCategory(@PathVariable String category) {
        Exercise.Category cat = Exercise.Category.valueOf(category.toUpperCase());
        return ResponseEntity.ok(exerciseRepo.findByCategory(cat));
    }

    // search by name
    @GetMapping("/search")
    public ResponseEntity<List<Exercise>> search(@RequestParam String q) {
        return ResponseEntity.ok(exerciseRepo.findByNameContainingIgnoreCase(q));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Exercise> getById(@PathVariable Long id) {
        return exerciseRepo.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
