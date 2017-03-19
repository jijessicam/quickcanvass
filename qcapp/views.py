from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

import hashlib
import random

from utils import *
# Create your views here.

def login(request):
	return render(request, 'login.html')

def signup(request):
	return render(request, 'signup.html')

@csrf_exempt
def makeaccount(request, methods=['POST']):
	#wow here's where we acutally upload the stuff to the db
	data = request.POST
	print("test", data.get('email'), data.get('passw'), data.get('isdirector'))
	#create a random 16 character salt for passwords
	salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
	hashed_pass = hashit(data.get('passw') + salt)
	print(hashed_pass)
	return redirect('/login')

def about(request):
    return render(request, 'about.html')

def research(request):
    return render(request, 'research.html')

def contact(request):
    return render(request, 'contact.html')

def search(request):
	return render(request, 'search.html')

def volunteerdash(request):
	return render(request, 'volunteerdash.html')