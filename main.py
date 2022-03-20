from bottle import route, run, template, post, request
import youtube_dl
import threading

class thread(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

# Need to manage a threadpool outside of the scope of the routing definitions.
thread1 = thread("")

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@post('/post')
def post_endpoint():
    global thread1
    url = request.json["url"]
    thread1.url = url
    thread1.start()
    return request.json

run(host='localhost', port=8080)
