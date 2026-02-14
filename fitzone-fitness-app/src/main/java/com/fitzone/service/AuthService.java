package com.fitzone.service;

import com.fitzone.dto.AuthRequest;
import com.fitzone.dto.AuthResponse;
import com.fitzone.model.User;
import com.fitzone.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepo;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepo, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepo = userRepo;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public AuthResponse register(AuthRequest request) {
        // make sure email isn't already taken
        if (userRepo.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already registered");
        }

        User user = new User(request.getName(), request.getEmail(), passwordEncoder.encode(request.getPassword()));
        user.setFitnessGoal(request.getFitnessGoal());
        user.setHeight(request.getHeight());
        user.setWeight(request.getWeight());

        user = userRepo.save(user);
        String token = jwtService.generateToken(user.getEmail());

        return new AuthResponse(token, user.getId(), user.getName(), user.getEmail(), user.getRole().name());
    }

    public AuthResponse login(AuthRequest request) {
        User user = userRepo.findByEmail(request.getEmail())
                .orElseThrow(() -> new RuntimeException("Invalid credentials"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid credentials");
        }

        // update last active timestamp
        user.setLastActiveAt(java.time.LocalDateTime.now());
        userRepo.save(user);

        String token = jwtService.generateToken(user.getEmail());
        return new AuthResponse(token, user.getId(), user.getName(), user.getEmail(), user.getRole().name());
    }
}
