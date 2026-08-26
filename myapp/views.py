from django.shortcuts import render


def application_success(request):
    return render(request, 'myapp/application_success.html')

def index_view(request):
    return render(request, 'myapp/index.html')

def about_view(request):
    return render(request, 'myapp/about.html')

def contact_view(request):
    return render(request, 'myapp/contact.html')

def admin_view(request):
    return render(request, 'myapp/admin.html')

def donate_view(request):
    return render(request, 'myapp/donate.html')

def gallery_view(request):
    return render(request, 'myapp/gallery.html')

def privacy_view(request):
    return render(request, 'myapp/privacy.html')

def program_view(request):
    return render(request, 'myapp/programs.html')

def quicklinks_view(request):
    return render(request, 'myapp/quicklinks.html')

def request_view(request):
    return render(request, 'myapp/request.html')

def stories_view(request):
    return render(request, 'myapp/stories.html')

def terms_view(request):
    return render(request, 'myapp/terms.html')

def volunteer_view(request):
    return render(request, 'myapp/volunteer.html')

def login_view(request):
    return render(request, 'myapp/login.html')

def dash_view(request):
    return render(request, 'myapp/dash.html')

def logout_view(request):
    from django.shortcuts import redirect
    return redirect('index')

def register_view(request):
    return render(request, 'myapp/register.html')
