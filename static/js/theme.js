// ==================== TEMA OSCURO/CLARO ====================
function initTheme() {
  const storedTheme = localStorage.getItem("theme");
  const html = document.documentElement;
  if (storedTheme === "dark") {
    html.classList.add("dark");
    html.classList.remove("light");
  } else if (storedTheme === "light") {
    html.classList.add("light");
    html.classList.remove("dark");
  } else {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      html.classList.add("dark");
      html.classList.remove("light");
    } else {
      html.classList.add("light");
      html.classList.remove("dark");
    }
  }
  updateThemeIcon();
}

function toggleTheme() {
  const html = document.documentElement;
  if (html.classList.contains("dark")) {
    html.classList.remove("dark");
    html.classList.add("light");
    localStorage.setItem("theme", "light");
  } else {
    html.classList.remove("light");
    html.classList.add("dark");
    localStorage.setItem("theme", "dark");
  }
  updateThemeIcon();
}

function updateThemeIcon() {
  const icon = document.getElementById("theme-icon");
  if (!icon) return;
  const isDark = document.documentElement.classList.contains("dark");
  if (isDark) {
    icon.classList.remove("bi-brightness-high-fill");
    icon.classList.add("bi-moon-fill");
  } else {
    icon.classList.remove("bi-moon-fill");
    icon.classList.add("bi-brightness-high-fill");
  }
}

// ==================== MENÚ DE USUARIO ====================
function initUserMenu() {
  const userBtn = document.getElementById("user-menu-btn");
  const userMenu = document.getElementById("user-menu");
  if (userBtn && userMenu) {
    // Eliminar event listeners anteriores para evitar duplicados
    const newUserBtn = userBtn.cloneNode(true);
    userBtn.parentNode.replaceChild(newUserBtn, userBtn);

    newUserBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      if (userMenu.style.display === "block") {
        userMenu.style.display = "none";
      } else {
        userMenu.style.display = "block";
      }
    });

    document.addEventListener("click", function () {
      userMenu.style.display = "none";
    });
  }
}

// ==================== INICIALIZACIÓN ====================
document.addEventListener("DOMContentLoaded", function () {
  initTheme();
  initUserMenu();

  // Botón de tema
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }
});

// Escuchar cambios en el sistema (opcional)
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    if (!localStorage.getItem("theme")) {
      const html = document.documentElement;
      if (e.matches) {
        html.classList.add("dark");
        html.classList.remove("light");
      } else {
        html.classList.add("light");
        html.classList.remove("dark");
      }
      updateThemeIcon();
    }
  });
