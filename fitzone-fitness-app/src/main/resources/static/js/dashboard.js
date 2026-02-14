document.addEventListener('DOMContentLoaded', async () => {
    if (!isLoggedIn()) {
        document.getElementById('dashboard-auth').style.display = 'block';
        return;
    }

    document.getElementById('dashboard').style.display = 'block';

    const data = await apiFetch('/api/dashboard');

    document.getElementById('total-workouts').textContent = data.totalWorkouts || 0;
    document.getElementById('total-calories').textContent = Math.round(data.totalCaloriesBurned || 0);
    document.getElementById('avg-steps').textContent = Math.round(data.avgStepsPerDay || 0).toLocaleString();
    document.getElementById('avg-sleep').textContent = (data.avgSleepHours || 0).toFixed(1);

    // Recent workouts table
    const tbody = document.getElementById('recent-workouts');
    if (data.recentWorkouts) {
        data.recentWorkouts.forEach(w => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${w.name || 'Workout'}</td>
                <td>${w.durationMinutes ? w.durationMinutes + ' min' : '-'}</td>
                <td>${w.caloriesBurned ? Math.round(w.caloriesBurned) : '-'}</td>
                <td>${w.date ? new Date(w.date).toLocaleDateString() : '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Weekly activity chart
    if (data.weeklyActivity && data.weeklyActivity.length > 0) {
        const ctx = document.getElementById('weekly-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.weeklyActivity.map(d => d.date),
                datasets: [
                    {
                        label: 'Steps',
                        data: data.weeklyActivity.map(d => d.steps || 0),
                        backgroundColor: 'rgba(79,70,229,.6)',
                        yAxisID: 'y'
                    },
                    {
                        label: 'Calories Burned',
                        data: data.weeklyActivity.map(d => d.caloriesBurned || 0),
                        type: 'line',
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16,185,129,.1)',
                        fill: true,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: { position: 'left', title: { display: true, text: 'Steps' } },
                    y1: { position: 'right', title: { display: true, text: 'Calories' }, grid: { drawOnChartArea: false } }
                }
            }
        });
    }
});
