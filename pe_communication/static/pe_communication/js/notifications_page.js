/**
 * JavaScript for the notifications page
 * Handles viewing notification details in modal and marking as read
 */

console.log("✅ notifications_page.js loaded successfully!");

let currentNotificationId = null;

// Wait for DOM to be fully loaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeNotifications);
} else {
    // DOM already loaded
    initializeNotifications();
}

function initializeNotifications() {
    console.log("📋 Initializing notifications...");

    // Setup view notification buttons
    const viewButtons = document.querySelectorAll(".view-notification-btn");
    console.log(`Found ${viewButtons.length} view buttons`);

    viewButtons.forEach((btn, index) => {
        btn.addEventListener("click", function (e) {
            console.log(`🔔 Button ${index} clicked`);
            e.preventDefault();

            const notificationItem = this.closest(".notification-item");
            if (!notificationItem) {
                console.error("❌ Notification item not found");
                return;
            }

            openModal(notificationItem);
        });
    });

    // Setup mark as read button
    const markReadBtn = document.getElementById("mark-read-modal-btn");
    if (markReadBtn) {
        markReadBtn.addEventListener("click", function () {
            console.log("✏️ Mark as read clicked");
            if (currentNotificationId) {
                markAsRead(currentNotificationId);
            }
        });
    } else {
        console.warn("⚠️ Mark read button not found");
    }

    // Setup mark as read buttons on the page cards
    const markReadButtons = document.querySelectorAll(
        ".mark-read-notification-btn",
    );
    console.log(`Found ${markReadButtons.length} mark-as-read buttons`);

    markReadButtons.forEach((btn, index) => {
        btn.addEventListener("click", function (e) {
            console.log(`✅ Mark-as-read button ${index} clicked`);
            e.preventDefault();

            const notificationItem = this.closest(".notification-item");
            if (!notificationItem) {
                console.error("❌ Notification item not found");
                return;
            }

            const notificationId = notificationItem.getAttribute("data-id");
            if (notificationId) {
                markAsRead(notificationId);
            }
        });
    });

    // Setup delete notification buttons
    const deleteButtons = document.querySelectorAll(".delete-notification-btn");
    console.log(`Found ${deleteButtons.length} delete buttons`);

    deleteButtons.forEach((btn, index) => {
        btn.addEventListener("click", function (e) {
            console.log(`🗑️ Delete button ${index} clicked`);
            e.preventDefault();

            const notificationItem = this.closest(".notification-item");
            if (!notificationItem) {
                console.error("❌ Notification item not found");
                return;
            }

            const notificationId = notificationItem.getAttribute("data-id");
            const notificationTitle =
                notificationItem
                    .querySelector(".notification-title")
                    ?.textContent?.trim() || "esta notificación";

            showDeleteConfirmation(notificationId, notificationTitle);
        });
    });

    // Setup confirm delete button
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener("click", function () {
            console.log("✅ Confirm delete clicked");
            if (currentNotificationId) {
                deleteNotification(currentNotificationId);
            }
        });
    } else {
        console.warn("⚠️ Confirm delete button not found");
    }

    console.log("✅ Notifications initialized successfully!");
}

function openModal(notificationItem) {
    const title =
        notificationItem
            .querySelector(".notification-title")
            ?.textContent?.trim() || "";
    const message =
        notificationItem
            .querySelector(".notification-body")
            ?.textContent?.trim() || "";
    const sender =
        notificationItem
            .querySelector(".notification-sender")
            ?.textContent?.trim() || "Sistema";
    const type =
        notificationItem
            .querySelector(".notification-type")
            ?.textContent?.trim() || "";
    const date =
        notificationItem
            .querySelector(".notification-date")
            ?.textContent?.trim() || "";
    const id = notificationItem.getAttribute("data-id");

    console.log("📝 Opening modal with data:", { id, title, sender });

    // Populate modal
    const titleEl = document.getElementById("modal-title");
    const messageEl = document.getElementById("modal-message");
    const senderEl = document.getElementById("modal-sender");
    const typeEl = document.getElementById("modal-type");
    const dateEl = document.getElementById("modal-date");

    if (titleEl) titleEl.textContent = title;
    if (messageEl) messageEl.textContent = message;
    if (senderEl) senderEl.textContent = sender;
    if (typeEl) typeEl.textContent = type;
    if (dateEl) dateEl.textContent = date;

    currentNotificationId = id;

    // Show modal
    const modalEl = document.getElementById("notificationModal");
    if (!modalEl) {
        console.error("❌ Modal not found in DOM");
        return;
    }

    if (typeof bootstrap === "undefined" || !bootstrap.Modal) {
        console.error("❌ Bootstrap Modal not available");
        return;
    }

    try {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
        console.log("✅ Modal shown successfully");
    } catch (error) {
        console.error("❌ Error showing modal:", error);
    }
}

function markAsRead(notificationId) {
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error("❌ CSRF token not found");
        return;
    }

    fetch("/comunicacion/mark-notification-read/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: "notification_id=" + notificationId,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                console.log("✅ Notification marked as read");
                window.location.reload();
                return;
            } else {
                console.error("❌ Error marking as read:", data.error);
            }
        })
        .catch((error) => {
            console.error("❌ Fetch error:", error);
        });
}

function getCsrfToken() {
    const tokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
    if (tokenInput) {
        return tokenInput.value;
    }

    const cookieName = "csrftoken";
    const cookieValue = document.cookie
        .split("; ")
        .find((row) => row.startsWith(cookieName + "="))
        ?.split("=")[1];
    return cookieValue || "";
}

function showDeleteConfirmation(notificationId, notificationTitle) {
    console.log(
        "🗑️ Showing delete confirmation for notification:",
        notificationId,
    );

    // Set current notification ID for deletion
    currentNotificationId = notificationId;

    // Update modal title
    const titleEl = document.getElementById("delete-notification-title");
    if (titleEl) {
        titleEl.textContent = notificationTitle;
    }

    // Show modal
    const modalEl = document.getElementById("deleteNotificationModal");
    if (!modalEl) {
        console.error("❌ Delete modal not found in DOM");
        return;
    }

    if (typeof bootstrap === "undefined" || !bootstrap.Modal) {
        console.error("❌ Bootstrap Modal not available");
        return;
    }

    try {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
        console.log("✅ Delete confirmation modal shown successfully");
    } catch (error) {
        console.error("❌ Error showing delete modal:", error);
    }
}

function deleteNotification(notificationId) {
    console.log("🗑️ Deleting notification:", notificationId);

    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.error("❌ CSRF token not found");
        return;
    }

    fetch("/comunicacion/delete-notification/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: "notification_id=" + notificationId,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                console.log("✅ Notification deleted successfully");

                // Close delete confirmation modal
                const deleteModalEl = document.getElementById(
                    "deleteNotificationModal",
                );
                const deleteModal = bootstrap.Modal.getInstance(deleteModalEl);
                if (deleteModal) {
                    deleteModal.hide();
                }

                // Remove notification from DOM
                const notificationItem = document.querySelector(
                    `.notification-item[data-id="${notificationId}"]`,
                );
                if (notificationItem) {
                    notificationItem.remove();
                    console.log("✅ Notification removed from DOM");
                }

                // Update counters if they exist
                updateNotificationCounters();
            } else {
                console.error("❌ Error deleting notification:", data.error);
                alert(
                    "Error al eliminar la notificación: " +
                        (data.error || "Error desconocido"),
                );
            }
        })
        .catch((error) => {
            console.error("❌ Fetch error:", error);
            alert("Error de conexión al eliminar la notificación");
        });
}

function updateNotificationCounters() {
    // Update unread count
    const unreadItems = document.querySelectorAll(
        "#unread-notifications .notification-item",
    );
    const unreadCountEl = document.querySelector(
        "#unread-notifications .notification-count",
    );
    if (unreadCountEl) {
        unreadCountEl.textContent = unreadItems.length;
    }

    // Update read count
    const readItems = document.querySelectorAll(
        "#read-notifications .notification-item",
    );
    const readCountEl = document.querySelector(
        "#read-notifications .notification-count",
    );
    if (readCountEl) {
        readCountEl.textContent = readItems.length;
    }

    // Show/hide empty states
    const unreadSection = document.getElementById("unread-notifications");
    const readSection = document.getElementById("read-notifications");

    if (unreadSection && unreadItems.length === 0) {
        const emptyState = unreadSection.querySelector(".empty-state");
        if (emptyState) emptyState.style.display = "block";
    }

    if (readSection && readItems.length === 0) {
        const emptyState = readSection.querySelector(".empty-state");
        if (emptyState) emptyState.style.display = "block";
    }
}
