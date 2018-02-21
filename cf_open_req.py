from Request import Request
from cfparser import *
import requests
import csv
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
import numpy as np

men_base_url_2017 = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2017/leaderboards?division=1&region=0&scaled=0&sort=0&occupation=0&page='
men_base_url_2018 = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2018/leaderboards?division=1&region=0&scaled=0&sort=0&occupation=0&page='
women_base_url_2018 = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2018/leaderboards?division=2&region=0&scaled=0&sort=0&occupation=0&page='

pages = []
def build_urls(page_num):
	for i in range(page_num):
		pages.append(men_base_url_2017 + str(i))

def get_pages_2017():
    page = requests.get(men_base_url_2017 + '1')
    return page.json()['totalpages']

def get_pages_2018():
    page = request.get(men_base_url_2018 + '1')
    return page.json()['pagination']['totalPages']

async def get_results():
    # start all the requests, so they all can eat network at the same time
    reqs = [Request(page) for page in pages]
    athletes = []
    for req in reqs:
        await req
        aths = parse_aths_2017(req)
        for ath in aths:
            athletes.append(ath)
    return athletes
 
def runner(coro):
    try:
        while True:
            coro.send(None)
    except StopIteration as val:
        return val.value
 
def get_results_base():
    return runner(get_results())

def write_csv(athletes):
    results = []
    with open('2017.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['Name', 'Score1', 'Score2', 'Score3', 'Score4', 'Score5']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for ath in athletes:
            res = parse_results_2017(ath)
            results.append(res)
            writer.writerow({'Name': res['name'], 'Score1': res['scores'][0], 'Score2': res['scores'][1],
                'Score3': res['scores'][2], 'Score4': res['scores'][3], 'Score5': res['scores'][4]})
    return results

def plot_scores(workout_num, results):
    data1 = np.array([ath['scores'][workout_num-1] for ath in results ]).astype(np.float)
    mu = np.mean(data1)
    sigma = np.std(data1)
    # get best fit for data
    lower = mu - 4*sigma
    upper = mu + 4*sigma
    x = np.linspace(lower, upper, 1000)
    pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
    hist, edges = np.histogram(data1[~np.isnan(data1)], density=True, bins=100)
    p1 = figure(title='2017 open workouts', background_fill_color='#E8DDCB')
    p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
        fill_color="#036564", line_color="#033649")
    p1.line(x, pdf, line_color="#D95B43", line_width=8, alpha=0.7)
    output_file('histogram.html')
    show(p1)

if __name__ == "__main__":
    print('start')
    # need to loop through the pages
    num_pages = get_pages_2017()
    build_urls(1000)
    athletes = get_results_base()
    results = write_csv(athletes)
    plot_scores(5, results)
    print('end')
