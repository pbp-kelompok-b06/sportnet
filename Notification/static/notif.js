function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function showToast(message, type = 'info') {
  // basic toast appended to body
  const toast = document.createElement('div');
  toast.className = `notification-toast fixed bottom-6 right-6 z-50 max-w-xs px-4 py-2 rounded shadow-lg text-sm text-white`;
  if (type === 'success') toast.style.background = '#059669';
  else if (type === 'error') toast.style.background = '#dc2626';
  else toast.style.background = '#1f2937';
  toast.textContent = message;

  document.body.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

async function markAsRead(notifId, btn) {
  try {
    const res = await fetch(`/notification/mark-as-read/${notifId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json'
      }
    });
    if (!res.ok) {
      const txt = await res.text();
      console.error('Mark read failed:', res.status, txt);
      showToast('Failed to read notifications', 'error');
      return;
    }
    const data = await res.json();
    if (data.status === 'success') {
      // Update UI
      const li = btn.closest('li');
      if (li) {
        li.classList.remove('bg-blue-50', 'border-l-4', 'border-blue-500');
        li.classList.add('bg-white', 'opacity-70');
        const badge = li.querySelector('span.inline-block');
        if (badge) badge.remove();
        btn.remove();
      }
      showToast('Notifications marked as read', 'success');
    }
  } catch (err) {
    console.error('Error marking notification read', err);
    showToast('Error ocurred while marking notification read', 'error');
  }
}

async function markAllAsRead(btn) {
  try {
    const res = await fetch(`/notification/mark-all-read/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json'
      }
    });
    if (!res.ok) {
      const txt = await res.text();
      console.error('Mark all failed:', res.status, txt);
      showToast('Failed to mark all notifications as read', 'error');
      return;
    }
    const data = await res.json();
    if (data.status === 'success') {
      // Update all UI entries
      const lis = document.querySelectorAll('li');
      lis.forEach(li => {
        if (li.classList.contains('bg-blue-50')) {
          li.classList.remove('bg-blue-50', 'border-l-4', 'border-blue-500');
          li.classList.add('bg-white', 'opacity-70');
          const badge = li.querySelector('span.inline-block');
          if (badge) badge.remove();
          const btn = li.querySelector('.mark-read-btn');
          if (btn) btn.remove();
        }
      });
      showToast(`${data.updated} marked as read`, 'success');
    }
  } catch (err) {
    console.error('Error marking all notifications read', err);
    showToast('Error ocurred', 'error');
  }
}

async function deleteNotification(notifId, btn) {

  try {
    const res = await fetch(`/notification/delete/${notifId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json'
      }
    });
    if (!res.ok) {
      const txt = await res.text();
      console.error('Delete failed:', res.status, txt);
      showToast('Failed to delete notification', 'error');
      return;
    }
    const data = await res.json();
    if (data.status === 'success') {
      // Animate removal
      const li = btn.closest('li');
      if (li) {
        li.style.opacity = '0';
        li.style.transform = 'translateX(20px)';
        li.style.transition = 'all 0.3s ease-out';
        
        setTimeout(() => {
          li.remove();
          
          // Check if there are no more notifications
          const notifList = document.querySelector('ul.space-y-4');
          if (notifList && notifList.children.length === 0) {
            // Reload page to show "No Notifications yet" message
            location.reload();
          }
        }, 300);
      }
      showToast('Notification deleted', 'success');
    }
  } catch (err) {
    console.error('Error deleting notification', err);
    showToast('Error occurred while deleting notification', 'error');
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const markReadButtons = document.querySelectorAll('.mark-read-btn');
  markReadButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const notifId = btn.dataset.notifId;
      markAsRead(notifId, btn);
    });
  });

  const deleteButtons = document.querySelectorAll('.delete-btn');
  deleteButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const notifId = btn.dataset.notifId;
      deleteNotification(notifId, btn);
    });
  });

  const markAllBtn = document.getElementById('mark-all-btn');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', (e) => {
      markAllAsRead(markAllBtn);
    });
  }
});
