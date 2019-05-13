from django.db import models
import os


class Diff(object):
    def __init__(self, src_file, tar_file, hunk_infos):
        self.src_file = src_file
        self.tar_file = tar_file
        self.hunk_infos = hunk_infos

    def __str__(self):
        return f"Diff <src_file: {self.src_file}  tar_file: {self.tar_file}  hunk_infos: {self.hunk_infos}>"

    def __repr__(self):
        return f"Diff <src_file: {self.src_file}  tar_file: {self.tar_file}  hunk_infos: {self.hunk_infos}>"


class FunctionDef(object):
    def __init__(self):
        self.file = None
        self.name = None
        self.start_lineno = 0

    def __str__(self):
        return f'FunctionDef<file: {self.file}  name: {self.name}  lineno: {self.start_lineno}>'

    def __repr__(self):
        return f'FunctionDef<file: {self.file}  name: {self.name}  lineno: {self.start_lineno}>'

    def __lt__(self, other):
        return self.start_lineno < other.start_lineno
