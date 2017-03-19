from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

def index(request):
    return render(request, 'login/index.html')
<<<<<<< HEAD

def signup(request):
	return render(request, 'login/signup.html')

@csrf_exempt
def makeaccount(request, methods=['POST']):
	#wow here's where we acutally upload the stuff to the db
	data = request.POST
	print("test", data.get('email'), data.get('passw'), data.get('isdirector'))
	return redirect('/login/signup')
=======
>>>>>>> 9115f1291f39d876e567becad2426e3051e58cfa
