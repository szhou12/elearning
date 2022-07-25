from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
#from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404
#from .models import Customer, Profile
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Avg, Count, Sum
from django.forms import inlineformset_factory
from .models import TakenQuiz, Profile, Quiz, Question, Answer, Learner, User, Course, Tutorial, Notes, Announcement
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm, PasswordChangeForm)

from django.contrib.auth import update_session_auth_hash

from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)

from .forms import (LearnerSignUpForm, InstructorSignUpForm, PostForm)
# from .forms import (TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, 
#                     BaseAnswerInlineFormSet, LearnerInterestsForm, LearnerCourse, UserForm, ProfileForm, PostForm)

# Create your views here.
# Shared Views

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'service.html')

def contact(request):
    return render(request, 'contact.html')

def login_form(request):
    return render(request, "login.html")

def loginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            # redirect to admin/instrustor/learner page by login type
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
            elif user.is_instructor:
                return redirect('instructor')
            elif user.is_learner:
                return redirect('learner')
            else:
                return redirect('login_form')
        else:
            messages.info(request, "Invalid username or password")
            return redirect('login_form')

def logoutView(request):
    logout(request)
    return redirect('home')

# Learner Views
class LearnerSignUpView(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        # specify user type as learner
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save() # save registration info
        login(self.request, user)

        # Once a leaner succesfully fills up all required registration info,
        # web page will be redirected to home page
        return redirect('home')
        # return redirect('learner')


# Admin Views
def dashboard(request):
    return render(request, 'dashboard/admin/home.html')


class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'dashboard/admin/signup_form.html'

    def get_context_data(self, **kwargs):
        # specify user type as instructor
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save() # save registration info
        messages.success(self.request, 'Instructor Added Successfully')

        # Once a leaner succesfully fills up all required registration info,
        # web page will be redirected to home page
        return redirect('isign') # instructor sign-in


class AdminLearner(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/admin/learner_signup_form.html'

    def get_context_data(self, **kwargs):
        # specify user type as learner
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save() # save registration info
        messages.success(self.request, 'Learner Added Successfully')

        # Once a leaner succesfully fills up all required registration info,
        # web page will be redirected to home page
        return redirect('addlearner') # learner sign-in
    

def course(request):
    if request.method == 'POST':
        name = request.POST['name']
        color = request.POST['color']

        a = Course(name=name, color=color)
        a.save()
        messages.success(request, 'A New Course Registered Successfully')
        return redirect('course')
    else:
        return render(request, 'dashboard/admin/course.html')


class AdminCreatePost(CreateView):
    model = Announcement
    form_class = PostForm
    template_name = 'dashboard/admin/post_form.html'
    success_url = reverse_lazy('dashboard') # when admin successfully post an annoucement, they will be redirected to dashboard page

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class ListUserView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')

class ADeleteuser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('aluser')
    success_message = "User Deleted Successfully"


# Instructor Views
def home_instructor(request):
    return render(request, 'dashboard/instructor/home.html')

class QuizCreateView(CreateView):
    model = Quiz
    template_name = 'dashboard/instructor/quiz_add_form.html'
    fields = ('name', 'course')

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'Quiz Created, Add Questions Next')
        # return redirect('quiz_change', quiz.pk)
        return redirect('instructor')