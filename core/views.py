from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.core.cache import cache

from .models import Thread, UnreadThread, Message


User = get_user_model()


@login_required
def user_list(request):
    """User list."""
    users = User.objects.exclude(id=request.user.id)
    for user in users:
        user.status = cache.get('seen_%s' % user.username)

    return render(request, 'user_list.html', {'users': users})


@login_required
def thread(request, username=None, thread_id=None):
    """Thread page."""
    messages = []
    users = {}
    if username:
        user = get_object_or_404(User, username=username)
        thread = Thread.objects.annotate(count=Count('users')).filter(users=request.user).filter(users=user).filter(count=2).first()
    elif thread_id:
        thread = get_object_or_404(Thread, pk=thread_id)

    if not thread:
        thread = Thread(name=', '.join([request.user.username, username]))
        thread.save()
        thread.users.add(request.user, user)
    else:
        # The user visited this tread - delete user's unread thread.
        UnreadThread.objects.filter(thread=thread, user=request.user).delete()

        messages = Message.objects.select_related('user').filter(thread=thread).order_by('date')[:50]
        for message in messages:
            if message.user.pk not in users:
                users[message.user.pk] = message.user.username

    return render(request, 'thread.html', {
        'thread': thread,
        'messages': messages,
        'users': users,
    })


def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('core:user_list'))
        else:
            print(form.errors)

    return render(request, 'login.html', {'form': form})


@login_required
def log_out(request):
    logout(request)
    return redirect(reverse('core:login'))


def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('core:login'))
        else:
            print(form.errors)

    return render(request, 'signup.html', {'form': form})
