from Request import Request
from cfparser import *
import requests
import csv
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
import numpy as np
import time
import json

men_base_url_2017 = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2017/leaderboards?division=1&region=0&scaled=0&sort=0&occupation=0&page='

men_base_url_2018 = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2018/leaderboards?division=1&region=0&scaled=0&sort=0&occupation=0&page='
women_base_url_2018 = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2018/leaderboards?division=2&region=0&scaled=0&sort=0&occupation=0&page='
men_base_url_2018_scaled = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2018/leaderboards?division=1&region=0&scaled=1&sort=0&occupation=0&page='
women_base_url_2018_scaled = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2018/leaderboards?division=2&region=0&scaled=1&sort=0&occupation=0&page='

pages = []

def build_urls(start, num, division):
    pages.clear() # clear out previous pages
    base_url = ''
    if division == 'men':
        base_url = men_base_url_2018;
    elif division == 'women':
        base_url = women_base_url_2018;
    elif division == 'men-s':
        base_url = men_base_url_2018_scaled;
    elif division == 'women-s':
        base_url = women_base_url_2018_scaled;
    
    for i in range(start, start + num):
        pages.append(base_url + str(i))


def get_pages_2018(division):
    num_pages = 0
    url = ''
    if division == 'men':
        url = men_base_url_2018
    elif division == 'women':
        url = women_base_url_2018
    elif division == 'men-s':
        url = men_base_url_2018_scaled
    elif division == 'women-s':
        url = women_base_url_2018_scaled
    if url != '':
        page = requests.get(url + '1')
        try:
            page.json()
        except json.decoder.JSONDecodeError as err:
            return 0
        num_pages = page.json()['pagination']['totalPages']
    return num_pages

async def get_results():
    # start all the requests, so they all can eat network at the same time
    reqs = [Request(page) for page in pages]
    athletes = []
    for req in reqs:
        await req
        aths = parse_aths_2018(req)
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

def write_csv(athletes, division):
    results = []
    with open('2018{}.csv'.format(division), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['Name', 'Score1', 'Score2', 'Score3', 'Score4', 'Score5']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for ath in athletes:
            res = parse_results_2018(ath)
            results.append(res)
            # 2018 only one
            # writer.writerow({'Name': res['name'], 'Score1': res['scores'][0], 'Score2': res['scores'][1],
            #    'Score3': res['scores'][2], 'Score4': res['scores'][3], 'Score5': res['scores'][4]})
            writer.writerow({'Name': res['name'], 'Score1': res['scores'][0]})
    return results

def plot_scores(workout_num, results, division):
    data1 = np.array([ath['scores'][workout_num-1] for ath in results ]).astype(np.float)
    data1 = data1[~np.isnan(data1)]
    # reject extreme outliers 5*std_dev
    data1 = data1[np.abs(data1 - mu) < 4*sigma]
    mu = np.mean(data1)
    sigma = np.std(data1)
    median = np.median(data1)
    mode = np.mode(data1)
    print(mu)
    print(sigma)
    print(median)
    print(mode)
    print(len(data1))
    # get best fit for data
    lower = mu - 4*sigma
    upper = mu + 4*sigma
    x = np.linspace(lower, upper, 1000)
    pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
    hist, edges = np.histogram(data1, density=True, bins=100)
    p1 = figure(title='18.{} {}'.format(workout_num, division), background_fill_color='#E8DDCB')
    p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
        fill_color="#036564", line_color="#033649")
    p1.line(x, pdf, line_color="#D95B43", line_width=8, alpha=0.7)
    output_file('18.{}_{}.html'.format(workout_num, division))
    show(p1)

def cfopen(division, workout):
    num_pages_total = get_pages_2018(division)
    print(num_pages_total)
    remaining = num_pages_total
    last_page_used = 1
    athletes = []
    while remaining > 0:
        num_pages = 500
        if last_page_used + 500 > num_pages_total:
            num_pages = num_pages_total - last_page_used
        build_urls(last_page_used, num_pages, division)
        last_page_used = last_page_used + num_pages
        remaining = num_pages_total - last_page_used
        print(pages[0])
        print(pages[-1:])
        aths = get_results_base()
        athletes.extend(aths)
        print('total athletes {}'.format(len(athletes)))
        time.sleep(5)
    if len(athletes) > 0:
        results = write_csv(athletes, division)
        plot_scores(workout, results, division)

if __name__ == "__main__":
    print('start')
    # divisions
    #cfopen('men', 1)
    #cfopen('women', 1)
    cfopen('men-s', 1)
    #cfopen('women-s', 1)
    print('end')
