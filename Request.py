import requests
import threading
import json

class Request:
    def __init__(self, url):
        self.url = url
        self.content = None
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._callback)
        self.thread.start()
 
    def _callback(self):
        page = requests.get(self.url)
        with self.lock:
            try:
                self.content = page.json()
            except json.decoder.JSONDecodeError as err:
                self.content = {}
            
 
    def __await__(self):
        yield
        self.thread.join()
        with self.lock:
            return self.content
