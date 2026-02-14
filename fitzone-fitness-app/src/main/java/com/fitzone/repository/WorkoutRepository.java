package com.fitzone.repository;

import com.fitzone.model.Workout;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;
import java.util.List;

public interface WorkoutRepository extends JpaRepository<Workout, Long> {
    List<Workout> findByUserIdOrderByCreatedAtDesc(Long userId);

    List<Workout> findByUserIdAndStatus(Long userId, Workout.Status status);

    @Query("SELECT w FROM Workout w WHERE w.user.id = :userId AND w.createdAt BETWEEN :start AND :end ORDER BY w.createdAt DESC")
    List<Workout> findByUserIdAndDateRange(@Param("userId") Long userId, @Param("start") LocalDateTime start, @Param("end") LocalDateTime end);

    @Query("SELECT COUNT(w) FROM Workout w WHERE w.user.id = :userId AND w.status = 'COMPLETED'")
    Long countCompletedByUserId(@Param("userId") Long userId);

    @Query("SELECT COALESCE(SUM(w.caloriesBurned), 0) FROM Workout w WHERE w.user.id = :userId AND w.status = 'COMPLETED'")
    Double totalCaloriesBurnedByUserId(@Param("userId") Long userId);
}
