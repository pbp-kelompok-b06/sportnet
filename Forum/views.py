from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from events.models import Event
from authenticate.models import Profile


# Import model & form HANYA untuk Forum
from .models import ForumPost
from .forms import ForumPostForm


@login_required # <-- Otomatis memblokir user yang belum login
def forum_page_view(request, event_id):
    """
    Menampilkan halaman forum (chat) untuk satu event spesifik.
    Juga menangani pengiriman pesan baru (POST).
    """
    
    # ambil data Event dan Profile user
    try:
        event = get_object_or_404(Event, id=event_id)
        profile = get_object_or_404(Profile, user=request.user) 
    except Exception as e:
        return render(request, 'forum/error_dependency.html', {'error': str(e)})

    # Logika jika user MENGIRIM PESAN BARU (method POST)
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.event = event
            new_post.profile = profile
            
            # (Cek apakah ini balasan)
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_post = ForumPost.objects.get(id=parent_id)
                    new_post.parent = parent_post
                except ForumPost.DoesNotExist:
                    pass 
            
            new_post.save()
            
            # Redirect kembali ke halaman yang sama
            return redirect('forum:forum_page', event_id=event.id)
    
    # Logika jika user HANYA MELIHAT HALAMAN (method GET)
    else:
        form = ForumPostForm() # Buat form kosong

    # ambil semua data post untuk ditampilkan di template
    posts = ForumPost.objects.filter(event=event, parent=None)

    # Siapkan data untuk dikirim ke template
    context = {
        'event': event,
        'posts': posts,
        'form': form,
        'current_profile': profile, 
    }
    
    # Tampilkan file HTML dan kirim datanya
    return render(request, 'forum/forum_page.html', context)