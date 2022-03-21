from bottle import route, run, template, post, request
import youtube_dl
import threading
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
thread_pool = [thread("")] * 2

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@post('/post')
def post_endpoint():
    global thread_pool
    url = request.json["url"]
    selected_thread = None
    for t in thread_pool:
        if not t.is_alive():
            t = thread(url)
            selected_thread = t
            break
    if selected_thread is None:
        return {"error": "no resources available, please try again later"}
    selected_thread.start()
    return request.json

run(host='localhost', port=8080)
