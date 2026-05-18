const analyticsInitData = window.analyticsInitData || {};
const eventId = analyticsInitData.eventId || null;
const ageData = analyticsInitData.ageData || {};
const genderData = analyticsInitData.genderData || {};
const ticketData = analyticsInitData.ticketData || {};
const registrationsTimeline = analyticsInitData.registrationsTimeline || {};

let ageChart, genderChart, distributionChart, pieChart;

function initCharts() {
    const ageLabels = Object.keys(ageData);
    const ageValues = Object.values(ageData);

    const genderLabels = Object.keys(genderData);
    const genderValues = Object.values(genderData);

    const ticketLabels = Object.keys(ticketData);
    const ticketValues = Object.values(ticketData);

    const timelineLabels = Object.keys(registrationsTimeline);
    const timelineValues = Object.values(registrationsTimeline);

    const rootStyles = getComputedStyle(document.documentElement);
    const isDark = document.documentElement.classList.contains("dark");
    const textColor =
        rootStyles.getPropertyValue("--text-on-surface-variant").trim() ||
        (isDark ? "#b0b3c0" : "#424655");
    const gridColor =
        rootStyles.getPropertyValue("--border-outline-variant").trim() ||
        (isDark ? "#3a3e4a" : "#c2c6d8");

    const colors = {
        primary: rootStyles.getPropertyValue("--primary").trim() || "#0057cd",
        success: rootStyles.getPropertyValue("--success").trim() || "#06a77d",
        warning: rootStyles.getPropertyValue("--warning").trim() || "#f8a900",
        danger: rootStyles.getPropertyValue("--error").trim() || "#dc2626",
        info: rootStyles.getPropertyValue("--primary").trim() || "#0057cd",
        purples: ["#6610f2", "#6f42c1", "#d63384", "#a2d9ff", "#ce907d"],
    };

    const chartDefaults = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { ticks: { color: textColor }, grid: { color: gridColor } },
            y: {
                beginAtZero: true,
                ticks: { color: textColor },
                grid: { color: gridColor },
            },
        },
    };

    const ageCtx = document.getElementById("ageChart")?.getContext("2d");
    if (ageCtx) {
        if (ageChart) ageChart.destroy();
        ageChart = new Chart(ageCtx, {
            type: "bar",
            data: {
                labels: ageLabels,
                datasets: [
                    {
                        label: "Asistentes",
                        data: ageValues,
                        backgroundColor: (context) => {
                            const index = context.dataIndex;
                            return index === 1 ? "#0058be" : "#e5eeff";
                        },
                        borderRadius: 8,
                        borderSkipped: false,
                        barThickness: 40,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                },
                scales: {
                    y: { display: false, grid: { display: false } },
                    x: {
                        grid: { display: false },
                        border: { display: false },
                        ticks: {
                            font: { size: 11, weight: "600" },
                            color: "#424754",
                        },
                    },
                },
            },
        });
    }

    const genderCtx = document.getElementById("genderChart")?.getContext("2d");
    if (genderCtx) {
        if (genderChart) genderChart.destroy();
        genderChart = new Chart(genderCtx, {
            type: "bar",
            data: {
                labels: genderLabels,
                datasets: [
                    {
                        label: "Asistentes",
                        data: genderValues,
                        backgroundColor: [
                            colors.primary,
                            colors.success,
                            colors.warning,
                            colors.info,
                        ],
                        borderRadius: 4,
                    },
                ],
            },
            options: chartDefaults,
        });
    }

    const distCtx = document
        .getElementById("distributionChart")
        ?.getContext("2d");
    if (distCtx) {
        if (distributionChart) distributionChart.destroy();
        distributionChart = new Chart(distCtx, {
            type: "line",
            data: {
                labels: timelineLabels,
                datasets: [
                    {
                        label: "Inscripciones",
                        data: timelineValues,
                        borderColor: colors.primary,
                        backgroundColor: colors.primary + "20",
                        fill: true,
                        tension: 0.3,
                        borderWidth: 2,
                    },
                ],
            },
            options: chartDefaults,
        });
    }

    const pieCtx = document.getElementById("pieChart")?.getContext("2d");
    if (pieCtx) {
        if (pieChart) pieChart.destroy();
        pieChart = new Chart(pieCtx, {
            type: "pie",
            data: {
                labels: ticketLabels,
                datasets: [
                    {
                        data: ticketValues,
                        backgroundColor: [
                            colors.primary,
                            colors.success,
                            colors.warning,
                            colors.info,
                            colors.purples[0],
                            colors.purples[1],
                        ],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
            },
        });
    }

    renderLegend(ticketLabels, ticketValues);
}

function renderLegend(labels, values) {
    const legend = document.getElementById("ticketLegend");
    const total = values.reduce((a, b) => a + b, 0);
    const rootStyles = getComputedStyle(document.documentElement);
    const colorVals = [
        rootStyles.getPropertyValue("--primary").trim() || "#0057cd",
        rootStyles.getPropertyValue("--success").trim() || "#06a77d",
        rootStyles.getPropertyValue("--warning").trim() || "#f8a900",
        rootStyles.getPropertyValue("--primary").trim() || "#0057cd",
        rootStyles.getPropertyValue("--error").trim() || "#dc2626",
    ];

    legend.innerHTML = labels
        .map((label, i) => {
            const count = values[i];
            const percent = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
            return `
            <div class="d-flex justify-content-between align-items-center py-2 border-bottom" style="border-color: var(--border-outline-variant);">
                <div class="d-flex align-items-center gap-2">
                    <span class="badge rounded-circle" style="width: 10px; height: 10px; padding: 0; background-color: ${colorVals[i % colorVals.length]};"></span>
                    <span class="small fw-medium">${label}</span>
                </div>
                <span class="small fw-bold">${percent}%</span>
            </div>
        `;
        })
        .join("");
}

async function loadStats() {
    try {
        const response = await fetch(`/pe_analytics/api/stats/${eventId}/`);
        const result = await response.json();
        if (result.success) {
            const data = result.data;
            document.querySelector(
                ".content-card:nth-child(4) h3",
            ).textContent = "$" + data.total_revenue.toFixed(2);
            document.querySelector(
                ".content-card:nth-child(5) h3",
            ).textContent = data.total_attendance;
            document.querySelector(
                ".content-card:nth-child(6) h3",
            ).textContent = "$" + data.avg_ticket_price.toFixed(2);
        }
    } catch (error) {
        showToast("Error cargando estadísticas", "error");
    }
}

async function exportReport() {
    try {
        await new Promise((resolve) => setTimeout(resolve, 800));

        const chartIds = [
            "distributionChart",
            "pieChart",
            "ageChart",
            "genderChart",
        ];
        const chartImages = {};

        for (const id of chartIds) {
            const canvas = document.getElementById(id);
            if (canvas && canvas.width > 0 && canvas.height > 0) {
                chartImages[id] = canvas.toDataURL("image/png");
            }
        }

        const formData = new FormData();
        formData.append("charts", JSON.stringify(chartImages));

        const response = await fetch(`/analytics/export/${eventId}/`, {
            method: "POST",
            body: formData,
            headers: { "X-CSRFToken": getCookie("csrftoken") },
        });
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `reporte_analiticas_${eventId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } else {
            const result = await response.json();
            alert(result.error || "Error al generar el reporte");
        }
    } catch (error) {
        showToast("Error al generar el reporte", "error");
    }
}

function loadRawData() {
    window.location.href = `/pe_analytics/api/stats/${eventId}/`;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1),
                );
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", initCharts);

const themeObserver = new MutationObserver(() => {
    if (ageChart) {
        ageChart.destroy();
    }
    if (genderChart) {
        genderChart.destroy();
    }
    if (distributionChart) {
        distributionChart.destroy();
    }
    if (pieChart) {
        pieChart.destroy();
    }
    initCharts();
});

themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
});
