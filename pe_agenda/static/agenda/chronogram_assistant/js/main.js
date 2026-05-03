/**
 * EventConcierge Main Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('.search-input');
    const categoryPills = document.querySelectorAll('.pill');
    const sessionCards = document.querySelectorAll('.session-card');
    const registerButtons = document.querySelectorAll('.btn-primary-custom, .btn-inscribed');

    let activeCategory = 'Todo';
    let searchQuery = '';

    // Search functionality
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase();
        filterSessions();
    });

    // Category filtering
    categoryPills.forEach(pill => {
        pill.addEventListener('click', () => {
            // Update active state
            categoryPills.forEach(p => {
                p.classList.remove('pill-active');
                p.classList.add('pill-inactive');
            });
            pill.classList.remove('pill-inactive');
            pill.classList.add('pill-active');

            activeCategory = pill.textContent.trim();
            filterSessions();
        });
    });

    // Filter logic
    function filterSessions() {
        let visibleCount = 0;
        const emptyState = document.getElementById('empty-state');

        sessionCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const category = card.querySelector('.tag').textContent.toLowerCase();
            const isInscribed = card.dataset.inscribed === 'true';
            
            const matchesSearch = title.includes(searchQuery);
            
            let matchesCategory = false;
            if (activeCategory === 'Todo') {
                matchesCategory = true;
            } else if (activeCategory === 'Mis Inscripciones') {
                matchesCategory = isInscribed;
            } else {
                matchesCategory = category.includes(activeCategory.toLowerCase());
            }

            if (matchesSearch && matchesCategory) {
                card.classList.remove('d-none');
                card.classList.add('d-flex');
                visibleCount++;
            } else {
                card.classList.remove('d-flex');
                card.classList.add('d-none');
            }
        });

        // Show/hide empty state
        if (visibleCount === 0) {
            emptyState.classList.remove('d-none');
        } else {
            emptyState.classList.add('d-none');
        }
    }

    // Register button interaction
    registerButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const card = btn.closest('.session-card');
            const isRegistered = card.dataset.inscribed === 'true';

            if (!isRegistered) {
                // Change to registered state
                btn.innerHTML = '<span class="material-symbols-outlined me-2" style="font-variation-settings: \'FILL\' 1;">check_circle</span> Inscrito';
                btn.classList.remove('btn-primary-custom');
                btn.classList.add('btn-inscribed');
                card.dataset.inscribed = 'true';
            } else {
                // Change to unregistered state (Unsubscribe)
                btn.innerHTML = '<span class="material-symbols-outlined me-2">add_circle</span> Inscribirme';
                btn.classList.remove('btn-inscribed');
                btn.classList.add('btn-primary-custom');
                card.dataset.inscribed = 'false';
            }

            // Re-filter if we are in "Mis Inscripciones" view
            if (activeCategory === 'Mis Inscripciones') {
                filterSessions();
            }
        });
    });

    // Back button
    const backBtn = document.querySelector('.back-link');
    if (backBtn) {
        backBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Navegando hacia atrás...');
        });
    }
});
