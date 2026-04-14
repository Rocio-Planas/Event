// Inicialización del tema (modo oscuro/claro)
function initTheme() {
    const storedTheme = localStorage.getItem('theme');
    const html = document.documentElement;
    if (storedTheme === 'dark') {
        html.classList.add('dark');
        html.classList.remove('light');
    } else if (storedTheme === 'light') {
        html.classList.add('light');
        html.classList.remove('dark');
    } else {
        // Seguir la preferencia del sistema
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            html.classList.add('dark');
            html.classList.remove('light');
        } else {
            html.classList.add('light');
            html.classList.remove('dark');
        }
    }
    updateThemeIcon();
}

function toggleTheme() {
    const html = document.documentElement;
    if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        html.classList.add('light');
        localStorage.setItem('theme', 'light');
    } else {
        html.classList.remove('light');
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = document.getElementById('theme-icon');
    if (!icon) return;
    const isDark = document.documentElement.classList.contains('dark');
    if (isDark) {
        icon.classList.remove('bi-brightness-high-fill');
        icon.classList.add('bi-moon-fill');
    } else {
        icon.classList.remove('bi-moon-fill');
        icon.classList.add('bi-brightness-high-fill');
    }
}

// Escuchar cambios en el sistema (opcional)
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    // Solo aplicar si el usuario no ha establecido una preferencia manual
    if (!localStorage.getItem('theme')) {
        const html = document.documentElement;
        if (e.matches) {
            html.classList.add('dark');
            html.classList.remove('light');
        } else {
            html.classList.add('light');
            html.classList.remove('dark');
        }
        updateThemeIcon();
    }
});

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    // También puedes mantener la lógica del menú de usuario si la tienes
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userMenu = document.getElementById('user-menu');
    if (userMenuBtn && userMenu) {
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userMenu.style.display = userMenu.style.display === 'block' ? 'none' : 'block';
        });
        document.addEventListener('click', (e) => {
            if (!userMenuBtn.contains(e.target) && !userMenu.contains(e.target)) {
                userMenu.style.display = 'none';
            }
        });
    }
});