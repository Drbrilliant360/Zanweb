from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),                                # http://127.0.0.1:8000/
    path('about/', views.about_view, name='about'),                          # http://127.0.0.1:8000/about/
    path('contact/', views.contact_view, name='contact'),                    # http://127.0.0.1:8000/contact/
    path('admin-workspace/', views.admin_view, name='admin_ws'),             # http://127.0.0.1:8000/admin-workspace/
    path('dash/', views.dash_view, name='dash'),                             # http://127.0.0.1:8000/dashboard/
    path('donate/', views.donate_view, name='donate'),                      # http://127.0.0.1:8000/donate/
    path('gallery/', views.gallery_view, name='gallery'),                    # http://127.0.0.1:8000/gallery/
    path('login/', views.login_view, name='login'),                          # http://127.0.0.1:8000/login/                 # http://127.0.0.1:8000/partners/
    path('privacy/', views.privacy_view, name='privacy'),                    # http://127.0.0.1:8000/privacy/
    
    # --- New File Routing Anchors ---
    path('programs/', views.program_view, name='programs'),                  # http://127.0.0.1:8000/programs/ 
    
    # 🟢 Set to /signup/ and linked cleanly to register_view
    path('register/', views.register_view, name='register'),                  # http://127.0.0.1:8000/signup/
    
    path('request/', views.request_view, name='request'),                    # http://127.0.0.1:8000/request/
    path('stories/', views.stories_view, name='stories'),                    # http://127.0.0.1:8000/stories/
    path('terms/', views.terms_view, name='terms'),                          # http://127.0.0.1:8000/terms/
    
    # 🟢 Set to /volunteer/ and linked cleanly to volunteer_view
    path('volunteer/', views.volunteer_view, name='volunteer'),              # http://127.0.0.1:8000/volunteer/
    path('events/', views.events_view, name='events'),                      # http://127.0.0.1:8000/events/

    path('logout/', views.logout_view, name='logout'),
    path('application-success/', views.application_success, name='application_success'),
    path('quicklinks/', views.quicklinks_view, name='quicklinks'),

    # ---- Password reset flow ----
    # Step 1: user requests a reset link by entering their email
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='myapp/password_reset.html',
            email_template_name='myapp/password_reset_email.html',
            subject_template_name='myapp/password_reset_subject.txt',
            success_url='/password-reset/done/',
        ),
        name='password_reset',
    ),

    # Step 2: confirmation that the email was sent
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='myapp/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    # Step 3: link from the email — lets the user set a new password
    path(
        'password-reset/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='myapp/set new pass.html',
            success_url='/password-reset/complete/',
        ),
        name='password_reset_confirm',
    ),

    # Step 4: success page
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='myapp/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]