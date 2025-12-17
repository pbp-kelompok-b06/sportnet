document.addEventListener('DOMContentLoaded', function() {
    // Mark single notification as read
    document.querySelectorAll('.mark-read-btn').forEach(button => {
        button.addEventListener('click', function() {
            const notifId = this.dataset.notifId;
            fetch(`/notification/mark-as-read/${notifId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update UI
                    const notifItem = this.closest('li');
                    notifItem.classList.remove('bg-blue-50', 'border-l-4', 'border-blue-500');
                    notifItem.classList.add('bg-white', 'opacity-70');
                    // Hide the mark as read button and new badge
                    this.style.display = 'none';
                    const newBadge = notifItem.querySelector('.bg-blue-200');
                    if (newBadge) newBadge.style.display = 'none';
                    // Update notification badge
                    updateNotificationBadge();
                    // Show toast
                    showToast('Notifikasi telah ditandai sebagai dibaca', 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Gagal menandai notifikasi sebagai dibaca', 'error');
            });
        });
    });

    // Mark all notifications as read
    const markAllBtn = document.getElementById('mark-all-btn');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function() {
            fetch('/notification/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update UI for all notifications
                    document.querySelectorAll('.mark-read-btn').forEach(btn => {
                        const notifItem = btn.closest('li');
                        notifItem.classList.remove('bg-blue-50', 'border-l-4', 'border-blue-500');
                        notifItem.classList.add('bg-white', 'opacity-70');
                        btn.style.display = 'none';
                    });
                    // Hide all new badges
                    document.querySelectorAll('.bg-blue-200').forEach(badge => {
                        badge.style.display = 'none';
                    });
                    // Update notification badge
                    updateNotificationBadge();
                    showToast('Semua notifikasi telah ditandai sebagai dibaca', 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Gagal menandai semua notifikasi sebagai dibaca', 'error');
            });
        });
    }
});

// Toast notification system
function showToast(message, type = 'success') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `transform transition-all duration-300 ease-in-out px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white min-w-[200px]`;
    
    // Icon based on type
    const icon = document.createElement('span');
    icon.className = 'text-lg';
    icon.textContent = type === 'success' ? '✓' : '✕';
    
    // Message
    const text = document.createElement('span');
    text.textContent = message;
    
    // Append elements
    toast.appendChild(icon);
    toast.appendChild(text);
    toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.add('translate-y-0', 'opacity-100');
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-2', 'opacity-0');
        setTimeout(() => {
            toastContainer.removeChild(toast);
            if (toastContainer.children.length === 0) {
                document.body.removeChild(toastContainer);
            }
        }, 300);
    }, 3000);
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to update notification badge
function updateNotificationBadge() {
    fetch('/notification/json/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        const notifications = data.notifications || [];
        const unreadCount = notifications.filter(n => !n.is_read).length;
        
        // Update all notification badges (desktop and mobile)
        const badges = document.querySelectorAll('.absolute.-top-2.-right-4, .absolute.-top-1.-right-3');
        
        badges.forEach(badge => {
            if (unreadCount > 0) {
                badge.textContent = unreadCount;
                badge.style.display = '';
            } else {
                badge.style.display = 'none';
            }
        });
    })
    .catch(error => console.error('Error updating badge:', error));
}

// Function to check for new notifications
function checkNewNotifications() {
    fetch('/notification/check-new/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.hasNew) {
            showToast('Anda memiliki notifikasi baru!', 'success');
            updateNotificationBadge();
        }
    })
    .catch(error => console.error('Error checking notifications:', error));
}

// Check immediately on page load
checkNewNotifications();

// Check for new notifications every 30 seconds
setInterval(checkNewNotifications, 30000);