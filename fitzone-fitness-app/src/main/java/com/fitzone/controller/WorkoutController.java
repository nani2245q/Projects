package com.fitzone.controller;

import com.fitzone.dto.WorkoutRequest;
import com.fitzone.model.User;
import com.fitzone.model.Workout;
import com.fitzone.repository.UserRepository;
import com.fitzone.service.WorkoutService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/workouts")
public class WorkoutController {

    private final WorkoutService workoutService;
    private final UserRepository userRepo;

    public WorkoutController(WorkoutService workoutService, UserRepository userRepo) {
        this.workoutService = workoutService;
        this.userRepo = userRepo;
    }

    // create a new workout
    @PostMapping
    public ResponseEntity<?> createWorkout(@AuthenticationPrincipal UserDetails userDetails, @RequestBody WorkoutRequest request) {
        Long userId = getUserId(userDetails);
        Workout workout = workoutService.createWorkout(userId, request);
        return ResponseEntity.ok(toResponse(workout));
    }

    // get all workouts for logged in user
    @GetMapping
    public ResponseEntity<?> getWorkouts(@AuthenticationPrincipal UserDetails userDetails) {
        Long userId = getUserId(userDetails);
        List<Map<String, Object>> workouts = workoutService.getUserWorkouts(userId)
                .stream().map(this::toResponse).collect(Collectors.toList());
        return ResponseEntity.ok(workouts);
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getWorkout(@PathVariable Long id) {
        return ResponseEntity.ok(toResponse(workoutService.getWorkout(id)));
    }

    // mark workout as done
    @PostMapping("/{id}/complete")
    public ResponseEntity<?> completeWorkout(@PathVariable Long id) {
        return ResponseEntity.ok(toResponse(workoutService.completeWorkout(id)));
    }

    // helper to get userId from the auth token
    private Long getUserId(UserDetails userDetails) {
        User user = userRepo.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));
        return user.getId();
    }

    // converts workout to a map for the response
    // TODO: maybe use a proper DTO for this later
    private Map<String, Object> toResponse(Workout w) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", w.getId());
        map.put("name", w.getName());
        map.put("notes", w.getNotes());
        map.put("status", w.getStatus());
        map.put("startedAt", w.getStartedAt());
        map.put("completedAt", w.getCompletedAt());
        map.put("durationMinutes", w.getDurationMinutes());
        map.put("caloriesBurned", w.getCaloriesBurned());
        map.put("exerciseCount", w.getExercises().size());
        map.put("createdAt", w.getCreatedAt());
        return map;
    }
}
