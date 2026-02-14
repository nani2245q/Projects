# FitZone Fitness Application

A full-stack fitness tracking application built with Spring Boot and MySQL/H2, featuring workout logging, exercise library management, daily activity tracking, and a data-driven dashboard with user activity analytics.

## Features

- **User Authentication** — JWT-based registration and login with role-based access
- **Exercise Library** — 20+ exercises categorized by muscle group, category, and difficulty with calorie burn rates
- **Workout Logging** — Create workouts with multiple exercises, track sets/reps/weight/duration, auto-calculate calories burned
- **Daily Activity Tracking** — Log steps, calories, water intake, sleep, weight, and mood
- **Dashboard Analytics** — KPI cards (total workouts, calories, avg steps, avg sleep), recent workouts, and weekly activity chart
- **Data-Informed Design** — Relational schemas designed for user activity tracking with data-driven feature prioritization

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Java 17, Spring Boot 3.2 |
| Database | MySQL (production), H2 (development/demo) |
| ORM | Spring Data JPA, Hibernate |
| Security | Spring Security, JWT (jjwt 0.12.3) |
| Frontend | Vanilla JavaScript, HTML5, CSS3, Chart.js |
| Build | Maven |

## Data Model

```
Users ──────────── name, email, password, role, fitness goal, height/weight
Exercises ──────── name, muscle group, category, difficulty, calories/min
Workouts ─────── user (FK), exercises (1:N), duration, calories, status
WorkoutExercises ── workout (FK), exercise (FK), sets, reps, weight, duration
ActivityLogs ───── user (FK), date, steps, calories, water, sleep, weight, mood
```

## Setup & Run

### Prerequisites
- Java 17+
- Maven 3.8+
- MySQL (optional — defaults to H2 in-memory)

### Quick Start (H2 — no database setup needed)

```bash
cd fitzone-fitness-app
./mvnw spring-boot:run
```

The app starts on **http://localhost:8080** with an H2 in-memory database. Data is seeded automatically on first run.

### With MySQL

```bash
# Create the database
mysql -u root -p -e "CREATE DATABASE fitzone;"

# Run with MySQL profile
./mvnw spring-boot:run -Dspring-boot.run.profiles=mysql
```

### Access

- **App**: http://localhost:8080
- **Exercise Library**: http://localhost:8080/pages/exercises.html
- **Login**: `john@test.com` / `password123` or `admin@fitzone.com` / `admin123`
- **H2 Console** (dev): http://localhost:8080/h2-console

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |

### Exercises (public)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/exercises` | List all exercises |
| GET | `/api/exercises/muscle-group/{group}` | Filter by muscle group |
| GET | `/api/exercises/category/{cat}` | Filter by category |
| GET | `/api/exercises/search?q=` | Search exercises |

### Workouts (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workouts` | Create workout with exercises |
| GET | `/api/workouts` | List user's workouts |
| GET | `/api/workouts/{id}` | Get workout detail |
| POST | `/api/workouts/{id}/complete` | Mark workout complete |

### Activity Logs (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/activity` | Log daily activity |
| GET | `/api/activity` | List user's logs |
| GET | `/api/activity/date/{date}` | Get log by date |
| GET | `/api/activity/range?start=&end=` | Get logs in date range |
| PUT | `/api/activity/{id}` | Update a log entry |

### Dashboard (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | User's analytics dashboard |
