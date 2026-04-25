from django.shortcuts import render


def landing_view(request):
    return render(request, 'landing.html')


def login_view(request):
    return render(request, 'auth/login.html')


def register_view(request):
    return render(request, 'auth/register.html')


def feed_view(request):
    return render(request, 'app/feed.html')


def hobbies_view(request):
    return render(request, 'app/hobbies.html')


def profile_view(request, user_id=None):
    return render(request, 'app/profile.html')


def edit_profile_view(request):
    return render(request, 'app/edit_profile.html')


def post_detail_view(request, pk):
    return render(request, 'app/post_detail.html')
