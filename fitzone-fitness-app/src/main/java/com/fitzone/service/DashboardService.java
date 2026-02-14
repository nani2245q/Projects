package com.fitzone.service;

import com.fitzone.dto.DashboardResponse;
import com.fitzone.model.ActivityLog;
import com.fitzone.model.Workout;
import com.fitzone.repository.ActivityLogRepository;
import com.fitzone.repository.WorkoutRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

// builds the data for the dashboard page
@Service
public class DashboardService {

    private final WorkoutRepository workoutRepo;
    private final ActivityLogRepository activityLogRepo;

    public DashboardService(WorkoutRepository workoutRepo, ActivityLogRepository activityLogRepo) {
        this.workoutRepo = workoutRepo;
        this.activityLogRepo = activityLogRepo;
    }

    public DashboardResponse getDashboard(Long userId) {
        DashboardResponse dashboard = new DashboardResponse();

        // summary stats
        dashboard.setTotalWorkouts(workoutRepo.countCompletedByUserId(userId));
        dashboard.setTotalCaloriesBurned(workoutRepo.totalCaloriesBurnedByUserId(userId));
        dashboard.setAvgStepsPerDay(activityLogRepo.avgStepsByUserId(userId));
        dashboard.setAvgSleepHours(activityLogRepo.avgSleepByUserId(userId));

        // grab last 5 workouts for the recent activity section
        List<Workout> recent = workoutRepo.findByUserIdOrderByCreatedAtDesc(userId);
        List<Map<String, Object>> recentList = new ArrayList<>();
        int limit = Math.min(recent.size(), 5);
        for (int i = 0; i < limit; i++) {
            Workout w = recent.get(i);
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("id", w.getId());
            map.put("name", w.getName());
            map.put("status", w.getStatus());
            map.put("durationMinutes", w.getDurationMinutes());
            map.put("caloriesBurned", w.getCaloriesBurned());
            map.put("date", w.getCreatedAt());
            map.put("exerciseCount", w.getExercises().size());
            recentList.add(map);
        }
        dashboard.setRecentWorkouts(recentList);

        // weekly activity chart data - last 7 days
        LocalDate today = LocalDate.now();
        LocalDate weekAgo = today.minusDays(6);
        List<ActivityLog> weekLogs = activityLogRepo.findByUserIdAndDateRange(userId, weekAgo, today);
        List<Map<String, Object>> weeklyData = new ArrayList<>();
        for (int i = 0; i < 7; i++) {
            LocalDate date = weekAgo.plusDays(i);
            Map<String, Object> dayMap = new LinkedHashMap<>();
            dayMap.put("date", date.toString());

            // find the log for this day, if it exists
            ActivityLog log = weekLogs.stream()
                    .filter(l -> l.getLogDate().equals(date))
                    .findFirst()
                    .orElse(null);

            dayMap.put("steps", log != null ? log.getSteps() : 0);
            dayMap.put("caloriesBurned", log != null ? log.getCaloriesBurned() : 0);
            dayMap.put("sleepHours", log != null ? log.getSleepHours() : 0);
            dayMap.put("waterMl", log != null ? log.getWaterMl() : 0);
            weeklyData.add(dayMap);
        }
        dashboard.setWeeklyActivity(weeklyData);

        return dashboard;
    }
}
