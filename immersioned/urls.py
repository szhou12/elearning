from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Shared URLs
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('lsign/', views.LearnerSignUpView.as_view(), name='lsign'), # convert class obj to fcn
    path('login/', views.loginView, name='login'),
    path('login_form/', views.login_form, name='login_form'),
    path('logout/', views.logoutView, name='logout'),
    # Admin URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/', views.course, name='course'),
    path('isign/', views.InstructorSignUpView.as_view(), name='isign'),
    path('addlearner/', views.AdminLearner.as_view(), name='addlearner'),
    path('apost/', views.AdminCreatePost.as_view(), name='apost'),
    # Instructor URLs
    path('instructor/', views.home_instructor, name='instructor'),
    path('quiz_add/', views.QuizCreateView.as_view(), name='quiz_add'),
]