import numpy as np

def parse_results_2018(row):
    '''
	num_pages = json_data['pagination']['totalPages']
	for row in json_data['leaderboardRows']:
		person = row['entrant']
		scores = row['scores']
		print(person['competitorName'])
		for wod in scores:
			print(wod['scaled'] + '  ' + wod['score'])
    '''
    res = {}
    res['name'] = row['entrant']['competitorName']
    res['persondetails'] = row['entrant']
    res['scores'] = []
    for score in row['scores']:
        if ':' in score['scoreDisplay']:
            # its a time value
            res['scores'].append(score['scoredetails']['time'])
        elif 'reps' in score['scoreDisplay']:
            # number of reps
            res['scores'].append(score['scoreDisplay'].split(' ')[0])
        else:
            # delete the user?
            res['scores'].append(np.nan)
    return res

def parse_results_2017(ath):
	# save the name and widdle down the scores
    res = {}
    res['name'] = ath['name']
    res['scores'] = []
    for score in ath['scores']:
        if ':' in score['scoredisplay']:
            # its a time value
            res['scores'].append(score['scoredetails']['time'])
        elif 'reps' in score['scoredisplay']:
            # number of reps
            res['scores'].append(score['scoredisplay'].split(' ')[0])
        else:
            # delete the user?
            res['scores'].append(np.nan)
    return res

def parse_aths_2017(req):
    return req.content['athletes']

def parse_aths_2018(req):
    if 'leaderboardRows' in req.content.keys():
        return req.content['leaderboardRows']
    else:
        return {}

def get_name_score_2017(ath):
    return ath['name'], ath['scores'][0]['scoredisplay']