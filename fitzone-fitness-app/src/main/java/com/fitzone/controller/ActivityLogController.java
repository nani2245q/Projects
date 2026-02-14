package com.fitzone.controller;

import com.fitzone.model.ActivityLog;
import com.fitzone.model.User;
import com.fitzone.repository.UserRepository;
import com.fitzone.service.ActivityLogService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

// endpoints for daily activity tracking (steps, calories, sleep, etc)
@RestController
@RequestMapping("/api/activity")
public class ActivityLogController {

    private final ActivityLogService activityLogService;
    private final UserRepository userRepo;

    public ActivityLogController(ActivityLogService activityLogService, UserRepository userRepo) {
        this.activityLogService = activityLogService;
        this.userRepo = userRepo;
    }

    // log a new activity entry
    @PostMapping
    public ResponseEntity<ActivityLog> logActivity(@AuthenticationPrincipal UserDetails userDetails, @RequestBody ActivityLog log) {
        Long userId = getUserId(userDetails);
        return ResponseEntity.ok(activityLogService.logActivity(userId, log));
    }

    @GetMapping
    public ResponseEntity<List<ActivityLog>> getLogs(@AuthenticationPrincipal UserDetails userDetails) {
        Long userId = getUserId(userDetails);
        return ResponseEntity.ok(activityLogService.getUserLogs(userId));
    }

    // get log for a specific date
    @GetMapping("/date/{date}")
    public ResponseEntity<?> getLogByDate(@AuthenticationPrincipal UserDetails userDetails,
                                          @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        Long userId = getUserId(userDetails);
        ActivityLog log = activityLogService.getLogByDate(userId, date);
        if (log == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(log);
    }

    // get logs between two dates
    @GetMapping("/range")
    public ResponseEntity<List<ActivityLog>> getLogsByRange(
            @AuthenticationPrincipal UserDetails userDetails,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate end) {
        Long userId = getUserId(userDetails);
        return ResponseEntity.ok(activityLogService.getLogsByDateRange(userId, start, end));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ActivityLog> updateLog(@PathVariable Long id, @RequestBody ActivityLog updates) {
        return ResponseEntity.ok(activityLogService.updateLog(id, updates));
    }

    private Long getUserId(UserDetails userDetails) {
        User user = userRepo.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));
        return user.getId();
    }
}
