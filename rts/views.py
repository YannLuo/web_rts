from django.shortcuts import render
from django.http import HttpResponse
from .control import process


def index(request):
    if request.method == "POST":
        process(request)
        return "ok"
    else:
        return HttpResponse("Hello world!")
