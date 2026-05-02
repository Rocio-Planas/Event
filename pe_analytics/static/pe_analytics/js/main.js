// Initialize Lucide Icons
lucide.createIcons();

// Sidebar Toggle Logic
const sidebarToggle = document.getElementById('sidebar-toggle');
const wrapper = document.getElementById('wrapper');

if (sidebarToggle) {
    sidebarToggle.addEventListener('click', (e) => {
        e.preventDefault();
        wrapper.classList.toggle('toggled');
    });
}

// Analytics Charts initialization
document.addEventListener('DOMContentLoaded', () => {
    // Trend Chart
    const trendCtx = document.getElementById('trendChart')?.getContext('2d');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [
                    {
                        label: 'Current Year',
                        data: [150, 230, 480, 720],
                        borderColor: '#0058be',
                        backgroundColor: 'rgba(0, 88, 190, 0.05)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 0,
                    },
                    {
                        label: 'Previous Year',
                        data: [120, 180, 320, 410],
                        borderColor: '#c2c6d6',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 0,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.03)' },
                        border: { display: false }
                    },
                    x: {
                        grid: { display: false },
                        border: { display: false }
                    }
                }
            }
        });
    }

    // Distribution Chart
    const distCtx = document.getElementById('distributionChart')?.getContext('2d');
    if (distCtx) {
        new Chart(distCtx, {
            type: 'doughnut',
            data: {
                labels: ['Standard', 'VIP Pass', 'Early Bird'],
                datasets: [{
                    data: [55, 25, 20],
                    backgroundColor: ['#0058be', '#198754', '#eff4ff'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                cutout: '80%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // Age Chart
    const ageCtx = document.getElementById('ageChart')?.getContext('2d');
    if (ageCtx) {
        new Chart(ageCtx, {
            type: 'bar',
            data: {
                labels: ['18-24', '25-34', '35-44', '45+'],
                datasets: [{
                    label: 'Attendees',
                    data: [35, 90, 70, 55],
                    backgroundColor: (context) => {
                        const index = context.dataIndex;
                        return index === 1 ? '#0058be' : '#e5eeff';
                    },
                    borderRadius: 8,
                    borderSkipped: false,
                    barThickness: 40
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true }
                },
                scales: {
                    y: {
                        display: false,
                        grid: { display: false }
                    },
                    x: {
                        grid: { display: false },
                        border: { display: false },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '600'
                            },
                            color: '#424754'
                        }
                    }
                }
            }
        });
    }
});
