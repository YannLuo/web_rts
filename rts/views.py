from django.shortcuts import render
from django.http import HttpResponse
from .control import process
import os
import json


def index(request):
    if request.method == "POST":
        process(request.body)
        return HttpResponse("ok")
    else:
        return HttpResponse("Hello world!")


def show_result(request):
    up, sha, down = request.path.split("/")[2:-1]
    with open(os.path.join("test_logs", up, sha, "%s.log" % (down,))) as rf:
        lines = rf.readlines()
    if request.method == "GET":
        return render(request, "test_log.html", {"log_path": request.path, "log": lines})
    elif request.method == "POST":
        content = '<br/>'.join(lines)
        return HttpResponse(json.dumps({"log": content}), content_type="application/json,charset=utf-8")
