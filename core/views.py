import json
import uuid
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from core.project import settings
from django.http import JsonResponse
from django.db.models import Q
import openai
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import user_passes_test
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.core.exceptions import PermissionDenied

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)





def index(request):

    return render(request, 'core/index.html')


def about(request):

    return render(request, 'core/about.html')

def admission(request):

    return render(request, 'core/admission.html')

def gallery(request):

    return render(request, 'core/gallery.html')

def media(request):
    return render(request, 'core/media.html')

def team(request):
    return render(request, 'core/team.html')

def prospectus(request):
    return render(request, 'core/prospectus.html')

from django.views.generic import ListView, DetailView
from .models import Blog

class BlogListView(ListView):
    model = Blog
    template_name = 'core/blog_list.html'
    context_object_name = 'blogs'
    ordering = ['-date_posted']
    paginate_by = 6  # Show 6 blogs per page

class BlogDetailView(DetailView):
    model = Blog
    template_name = 'core/blog_list.html'
    context_object_name = 'blog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

from django.views.generic import CreateView
from .forms import BlogForm

from django.http import JsonResponse
from django.template.loader import render_to_string

class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/blog_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = {
                'success': True,
                'message': 'Blog created successfully!',
                'redirect_url': self.get_success_url()
            }
            return JsonResponse(data)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('blog_list')
    

openai.api_key = settings.OPENAI_API_KEY

school_info = """
Paterson Park Primary School is a Seventh-day Adventist primary school located in Orange Grove, Johannesburg. 
The school exists to educate primary school-aged students (grades R–7) to the best of our ability. 
The school's values are expressed in its Vision and Mission statements.
We believe it is our privilege and responsibility to provide Christian education for our children and those in the community; to foster their moral and spiritual development; to encourage their creative ability as well as their ability to think clearly and logically; and to teach them the responsibilities and privileges of good citizenship and service to God, their church, their country, and their fellow humanity.

Our Mission
Paterson Park School is committed to deliver a holistic education which concentrates on developing their pupils' spiritual, cognitive, social, emotional and physical abilities in an inclusive, non-discriminatory milieu.

Our vision We aim to provide a safe, secure and stimulating environment in which our pupils can develop their full potential.
We aim to provide a curriculum which is relevant, appropriate and challenging, and which meets the needs of all our pupils.

Academic Excellence
We offer CAPS Curriculum as prescribed by the GDE. In addition to this we offer Bible as a subject.

96% pass average in the last five years
Personal online learning account with My Cyberwall
Balanced environment where natural abilities are challenged
Art Exhibition
Curriculum
We offer a comprehensive curriculum that develops the whole child.

Bible
Mathematics
English
Life Skills & Life Orientation
EMS & Social Sciences
Natural Sciences & Technology
Creative Arts
IsiZulu and Afrikaans
Technology Fair
Student Development
Paterson Park School gives learners opportunities to:

Develop academic excellence
Mature in physical skills
Make positive social adjustments
Build lasting peer relationships
Cultivate critical thinking
Grow in Christian values
Create a sense of pride
Feel secure and nurtured
"""

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        prompt = f"{school_info}\n\nVisitor: {user_message}\nChatbot:"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot that answers questions about Bright Future High School."},
                {"role": "user", "content": prompt}
            ]
        )

        answer = response['choices'][0]['message']['content']
        return JsonResponse({'response': answer})