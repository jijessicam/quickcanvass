from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

def login(request):
    return render(request, 'login/index.html')

def signup(request):
	return render(request, 'login/signup.html')

@csrf_exempt
def makeaccount(request, methods=['POST']):
	#wow here's where we acutally upload the stuff to the db
	data = request.POST
	print("test", data.get('email'), data.get('passw'), data.get('isdirector'))
	return redirect('/login/signup')
