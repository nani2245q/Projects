package com.fitzone.controller;

import com.fitzone.dto.DashboardResponse;
import com.fitzone.model.User;
import com.fitzone.repository.UserRepository;
import com.fitzone.service.DashboardService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

// returns all the stats for the user's dashboard page
@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;
    private final UserRepository userRepo;

    public DashboardController(DashboardService dashboardService, UserRepository userRepo) {
        this.dashboardService = dashboardService;
        this.userRepo = userRepo;
    }

    @GetMapping
    public ResponseEntity<DashboardResponse> getDashboard(@AuthenticationPrincipal UserDetails userDetails) {
        User user = userRepo.findByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));
        return ResponseEntity.ok(dashboardService.getDashboard(user.getId()));
    }
}
