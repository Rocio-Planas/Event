// ==================== TRADUCCIONES ====================
const translations = {
  es: {
    // Navbar y footer (claves comunes)
    nav_inicio: "Inicio",
    nav_presenciales: "Eventos Presenciales",
    nav_virtuales: "Eventos Virtuales",
    nav_contacto: "Contacto",
    my_dashboard: "Mi Panel",
    my_profile: "Mi Perfil",
    admin_panel: "Panel de Administración",
    login: "Iniciar Sesión",
    register: "Registrarse",
    footer_copyright: "Todos los derechos reservados.",
    about_link: "Acerca de",
    terms_link: "Términos y condiciones",
    privacy_link: "Política de privacidad",

    // Event Form
    form_title: "Detalles del Nuevo Evento",
    form_subtitle: "Configura tu próxima reunión memorable con precisión.",
    event_cover: "Portada del Evento",
    drop_image: "Suelta tu imagen aquí o explora",
    browse: "explora",
    image_hint: "PNG o JPG de alta resolución (Máx 10MB)",
    event_title_label: "Título del Evento",
    event_title_placeholder: "Dale a tu evento un nombre memorable...",
    description_label: "Descripción",
    description_placeholder: "Cuéntales a la gente qué esperar...",
    category_label: "Categoría",
    custom_category_label: "Nombre de Categoría Personalizada",
    custom_category_placeholder: "Ingresa el nombre de la categoría...",
    schedule_label: "Horario",
    duration_label: "Duración",
    minutes: "Minutos",
    access_type_label: "Tipo de Acceso",
    public_event: "Evento Público",
    public_desc: "Visible para todos",
    private_event: "Evento Privado",
    private_desc: "Acceso solo por invitación",
    invite_by_email: "Invitar por Email",
    invite_placeholder: "Ingresa direcciones de email separadas por comas...",
    create_event_btn: "Crear Evento",
    remove_btn: "Remover",

    // Organizer Dashboard
    config_event: "Configuración del Evento",
    change_cover: "Cambiar Portada",
    event_title_dash: "Título del Evento",
    description_dash: "Descripción",
    start_datetime: "Fecha y Hora de Inicio",
    duration_minutes: "Duración (minutos)",
    access_type_dash: "Tipo de Acceso",
    public: "Público",
    private: "Privado",
    invitations_label: "Invitaciones por Email",
    invitations_placeholder: "ejemplo1@mail.com, ejemplo2@mail.com",
    invite_link_label: "Enlace de invitación único:",
    copy_btn: "Copiar",
    copied: "¡Copiado al portapapeles!",
    save_changes: "Guardar Cambios",
    upload_material: "Subir material post-evento",
    metrics_title: "Métricas en Tiempo Real",
    live: "EN VIVO",
    online: "En línea",
    messages: "Mensajes",
    hands: "Manos",
    participation: "Participación",
    time: "Tiempo",
    satisfaction: "Satisfacción",
    updated_every: "Actualizado cada 5 segundos",
    quick_actions: "Acciones Rápidas",
    go_streaming: "Ir a Sala de Transmisión",
    export_pdf: "Exportar Reporte (PDF)",
    live_streaming: "Transmisión en Vivo",
    preview: "Previsualizar",
    youtube_help_title: "¿Cómo obtener la URL?",
    youtube_help_step1: "En YouTube, haz clic en Compartir bajo tu video.",
    youtube_help_step2: "Selecciona la opción Insertar (Embed).",
    youtube_help_step3: 'Copia solo el enlace dentro de src="..." (ej: https://www.youtube.com/embed/ABC).',
    youtube_url_label: "URL de Embed de YouTube",
    test_btn: "Probar",
    close: "Cerrar",
    share_material: "Compartir material del evento",
    recording_url: "URL de grabación (YouTube, Vimeo, etc.)",
    upload_slides: "Presentación o documento (PDF, PPT, etc.)",
    notify_followers: "Subir y notificar a seguidores",

    // Streaming Room
    live_indicator: "EN VIVO",
    viewers: "espectadores",
    record_screen: "Grabar pantalla",
    info_event: "Información del Evento",
    online_event: "En línea",
    live_poll: "Encuesta en Vivo",
    no_active_poll: "No hay encuestas activas",
    new_poll: "Nueva Encuesta",
    question_label: "Pregunta",
    question_placeholder: "¿Qué te parece el evento?",
    options_label: "Opciones",
    add_option: "Añadir opción",
    publish_poll: "Publicar Encuesta",
    chat_title: "Chat en Vivo",
    chat_placeholder: "Escribe un mensaje...",
    anon_question: "Pregunta anónima",
    raise_hand: "Levantar mano",
    rate_session: "¿Qué te está pareciendo la sesión?",
    excellent: "Excelente",
    very_good: "Muy buena",
    good: "Buena",
    fair: "Regular",
    poor: "Mala",
    send_anon_question: "Enviar Pregunta Anónima",
    cancel: "Cancelar",
    send: "Enviar",

    // Waiting Room
    event_upcoming: "Evento Próximo",
    days: "Días",
    hours: "Horas",
    minutes_short: "Mins",
    seconds: "Segs",
    invite_collaborators: "Invitar Colaboradores",
    enter_room: "Entrar a la Sala",
    room_opens_at: "La sala se abrirá cuando llegue la hora del evento.",

    // Additional for Organizer Dashboard
    emails_separator: "Separa los correos con comas.",
    shared_material: "Material ya compartido",
    recording: "Grabación",
    presentation: "Presentación",

    // Additional for Streaming Room
    transmission_starts_soon: "La transmisión comenzará pronto",

    // Emails
    invitation_title: "Has sido invitado a un evento privado",
    accept_invitation: "Unirme al evento - Sala de espera",
    what_is_this: "📌 ¿Qué es esto? El enlace te llevará a la sala de espera del evento. Cuando llegue la hora, podrás acceder a la transmisión en vivo.",
    reminder_title: "Recordatorio:",
    event_starts_soon: "El evento virtual",
    starts_in_1_hour: "comienza en 1 hora.",
    date_label: "Fecha:",
    duration_label: "Duración:",
    minutes: "minutos",
    organized_by: "Organizado por:",
    join_event: "Unirse al evento",
    ignore_reminder: "Si no esperabas este recordatorio, ignora este mensaje.",
    reminder_title: "Recordatorio",
    join_event: "Unirse al evento",
    ignore_reminder: "Si no esperabas este recordatorio, ignora este mensaje.",
    new_material_available: "Nuevo material disponible",
    organizer_shared_material: "El organizador ha compartido material del evento",
    recording_label: "🎥 Grabación:",
    presentation_label: "📊 Presentación:",
    view_recording: "Ver grabación",
    download_presentation: "Descargar presentación",
    view_event: "Ver evento",

    // Rating section
    rate_this_session: "CALIFICA ESTA SESIÓN",
    what_do_you_think_session: "¿Qué te está pareciendo la sesión?",
    excellent_rating: "Excelente",
    very_good_rating: "Muy buena",
    good_rating: "Buena",
    fair_rating: "Regular",
    poor_rating: "Mala",
    your_opinion_helps_improve: "Tu opinión nos ayuda a mejorar"
  },
  en: {
    nav_inicio: "Home",
    nav_presenciales: "In-Person Events",
    nav_virtuales: "Virtual Events",
    nav_contacto: "Contact",
    my_dashboard: "My Dashboard",
    my_profile: "My Profile",
    admin_panel: "Admin Panel",
    login: "Login",
    register: "Sign up",
    footer_copyright: "All rights reserved.",
    about_link: "About",
    terms_link: "Terms and Conditions",
    privacy_link: "Privacy Policy",

    form_title: "New Event Details",
    form_subtitle: "Configure your next remarkable gathering with precision.",
    event_cover: "Event Cover",
    drop_image: "Drop your image here or browse",
    browse: "browse",
    image_hint: "High-res PNG or JPG (Max 10MB)",
    event_title_label: "Event Title",
    event_title_placeholder: "Give your event a memorable name...",
    description_label: "Description",
    description_placeholder: "Tell people what to expect...",
    category_label: "Category",
    custom_category_label: "Custom Category Name",
    custom_category_placeholder: "Enter category name...",
    schedule_label: "Schedule",
    duration_label: "Duration",
    minutes: "Minutes",
    access_type_label: "Access Type",
    public_event: "Public Event",
    public_desc: "Visible to everyone",
    private_event: "Private Event",
    private_desc: "Invite only access",
    invite_by_email: "Invite by Email",
    invite_placeholder: "Enter email addresses separated by commas...",
    create_event_btn: "Create Event",
    remove_btn: "Remove",

    config_event: "Event Configuration",
    change_cover: "Change Cover",
    event_title_dash: "Event Title",
    description_dash: "Description",
    start_datetime: "Start Date and Time",
    duration_minutes: "Duration (minutes)",
    access_type_dash: "Access Type",
    public: "Public",
    private: "Private",
    invitations_label: "Email Invitations",
    invitations_placeholder: "email1@mail.com, email2@mail.com",
    invite_link_label: "Unique invitation link:",
    copy_btn: "Copy",
    copied: "Copied to clipboard!",
    save_changes: "Save Changes",
    upload_material: "Upload post-event material",
    metrics_title: "Real-time Metrics",
    live: "LIVE",
    online: "Online",
    messages: "Messages",
    hands: "Hands",
    participation: "Participation",
    time: "Time",
    satisfaction: "Satisfaction",
    updated_every: "Updated every 5 seconds",
    quick_actions: "Quick Actions",
    go_streaming: "Go to Streaming Room",
    export_pdf: "Export Report (PDF)",
    live_streaming: "Live Streaming",
    preview: "Preview",
    youtube_help_title: "How to get the URL?",
    youtube_help_step1: "On YouTube, click Share below your video.",
    youtube_help_step2: "Select the Embed option.",
    youtube_help_step3: 'Copy only the link inside src="..." (e.g., https://www.youtube.com/embed/ABC).',
    youtube_url_label: "YouTube Embed URL",
    test_btn: "Test",
    close: "Close",
    share_material: "Share event material",
    recording_url: "Recording URL (YouTube, Vimeo, etc.)",
    upload_slides: "Slides or document (PDF, PPT, etc.)",
    notify_followers: "Upload and notify followers",

    live_indicator: "LIVE",
    viewers: "viewers",
    record_screen: "Record screen",
    info_event: "Event Information",
    online_event: "Online",
    live_poll: "Live Poll",
    no_active_poll: "No active polls",
    new_poll: "New Poll",
    question_label: "Question",
    question_placeholder: "How do you like the event?",
    options_label: "Options",
    add_option: "Add option",
    publish_poll: "Publish Poll",
    chat_title: "Live Chat",
    chat_placeholder: "Type a message...",
    anon_question: "Anonymous question",
    raise_hand: "Raise hand",
    rate_session: "How do you rate this session?",
    excellent: "Excellent",
    very_good: "Very good",
    good: "Good",
    fair: "Fair",
    poor: "Poor",
    send_anon_question: "Send Anonymous Question",
    cancel: "Cancel",
    send: "Send",

    event_upcoming: "Upcoming Event",
    days: "Days",
    hours: "Hours",
    minutes_short: "Mins",
    seconds: "Secs",
    invite_collaborators: "Invite Collaborators",
    enter_room: "Enter Room",
    room_opens_at: "The room will open when the event starts.",

    // Additional for Organizer Dashboard
    emails_separator: "Separate emails with commas.",
    shared_material: "Already shared material",
    recording: "Recording",
    presentation: "Presentation",

    // Additional for Streaming Room
    transmission_starts_soon: "The transmission will start soon",

    // Emails
    invitation_title: "You have been invited to a private event",
    accept_invitation: "Join the event - Waiting room",
    what_is_this: "📌 What is this? The link will take you to the event's waiting room. When the time comes, you'll be able to access the live stream.",
    ignore_invitation: "If you did not expect this invitation, ignore this message.",
    reminder_title: "Reminder",
    join_event: "Join the event",
    ignore_reminder: "If you did not expect this reminder, ignore this message.",
    event_starts_soon: "The virtual event",
    starts_in_1_hour: "starts in 1 hour.",
    date_label: "Date:",
    duration_label: "Duration:",
    minutes: "minutes",
    organized_by: "Organized by:",
    new_material_available: "New material available",
    organizer_shared_material: "The organizer has shared event material",
    recording_label: "🎥 Recording:",
    presentation_label: "📊 Presentation:",
    view_recording: "View recording",
    download_presentation: "Download presentation",
    view_event: "View event",

    // Rating section
    rate_this_session: "RATE THIS SESSION",
    what_do_you_think_session: "What do you think of the session?",
    excellent_rating: "Excellent",
    very_good_rating: "Very good",
    good_rating: "Good",
    fair_rating: "Fair",
    poor_rating: "Poor",
    your_opinion_helps_improve: "Your opinion helps us improve"
  },
};

// ==================== LÓGICA DE TEMA ====================
function initTheme() {
  const stored = localStorage.getItem("theme");
  const html = document.documentElement;
  if (stored === "dark") {
    html.classList.add("dark");
    html.classList.remove("light");
  } else if (stored === "light") {
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
  updateIcon();
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
  updateIcon();
}

function updateIcon() {
  const icon = document.getElementById("theme-icon");
  if (icon) {
    if (document.documentElement.classList.contains("dark")) {
      icon.className = "bi bi-moon-fill";
    } else {
      icon.className = "bi bi-brightness-high-fill";
    }
  }
}

// ==================== LÓGICA DE TRADUCCIÓN ====================
let currentLang = localStorage.getItem("lang") || "es"; // español por defecto

function applyTranslations() {
  const t = translations[currentLang];
  if (!t) return;

  // Elementos con data-i18n
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (t[key]) {
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        if (el.hasAttribute("placeholder")) {
          el.placeholder = t[key];
        } else {
          el.value = t[key];
        }
      } else {
        el.innerText = t[key];
      }
    }
  });

  // Elementos con data-i18n-placeholder (solo placeholder)
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (t[key]) el.placeholder = t[key];
  });

  // Elementos con data-i18n-title (solo title)
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const key = el.getAttribute("data-i18n-title");
    if (t[key]) el.title = t[key];
  });

  // Actualizar clases activas de los botones de idioma
  const langEs = document.getElementById("lang-es");
  const langEn = document.getElementById("lang-en");
  if (langEs && langEn) {
    if (currentLang === "es") {
      langEs.classList.add("lang-active");
      langEn.classList.remove("lang-active");
    } else {
      langEn.classList.add("lang-active");
      langEs.classList.remove("lang-active");
    }
  }
}

function setLanguage(lang) {
  if (lang !== "es" && lang !== "en") return;
  currentLang = lang;
  localStorage.setItem("lang", lang);
  applyTranslations();
  // Disparar evento para que otros scripts (como gráficas, etc.) puedan reaccionar
  window.dispatchEvent(
    new CustomEvent("languageChanged", { detail: { lang: lang } }),
  );
}

function initLanguage() {
  // Sincronizar currentLang con localStorage (por si se cambió desde otra pestaña)
  const stored = localStorage.getItem("lang");
  if (stored === "es" || stored === "en") {
    currentLang = stored;
  } else {
    currentLang = "es";
    localStorage.setItem("lang", "es");
  }
  applyTranslations();
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) themeToggle.addEventListener("click", toggleTheme);
  const langEs = document.getElementById("lang-es");
  const langEn = document.getElementById("lang-en");
  if (langEs) langEs.addEventListener("click", () => setLanguage("es"));
  if (langEn) langEn.addEventListener("click", () => setLanguage("en"));
  // Lógica del menú de usuario (si existe)
  const userBtn = document.getElementById("user-menu-btn");
  const userMenu = document.getElementById("user-menu");
  if (userBtn && userMenu) {
    userBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      userMenu.style.display =
        userMenu.style.display === "block" ? "none" : "block";
    });
    document.addEventListener(
      "click",
      () => (userMenu.style.display = "none"),
    );
  }
});
