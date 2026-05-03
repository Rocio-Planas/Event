/**
 * Notifications functionality for EventPulse
 * Handles fetching, displaying, and marking notifications as read
 */

(function () {
    "use strict";

    // Configuration
    var POLL_INTERVAL = 30000;
    var UNREAD_ENDPOINT = "/comunicacion/unread-notifications/";
    var MARK_READ_ENDPOINT = "/comunicacion/mark-notification-read/";
    var notificationCache = [];

    // Request browser notification permission
    function requestNotificationPermission() {
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }
    }

    // Show browser notification
    function showBrowserNotification(title, body) {
        if ("Notification" in window && Notification.permission === "granted") {
            new Notification(title, {
                body: body,
                icon: "/static/img/logo.png",
            });
        }
    }

    // Fetch unread notifications from server
    function fetchUnreadNotifications() {
        fetch(UNREAD_ENDPOINT, { method: "GET", credentials: "same-origin" })
            .then(function (r) {
                return r.json();
            })
            .then(function (data) {
                if (data.success) {
                    renderNotifications(data.notifications);
                    updateBadge(data.count);
                    data.notifications.forEach(function (n) {
                        var exists = notificationCache.find(function (x) {
                            return x.id === n.id;
                        });
                        if (!exists && notificationCache.length > 0) {
                            showBrowserNotification(n.title, n.message);
                        }
                    });
                    notificationCache = data.notifications;
                }
            })
            .catch(function (e) {
                console.error("Error fetching notifications:", e);
            });
    }

    // Render notifications in dropdown
    function renderNotifications(notifications) {
        var container = document.getElementById("notifications-list");
        if (!container) return;
        if (!notifications || notifications.length === 0) {
            container.innerHTML =
                '<div class="dropdown-item text-muted small">Sin notificaciones</div>';
            return;
        }
        container.innerHTML = notifications
            .map(function (n) {
                var senderText = n.sender ? "De: " + n.sender.name : "Sistema";
                return (
                    '<a class="dropdown-item notification-item' +
                    (n.is_read ? "" : " bg-light") +
                    '" href="#" data-id="' +
                    n.id +
                    '" onclick="markAsRead(' +
                    n.id +
                    '); return false;"><div class="small text-muted mb-1">' +
                    senderText +
                    '</div><div class="fw-bold small">' +
                    n.title +
                    '</div><div class="small text-muted text-truncate">' +
                    n.message +
                    '</div><div class="small text-muted">' +
                    new Date(n.created_at).toLocaleString() +
                    "</div></a>"
                );
            })
            .join("");
    }

    // Update notification badge
    function updateBadge(count) {
        var badge = document.getElementById("unread-badge");
        if (badge) {
            badge.style.display = count > 0 ? "block" : "none";
            badge.textContent = count > 9 ? "9+" : count;
        }
    }

    // Mark notification as read (global function)
    window.markAsRead = function (notificationId) {
        var formData = new FormData();
        formData.append("notification_id", notificationId);
        fetch(MARK_READ_ENDPOINT, {
            method: "POST",
            body: formData,
            credentials: "same-origin",
        })
            .then(function (r) {
                return r.json();
            })
            .then(function (data) {
                if (data.success) fetchUnreadNotifications();
            })
            .catch(function (e) {
                console.error("Error marking notification as read:", e);
            });
    };

    // Initialize notifications when DOM is ready
    document.addEventListener("DOMContentLoaded", function () {
        requestNotificationPermission();
        fetchUnreadNotifications();
        setInterval(fetchUnreadNotifications, POLL_INTERVAL);
    });
})();
