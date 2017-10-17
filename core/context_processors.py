from .models import Thread, UnreadThread


def unread_threads(request):
    """Arrival date."""
    threads = []
    unread_threads_counter = 0

    if request.user.is_authenticated():
        threads = UnreadThread.objects.filter(user=request.user)\
                      .select_related('thread').order_by('-date')[:10]
        threads = [
            (thread.thread.id, thread.thread.name)
            for thread in threads
        ]
        unread_threads_counter = len(threads)

        # If there no unread_threads_counter - show last threads.
        if not threads:
            threads = Thread.objects.filter(users=request.user)\
                          .order_by('-last_message')[:10]
            threads = [(thread.id, thread.name) for thread in threads]

    return {'threads': threads, 'unread_threads': unread_threads_counter}
