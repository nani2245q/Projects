package com.fitzone.dto;

import java.util.List;
import java.util.Map;

public class DashboardResponse {
    private Long totalWorkouts;
    private Double totalCaloriesBurned;
    private Double avgStepsPerDay;
    private Double avgSleepHours;
    private List<Map<String, Object>> recentWorkouts;
    private List<Map<String, Object>> weeklyActivity;

    public Long getTotalWorkouts() { return totalWorkouts; }
    public void setTotalWorkouts(Long totalWorkouts) { this.totalWorkouts = totalWorkouts; }
    public Double getTotalCaloriesBurned() { return totalCaloriesBurned; }
    public void setTotalCaloriesBurned(Double totalCaloriesBurned) { this.totalCaloriesBurned = totalCaloriesBurned; }
    public Double getAvgStepsPerDay() { return avgStepsPerDay; }
    public void setAvgStepsPerDay(Double avgStepsPerDay) { this.avgStepsPerDay = avgStepsPerDay; }
    public Double getAvgSleepHours() { return avgSleepHours; }
    public void setAvgSleepHours(Double avgSleepHours) { this.avgSleepHours = avgSleepHours; }
    public List<Map<String, Object>> getRecentWorkouts() { return recentWorkouts; }
    public void setRecentWorkouts(List<Map<String, Object>> recentWorkouts) { this.recentWorkouts = recentWorkouts; }
    public List<Map<String, Object>> getWeeklyActivity() { return weeklyActivity; }
    public void setWeeklyActivity(List<Map<String, Object>> weeklyActivity) { this.weeklyActivity = weeklyActivity; }
}
