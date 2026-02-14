package com.fitzone.repository;

import com.fitzone.model.ActivityLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface ActivityLogRepository extends JpaRepository<ActivityLog, Long> {
    List<ActivityLog> findByUserIdOrderByLogDateDesc(Long userId);

    Optional<ActivityLog> findByUserIdAndLogDate(Long userId, LocalDate date);

    @Query("SELECT a FROM ActivityLog a WHERE a.user.id = :userId AND a.logDate BETWEEN :start AND :end ORDER BY a.logDate")
    List<ActivityLog> findByUserIdAndDateRange(@Param("userId") Long userId, @Param("start") LocalDate start, @Param("end") LocalDate end);

    @Query("SELECT COALESCE(AVG(a.steps), 0) FROM ActivityLog a WHERE a.user.id = :userId")
    Double avgStepsByUserId(@Param("userId") Long userId);

    @Query("SELECT COALESCE(AVG(a.sleepHours), 0) FROM ActivityLog a WHERE a.user.id = :userId")
    Double avgSleepByUserId(@Param("userId") Long userId);
}
