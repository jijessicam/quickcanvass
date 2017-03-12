from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

def about(request):
    return render(request, 'login/about.html')
def index(request):
        return render(request, 'search/index.html')
