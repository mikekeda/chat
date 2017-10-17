from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .models import Profile, Thread, UnreadThread, Message
from .forms import AvatarForm

User = get_user_model()


@login_required
def user_list(request):
    """User list."""
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    for user in users:
        try:
            user.status = user.profile.online()
        except Profile.DoesNotExist:
            Profile.objects.get_or_create(user=user)
            user.status = False

    return render(request, 'user_list.html', {'users': users})


@login_required
def profile_view(request, username):
    """User profile."""
    user = get_object_or_404(User, username=username)
    form = AvatarForm(data=request.POST)

    return render(request, 'profile.html', {
        'profile_user': user,
        'is_current_user': user == request.user,
        'form': form,
    })


@login_required
def thread_view(request, username=None, thread_id=None):
    """Thread page."""
    interlocutor = None
    if username:
        interlocutor = get_object_or_404(User, username=username)
        thread = Thread.objects\
            .annotate(count=Count('users'))\
            .filter(users=request.user)\
            .filter(users=interlocutor)\
            .filter(count=2)\
            .first()
        if not thread:
            thread = Thread(name=', '.join([request.user.username, username]))
            thread.save()
            thread.users.add(request.user, interlocutor)
    elif thread_id:
        thread = get_object_or_404(Thread, pk=thread_id)
    else:
        # username or thread_id should be passed.
        raise Http404

    # The user visited this tread - delete user's unread thread.
    UnreadThread.objects.filter(thread=thread, user=request.user).delete()

    users = {}
    for user in thread.users.all():
        profile, _ = Profile.objects.get_or_create(user=user)
        users[user.pk] = {
            'username': user.username,
            'avatar': profile.avatar.url,
        }

    messages = Message.objects.select_related('user').filter(thread=thread)\
                   .order_by('date')[:50]
    for message in messages:
        if message.user.pk not in users:
            try:
                avatar = message.user.profile.avatar.url
            except Profile.DoesNotExist:
                # If there no user profile - create it.
                profile, _ = Profile.objects.get_or_create(user=message.user)
                avatar = profile.avatar.url

            users[message.user.pk] = {
                'username': message.user.username,
                'avatar': avatar,
            }
    for message in messages:
        message.avatar = users[message.user.pk]['avatar']

    return render(request, 'thread.html', {
        'thread': thread,
        'messages': messages,
        'users': users,
        'interlocutor': interlocutor,
    })


@login_required
def call_view(request, username):
    """Call page."""
    interlocutor = get_object_or_404(User, username=username)

    return render(request, 'call.html', {
        'interlocutor': interlocutor,
    })


@login_required
def update_profile(request):
    """Update user."""
    if request.method == 'POST':
        avatar = request.FILES.get('avatar', '')
        if avatar:
            profile = get_object_or_404(Profile, user=request.user)
            form = AvatarForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            allowed_fields = ['first_name', 'last_name', 'email']
            field = request.POST.get('name', '')
            value = request.POST.get('value', '')
            if field and field in allowed_fields:
                setattr(request.user, field, value)
                try:
                    request.user.clean_fields()
                    request.user.save()
                    return JsonResponse({'success': True})
                except ValidationError as e:
                    return JsonResponse(
                        ', '.join(e.message_dict[field]),
                        safe=False,
                        status=422
                    )

    return JsonResponse(
        _("You can't change this field"),
        safe=False,
        status=403
    )


def log_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('core:user_list'))

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
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)

            return redirect(reverse('core:user_list'))

    return render(request, 'signup.html', {'form': form})
