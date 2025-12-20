// Mark as read functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle mark as read buttons
    const markReadButtons = document.querySelectorAll('.mark-read-btn');
    markReadButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const notifId = this.getAttribute('data-notif-id');
            
            try {
                const response = await fetch(`/notification/mark-read/${notifId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                if (response.ok) {
                    // Remove the button and "New" badge
                    const liElement = this.closest('li');
                    
                    // Remove mark-read button
                    this.remove();
                    
                    // Remove "New" badge
                    const badge = liElement.querySelector('.inline-block.align-middle');
                    if (badge) {
                        badge.remove();
                    }
                    
                    // Update styling - remove blue highlight
                    liElement.classList.remove('bg-blue-50', 'border-l-4', 'border-blue-500');
                    liElement.classList.add('bg-white', 'opacity-70');
                    
                    // Update title color
                    const title = liElement.querySelector('h2');
                    if (title) {
                        title.classList.remove('text-blue-700');
                        title.classList.add('text-gray-800');
                    }
                } else {
                    alert('Failed to mark as read');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred');
            }
        });
    });

    // Handle delete buttons
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const notifId = this.getAttribute('data-notif-id');
            
            // Confirm deletion
            if (!confirm('Are you sure you want to delete this notification?')) {
                return;
            }
            
            try {
                const response = await fetch(`/notification/delete/${notifId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                if (response.ok) {
                    // Animate removal
                    const liElement = this.closest('li');
                    liElement.style.opacity = '0';
                    liElement.style.transform = 'translateX(20px)';
                    liElement.style.transition = 'all 0.3s ease-out';
                    
                    setTimeout(() => {
                        liElement.remove();
                        
                        // Check if there are no more notifications
                        const notifList = document.querySelector('ul.space-y-4');
                        if (notifList && notifList.children.length === 0) {
                            // Reload page to show "No Notifications yet" message
                            location.reload();
                        }
                    }, 300);
                } else {
                    alert('Failed to delete notification');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred');
            }
        });
    });

    // Check for new notifications
    checkNewNotifications();
});

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

// Check for new notifications function (called from template)
function checkNewNotifications() {
    // This function can be expanded later to check for new notifications
    // via a separate API endpoint
}
