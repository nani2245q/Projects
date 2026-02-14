package com.fitzone.service;

import com.fitzone.model.ActivityLog;
import com.fitzone.model.User;
import com.fitzone.repository.ActivityLogRepository;
import com.fitzone.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class ActivityLogService {

    private final ActivityLogRepository activityLogRepo;
    private final UserRepository userRepo;

    public ActivityLogService(ActivityLogRepository activityLogRepo, UserRepository userRepo) {
        this.activityLogRepo = activityLogRepo;
        this.userRepo = userRepo;
    }

    public ActivityLog logActivity(Long userId, ActivityLog log) {
        User user = userRepo.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        log.setUser(user);

        // default to today if no date given
        if (log.getLogDate() == null) {
            log.setLogDate(LocalDate.now());
        }

        return activityLogRepo.save(log);
    }

    public List<ActivityLog> getUserLogs(Long userId) {
        return activityLogRepo.findByUserIdOrderByLogDateDesc(userId);
    }

    public ActivityLog getLogByDate(Long userId, LocalDate date) {
        return activityLogRepo.findByUserIdAndLogDate(userId, date)
                .orElse(null);
    }

    public List<ActivityLog> getLogsByDateRange(Long userId, LocalDate start, LocalDate end) {
        return activityLogRepo.findByUserIdAndDateRange(userId, start, end);
    }

    // update individual fields if they're provided
    // TODO: add validation later
    public ActivityLog updateLog(Long logId, ActivityLog updates) {
        ActivityLog log = activityLogRepo.findById(logId)
                .orElseThrow(() -> new RuntimeException("Activity log not found"));

        if (updates.getSteps() != null) log.setSteps(updates.getSteps());
        if (updates.getCaloriesConsumed() != null) log.setCaloriesConsumed(updates.getCaloriesConsumed());
        if (updates.getCaloriesBurned() != null) log.setCaloriesBurned(updates.getCaloriesBurned());
        if (updates.getWaterMl() != null) log.setWaterMl(updates.getWaterMl());
        if (updates.getSleepHours() != null) log.setSleepHours(updates.getSleepHours());
        if (updates.getWeightKg() != null) log.setWeightKg(updates.getWeightKg());
        if (updates.getMood() != null) log.setMood(updates.getMood());
        if (updates.getNotes() != null) log.setNotes(updates.getNotes());

        return activityLogRepo.save(log);
    }
}
