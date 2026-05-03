// Chronogram Assistant - JavaScript
// Handles search, filtering, and interaction functionality

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const activityCards = document.querySelectorAll(".agenda-item");
    const dayFilter = document.getElementById("filter-day");
    const zoneFilter = document.getElementById("filter-zone");
    const speakerFilter = document.getElementById("filter-speaker");
    const emptyState = document.getElementById("empty-state");

    function formatDayLabel(dayValue) {
        if (!dayValue) return dayValue;
        const date = new Date(dayValue);
        return new Intl.DateTimeFormat("es-ES", {
            day: "numeric",
            month: "short",
        }).format(date);
    }

    function populateFilters() {
        const days = new Set();
        const zones = new Set();
        const speakers = new Set();

        activityCards.forEach((card) => {
            if (card.dataset.day) days.add(card.dataset.day);
            if (card.dataset.zone) zones.add(card.dataset.zone);
            if (card.dataset.speaker) speakers.add(card.dataset.speaker);
        });

        const sortedDays = Array.from(days).sort();
        const sortedZones = Array.from(zones).sort();
        const sortedSpeakers = Array.from(speakers).sort();

        sortedDays.forEach((day) => {
            const option = document.createElement("option");
            option.value = day;
            option.textContent = formatDayLabel(day);
            dayFilter.appendChild(option);
        });

        sortedZones.forEach((zone) => {
            const option = document.createElement("option");
            option.value = zone;
            option.textContent = zone;
            zoneFilter.appendChild(option);
        });

        sortedSpeakers.forEach((speaker) => {
            const option = document.createElement("option");
            option.value = speaker;
            option.textContent = speaker;
            speakerFilter.appendChild(option);
        });
    }

    function filterSessions() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedDay = dayFilter.value;
        const selectedZone = zoneFilter.value;
        const selectedSpeaker = speakerFilter.value;
        let visibleCount = 0;

        activityCards.forEach((card) => {
            const title = card.querySelector("h3").textContent.toLowerCase();
            const description =
                card
                    .querySelector(".session-description")
                    ?.textContent.toLowerCase() || "";
            const speakerName = card.dataset.speaker?.toLowerCase() || "";
            const dayValue = card.dataset.day || "";
            const zoneValue = (card.dataset.zone || "").toLowerCase();

            let showCard = true;

            if (searchTerm) {
                showCard =
                    title.includes(searchTerm) ||
                    description.includes(searchTerm) ||
                    speakerName.includes(searchTerm) ||
                    zoneValue.includes(searchTerm);
            }

            if (selectedDay !== "all") {
                showCard = showCard && dayValue === selectedDay;
            }

            if (selectedZone !== "all") {
                showCard = showCard && zoneValue === selectedZone.toLowerCase();
            }

            if (selectedSpeaker !== "all") {
                showCard =
                    showCard && speakerName === selectedSpeaker.toLowerCase();
            }

            card.style.display = showCard ? "flex" : "none";
            if (showCard) visibleCount++;
        });

        if (visibleCount === 0) {
            emptyState.classList.remove("d-none");
        } else {
            emptyState.classList.add("d-none");
        }
    }

    if (searchInput) {
        searchInput.addEventListener("input", filterSessions);
    }

    [dayFilter, zoneFilter, speakerFilter].forEach((filter) => {
        if (filter) {
            filter.addEventListener("change", filterSessions);
        }
    });

    populateFilters();
    filterSessions();
});
