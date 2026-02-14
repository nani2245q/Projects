package com.fitzone.dto;

import java.util.List;

public class WorkoutRequest {
    private String name;
    private String notes;
    private List<ExerciseEntry> exercises;

    public static class ExerciseEntry {
        private Long exerciseId;
        private Integer sets;
        private Integer reps;
        private Double weightKg;
        private Integer durationSeconds;
        private Double distanceMeters;
        private String notes;

        public Long getExerciseId() { return exerciseId; }
        public void setExerciseId(Long exerciseId) { this.exerciseId = exerciseId; }
        public Integer getSets() { return sets; }
        public void setSets(Integer sets) { this.sets = sets; }
        public Integer getReps() { return reps; }
        public void setReps(Integer reps) { this.reps = reps; }
        public Double getWeightKg() { return weightKg; }
        public void setWeightKg(Double weightKg) { this.weightKg = weightKg; }
        public Integer getDurationSeconds() { return durationSeconds; }
        public void setDurationSeconds(Integer durationSeconds) { this.durationSeconds = durationSeconds; }
        public Double getDistanceMeters() { return distanceMeters; }
        public void setDistanceMeters(Double distanceMeters) { this.distanceMeters = distanceMeters; }
        public String getNotes() { return notes; }
        public void setNotes(String notes) { this.notes = notes; }
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
    public List<ExerciseEntry> getExercises() { return exercises; }
    public void setExercises(List<ExerciseEntry> exercises) { this.exercises = exercises; }
}
