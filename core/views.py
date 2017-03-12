from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.core import serializers

from .models import Thread, Message


User = get_user_model()


@login_required
def user_list(request):
    """
    NOTE: This is fine for demonstration purposes, but this should be
    refactored before we deploy this app to production.
    Imagine how 100,000 users logging in and out of our app would affect
    the performance of this code!
    """
    users = User.objects.exclude(id=request.user.id).select_related('logged_in_user')
    for user in users:
        user.status = hasattr(user, 'logged_in_user')

    return render(request, 'user_list.html', {'users': users})


@login_required
def thread(request, username):
    """Thread page."""
    messages = []
    users = {}
    user = get_object_or_404(User, username=username)
    thread = Thread.objects.annotate(count=Count('users')).filter(users=request.user).filter(users=user).filter(count=2).first()
    if not thread:
        thread = Thread(name=', '.join([request.user.username, username]))
        thread.save()
        thread.users.add(request.user, user)
    else:
        messages = Message.objects.select_related('user').filter(thread=thread).order_by('date')[:100]
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
