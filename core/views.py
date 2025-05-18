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







def index(request):

    return render(request, 'core/index.html')




def team(request):
    return render(request, 'core/team.html')

def prospectus(request):
    return render(request, 'core/prospectus.html')



