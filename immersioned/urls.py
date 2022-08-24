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
    path('aluser/', views.ListUserView.as_view(), name='aluser'),
    path('aduser/<int:pk>', views.ADeleteuser.as_view(), name='aduser'),
    path('icourse/', views.icourse, name='icourse'),
    path('icourse2/', views.icourse, name='icourse2'),
    # Instructor URLs
    path('instructor/', views.home_instructor, name='instructor'),
    path('quiz_add/', views.QuizCreateView.as_view(), name='quiz_add'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('post/',views.add_tutorial, name='publish_tutorial'),
    path('itutorial/', views.itutorial, name='itutorial'),
    path('itutorials/<int:pk>/', views.ITutorialDetail.as_view(), name = "itutorial-detail"),
    # Student URLs
    path('learner/', views.home_learner, name='learner'),
    path('ltutorial/',views.ltutorial, name='ltutorial'),
    path('tutorials/<int:pk>/', views.LTutorialDetail.as_view(), name = "tutorial-detail"),
    path('interests/', views.LearnerInterestsView.as_view(), name='interests'),
    path('llistnotes/', views.LLNotesList.as_view(), name='llnotes'),
    path('ladd_notes/', views.student_add_notes, name='ladd_notes'),
    path('lpublish_notes/', views.student_publish_notes, name='lpublish_notes'),
    path('update_file/<int:pk>', views.student_update_file, name='update_file'),
]