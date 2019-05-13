import os
import ast
import json
import astor
from unidiff import PatchSet
from .models import Diff, FunctionDef
from .config import DOWNSTREAM_REPOS


UPSTREAM_REPO_PATH = os.path.join('repos', 'numpy')


def read_callgraph(repo: str):
    with open(os.path.join("callgraph", "method_level", "%s_callgraph.json" % (repo, )), mode="r", encoding="utf-8") as rf:
        callgraph = json.load(rf)
    with open(os.path.join("callgraph", "method_level", "%s_rev_callgraph.json" % (repo, )), mode="r", encoding="utf-8") as rf:
        rev_callgraph = json.load(rf)
    return callgraph, rev_callgraph


def dump_one_hunk(hunk):
    src_st_lineno = hunk.source_start
    tar_st_lineno = hunk.target_start
    d_cnt = 0
    delete_linenos = []
    a_cnt = 0
    add_linenos = []
    for line in hunk.source:
        if line.startswith('-'):
            delete_linenos.append(src_st_lineno + d_cnt)
            d_cnt += 1
        else:
            d_cnt += 1
    for line in hunk.target:
        if line.startswith('+'):
            add_linenos.append(tar_st_lineno + a_cnt)
            a_cnt += 1
        else:
            a_cnt += 1
    delete_linenos = sorted(delete_linenos)
    add_linenos = sorted(add_linenos)
    return {
        "d": delete_linenos,
        "a": add_linenos
    }


def dump_one_patch(patch):
    src_file = patch.source_file
    tar_file = patch.target_file
    delete_linenos = []
    add_linenos = []
    for hunk in patch:
        hunk_info = dump_one_hunk(hunk)
        delete_linenos.extend(hunk_info["d"])
        add_linenos.extend(hunk_info["a"])
    modify_info = {
        "d": delete_linenos,
        "a": add_linenos
    }
    return Diff(src_file, tar_file, modify_info)


def parse_diff(diff):
    patches = PatchSet(diff)
    diff = []
    for patch in patches:
        patch_info = dump_one_patch(patch)
        diff.append(patch_info)
    return diff


def collect_functiondef(fp: str):
    root = astor.parse_file(fp)
    with open(fp, mode='r', encoding='utf-8') as rf:
        lines = rf.readlines()
    line_cnt = len(lines)
    functiondef_list = []
    for node in root.body:
        if isinstance(node, ast.FunctionDef):
            entry = FunctionDef()
            entry.file = fp
            entry.name = node.name
            entry.start_lineno = node.lineno
            functiondef_list.append(entry)
        elif isinstance(node, ast.ClassDef):
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    entry = FunctionDef()
                    entry.file = fp
                    entry.name = n.name
                    entry.start_lineno = n.lineno
                    functiondef_list.append(entry)
    EOF_entry = FunctionDef()
    EOF_entry.file = fp
    EOF_entry.name = '__EOF__'
    EOF_entry.start_lineno = line_cnt + 1
    functiondef_list.append(EOF_entry)
    return sorted(functiondef_list)


def get_modified_functions(diff_content):
    diff_infos = parse_diff(diff_content)
    mod_functiondef_list = set()
    for diff in diff_infos:
        tar_file_path = diff.tar_file[2:]
        if tar_file_path.endswith('.py'):
            tar_module = '.'.join(tar_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(
                os.path.join(UPSTREAM_REPO_PATH, tar_file_path))
            for add_lineno in diff.hunk_infos["a"]:
                for i in range(len(functiondef_list) - 1):
                    if functiondef_list[i].start_lineno <= add_lineno < functiondef_list[i + 1].start_lineno:
                        mod_functiondef_list.add(
                            (tar_module, functiondef_list[i].name))
        src_file_path = diff.src_file[2:]
        if src_file_path.endswith('.py'):
            src_module = '.'.join(src_file_path[:-3].split('/'))
            functiondef_list = collect_functiondef(
                os.path.join(UPSTREAM_REPO_PATH, src_file_path))
            for del_lineno in diff.hunk_infos["d"]:
                for i in range(len(functiondef_list) - 1):
                    if functiondef_list[i].start_lineno <= del_lineno < functiondef_list[i + 1].start_lineno:
                        mod_functiondef_list.add(
                            (src_module, functiondef_list[i].name))
    return mod_functiondef_list


def select_relevant_downstreams(modified_functions):
    relevant_downstreams = set()
    for downstream in DOWNSTREAM_REPOS:
        _, rev_callgraph = read_callgraph(downstream)
        f = False
        for prefix_namespace, name in modified_functions:
            for cur_call in rev_callgraph.keys():
                if cur_call.startswith(prefix_namespace + ".") and \
                        cur_call.split('.')[-1] == name and \
                        downstream not in relevant_downstreams and \
                        downstream != "numpy":
                    f = True
                    relevant_downstreams.add(downstream)
                    break
            if f:
                break
    return relevant_downstreams
