/**
 * Concierge 360 - Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Concierge 360 Dashboard Ready');

    // Handle Ticket QR Button
    const ticketBtn = document.querySelector('.btn-primary');
    if (ticketBtn) {
        ticketBtn.addEventListener('click', () => {
            alert('Mostrando Ticket QR...');
        });
    }

    // Handle Bookmark Buttons
    const bookmarkBtns = document.querySelectorAll('.material-symbols-outlined');
    bookmarkBtns.forEach(btn => {
        if (btn.textContent === 'bookmark_add' || btn.textContent === 'bookmark') {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (btn.textContent === 'bookmark_add') {
                    btn.textContent = 'bookmark';
                    btn.style.color = 'var(--primary)';
                } else {
                    btn.textContent = 'bookmark_add';
                    btn.style.color = 'var(--outline-variant)';
                }
            });
        }
    });

    // Handle Navigation Links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
});
