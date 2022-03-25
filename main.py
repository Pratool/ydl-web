from bottle import route, run, template, post, request
from  bottle import static_file
import glob
import youtube_dl
import threading
import time
from uuid import uuid4

class thread(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
        self.id = str(uuid4())

    def run(self):
        ydl_opts = {"outtmpl": f"{self.id}.%(ext)s"}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

# Need to manage a threadpool outside of the scope of the routing definitions.
thread_pool = [None] * 16

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/download/<uuid>')
def download(uuid):
    possible_paths = glob.glob(f"{uuid}*")
    if len(possible_paths) == 0:
        return {"error": f"{uuid} download not found"}
    for path in possible_paths:
        if path[-1:-6] == ".part":
            return {"error": "{uuid} has not completed downloading"}
        else:
            break
    return static_file(path, root="/home/pratool/home/ydl-web/ydl-web")

@post('/post')
def post_endpoint():
    global thread_pool
    url = request.json["url"]
    idx = 0
    while idx < len(thread_pool):
        t = thread_pool[idx]
        if t is None or not t.is_alive():
            break
        idx += 1
    if idx >= len(thread_pool):
        return {"error": "no resources available, please try again later"}
    thread_pool[idx] = thread(url)
    thread_pool[idx].start()
    return request.json

run(host='localhost', port=8080)
