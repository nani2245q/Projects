package com.fitzone.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;

@Entity
@Table(name = "exercises")
public class Exercise {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    private String name;

    private String description;

    @Enumerated(EnumType.STRING)
    @Column(name = "muscle_group")
    private MuscleGroup muscleGroup;

    @Enumerated(EnumType.STRING)
    private Category category;

    @Column(name = "calories_per_minute")
    private Double caloriesPerMinute;

    private String difficulty;

    public enum MuscleGroup {
        CHEST, BACK, SHOULDERS, ARMS, LEGS, CORE, FULL_BODY, CARDIO
    }

    public enum Category {
        STRENGTH, CARDIO, FLEXIBILITY, BALANCE, HIIT
    }

    public Exercise() {}

    public Exercise(String name, MuscleGroup muscleGroup, Category category) {
        this.name = name;
        this.muscleGroup = muscleGroup;
        this.category = category;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public MuscleGroup getMuscleGroup() { return muscleGroup; }
    public void setMuscleGroup(MuscleGroup muscleGroup) { this.muscleGroup = muscleGroup; }
    public Category getCategory() { return category; }
    public void setCategory(Category category) { this.category = category; }
    public Double getCaloriesPerMinute() { return caloriesPerMinute; }
    public void setCaloriesPerMinute(Double caloriesPerMinute) { this.caloriesPerMinute = caloriesPerMinute; }
    public String getDifficulty() { return difficulty; }
    public void setDifficulty(String difficulty) { this.difficulty = difficulty; }
}
