from django.shortcuts import render
from django.http import HttpResponse
from .control import process


def index(request):
    if request.method == "POST":
        return HttpResponse(process(request))
    else:
        return HttpResponse("Hello world!")
