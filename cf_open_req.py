import requests
import threading

men_base_url_2017 = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2017/leaderboards?division=1&region=0&scaled=0&sort=0&occupation=0&page='
pages = []
def build_urls(page_num):
	for i in range(page_num):
		pages.append(men_base_url_2017 + str(i))

def parse_results_2018(json_data):
	num_pages = json_data['pagination']['totalPages']
	for row in json_data['leaderboardRows']:
		person = row['entrant']
		scores = row['scores']
		print(person['competitorName'])
		for wod in scores:
			print(wod['scaled'] + '  ' + wod['score'])

def parse_results_2017(json_data):
	for athlete in json_data['athletes']:
		name = athlete['name']
		print(name)

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
            self.content = page.json()
 
    def __await__(self):
        yield
        self.thread.join()
        with self.lock:
            return self.content
 
async def get_results():
    # start all the requests, so they all can eat network at the same time
    reqs = [Request(page) for page in pages]
    athletes = 0
    for req in reqs:
        await req
        athletes += len(req.content['athletes'])
    return athletes
 
def runner(coro):
    try:
        while True:
            coro.send(None)
    except StopIteration as val:
        return val.value
 
def get_results_base():
    return runner(get_results())
 
if __name__ == "__main__":
	build_urls(100)
	print("Async return value: {0}".format(get_results_base()))
