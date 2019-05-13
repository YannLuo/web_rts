import json
import requests
from .utils import get_modified_functions, select_relevant_downstreams
import subprocess
import os


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Accept": "application/vnd.github.VERSION.diff",
    "Host": "api.github.com",
}
NUMPY_URL_TPL = "https://api.github.com/repos/numpy/numpy/commits/%s"


def get_new_commit(body):
    j = json.loads(body)
    return j["after"]


def get_diff(sha):
    resp = requests.get(NUMPY_URL_TPL % (sha, ), headers=HEADERS)
    return resp.text


def run_regression(relevant_downstreams, sha):
    downstream_test_drivers = os.listdir("numpy_test_drivers")
    try:
        os.makedirs(os.path.join("test_logs", "numpy", sha))
    except:
        pass
    for downstream_test_driver in downstream_test_drivers:
        downstream_name = "_".join(downstream_test_driver.split('.')[0].split("_")[1:])
        if downstream_name not in relevant_downstreams:
            continue
        if downstream_name == "alphalens":
            continue
        if downstream_name == "joblib":
            continue
        if downstream_name == "dask":
            continue
        if downstream_name == "numpy_buffer":
            continue
        if downstream_name == "indi":
            continue
        pyfile_path = os.path.join("test_numpy", downstream_test_driver)
        with open(os.path.join("test_logs", "numpy", sha,
                               "test_log_" + downstream_name + ".txt"), mode="w") as wf:
            p = subprocess.Popen(["python3", pyfile_path], stdout=wf, stderr=wf)
            try:
                p.communicate(timeout=12600)
            except:
                p.kill()


def process(request):
    body = str(request.body, encoding="utf-8")
    new_commit = get_new_commit(body)
    diff_content = get_diff(new_commit)
    modified_functions = get_modified_functions(diff_content)
    relevant_downstreams = select_relevant_downstreams(modified_functions)
    return "\n".join(relevant_downstreams)
