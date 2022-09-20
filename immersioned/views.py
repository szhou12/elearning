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
import csv
import json
from . import models

from .forms import (LearnerSignUpForm, LearnerInterestsForm, InstructorSignUpForm, PostForm)
# from .forms import (TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, 
#                     BaseAnswerInlineFormSet, LearnerInterestsForm, LearnerCourse, UserForm, ProfileForm, PostForm)

# Create your views here.


#################### Shared Views ####################
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



#################### Admin Views ####################
def dashboard(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()
    admin_context = {'learner':learner, 'course':course, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/admin/home.html', context=admin_context)


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

        # Once a learner succesfully fills up all required registration info,
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

def icourse(request):
    return render(request, 'dashboard/admin/icourse.html')

def icourse2(request):
    return render(request, 'dashboard/admin/icourse2.html')


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




#################### Instructor Views ####################
def home_instructor(request):
    # return render(request, 'dashboard/instructor/home.html')
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()
    instructor_context = {'learner':learner, 'course':course, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/instructor/home.html', context=instructor_context)

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

def tutorial(request):
    courses = Course.objects.only('id', 'name')
    courses_context = {'courses': courses}
    return render(request, 'dashboard/instructor/tutorial.html', context=courses_context)

def add_tutorial(request):
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        content = request.POST['content']
        thumb = request.FILES['thumb']
        current_user = request.user
        author_id = current_user.id
        # print(author_id)
        # print(course_id)
        new_tutorial = Tutorial(title=title, content=content, thumb=thumb, user_id=author_id, course_id=course_id)
        new_tutorial.save()
        messages.success(request, 'New Tutorial Added Successfully!')
        return redirect('tutorial')
    else:
        messages.error(request, "Failed to Add a New Tutorial")
        return redirect('tutorial')


def itutorial(request):
    tutorials = Tutorial.objects.all().order_by('-created_at')
    tutorials = {'tutorials':tutorials}
    return render(request, 'dashboard/instructor/list_tutorial.html', tutorials)

def sample_data(request):
    return render(request,'dashboard/instructor/sample_data.html')

def sample_data2(request):
    file = Notes.objects.get(pk=1)
    game_data = json.loads(file.data)
    data = {}

    data["gd"] = game_data[1:]
    return render(request,'dashboard/instructor/sample_data2.html', context=data)

class ITutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/instructor/tutorial_detail.html'


class LNotesList(ListView):
    model = Notes
    template_name = 'dashboard/instructor/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4


    def get_queryset(self):
        return Notes.objects.order_by('-id')



#################### Student Views ####################
def home_learner(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()

    context = {'learner':learner, 'course':course, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/learner/home.html', context=context)


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
        # web page will be redirected to student/learner page
        return redirect('learner')


def ltutorial(request):
    ## List tutorials only with course_id selected by the learner

    current_user = request.user

    # selected_course_ids = current_user.learner.interests.values_list('id', flat=True)
    selected_course = current_user.learner.interests.all()
    # print(selected_course)

    tutorials = Tutorial.objects.filter(course__in=selected_course).order_by('-created_at')
    # tutorials = Tutorial.objects.all().order_by('-created_at')

    tutorials = {'tutorials':tutorials}
    return render(request, 'dashboard/learner/list_tutorial.html', tutorials)


class LTutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/learner/tutorial_detail.html'



class LearnerInterestsView(UpdateView):
    model = Learner
    form_class = LearnerInterestsForm
    template_name = 'dashboard/learner/interests_form.html'
    # success_url = reverse_lazy('lquiz_list')
    # success_url = reverse_lazy('learner')
    success_url = reverse_lazy('interests')

    def get_object(self):
        return self.request.user.learner

    def form_valid(self, form):
        messages.success(self.request, 'Course Updated Successfully')
        return super().form_valid(form)



class LLNotesList(ListView):
    model = Notes
    template_name = 'dashboard/learner/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4


    def get_queryset(self):
        return Notes.objects.order_by('-id')


def student_add_notes(request):
    current_user = request.user
    selected_course = current_user.learner.interests.all().only('id', 'name')

    # courses = Course.objects.only('id', 'name')

    context = {'courses':selected_course}
    return render(request, 'dashboard/learner/add_notes.html', context)


def parse_file(f):
    file_data = f.read().decode("utf-8")
    result = []
    lines = file_data.split("\r\n")	
    
    for line in lines:
        row = line.split(",")
        result.append(row)

    return result


def student_publish_notes(request):
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        cover = request.FILES['cover']

        file = request.FILES['file'] # TODO: add a helper function that parse & store file
        game_data = json.dumps(parse_file(file))

        current_user = request.user
        user_id = current_user.id

        note = Notes(title=title, cover=cover, file=file, user_id=user_id, course_id=course_id, data=game_data)
        note.save()
        messages.success = (request, 'File Uploaded Successfully')
        return redirect('llnotes')
    else:
        messages.error = (request, 'Upload Failed')
        return redirect('ladd_notes')


def student_update_file(request, pk):
    if request.method == 'POST':

        file = request.FILES['file'] # TODO: add a helper function that parse & store file
        file_name = request.FILES['file'].name

        
        game_data = json.dumps(parse_file(file))

        fs = FileSystemStorage()
        file = fs.save(file.name, file)
        fileurl = fs.url(file)
        file = file_name
        # print(file)

        Notes.objects.filter(id = pk).update(file = file)
        Notes.objects.filter(id = pk).update(data = game_data)
        messages.success = (request, 'Notes was updated successfully!')
        return redirect('llnotes')
    else:
        return render(request, 'dashboard/learner/update.html')