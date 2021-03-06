import os
import scrapy
import pandas as pd

pd.set_option('display.max_colwidth', -1)

def abspath(file):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), file))

## 11eyes CrossOver (Developer, Editeur, Genre, JP)
with open(abspath('./offline-tests/eyes.html')) as file:
	with open(abspath('./tests/eyes.html')) as file:
		eyes_sel = scrapy.Selector(text=file.read())

# Peggle (Developers, Editeur, Jouable sur, Genre, NA, EU)
with open(abspath('./offline-tests/peggle.html')) as file:
	with open(abspath('./tests/peggle.html')) as file:
		peggle_sel = scrapy.Selector(text=file.read())

# Witcher 3 (Developer, Editeur, Jouable sur, Genres, NA, EU, JP)
with open(abspath('./offline-tests/witcher3.html')) as file:
	with open(abspath('./tests/witcher3.html')) as file:
		witcher_sel = scrapy.Selector(text=file.read())

# Blood & Wine (Type, Developer, Editeur, Jouable sur, Genres, NA)
with open(abspath('./offline-tests/bloodwine.html')) as file:
	with open(abspath('./tests/bloodwine.html')) as file:
		blood_sel = scrapy.Selector(text=file.read())

# IDARB (Co-Op, Vs.)
with open(abspath('./offline-tests/idarb.html')) as file:
	with open(abspath('./tests/idarb.html')) as file:
		idarb_sel = scrapy.Selector(text=file.read())

def parse_game(sel):
	game_df = pd.DataFrame()

	game_df['id'] = [0] # factice pour l'instant

	# Titre
	game_df['title'] = [sel.css('div.profile_header::text').extract_first().strip()] 

	# Temps de jeu
	all_times = sel.css('div.game_times > li')
	time_names = all_times.xpath('./h5/text()').extract()
	time_times = all_times.xpath('./div/text()').extract()
	
	time_times = [s.strip().replace('--', 'NA').replace('½', '.5') for s in time_times]
	time_times = [s.strip().replace('--', '').replace('½', '.5') for s in time_times]
	
	time_times = [str(float(s.split(' ')[0]) / 60.0) if 'Mins' in s else s.split(' ')[0] for s in time_times]
	names_times = dict(zip(time_names, time_times))
	for key in ['Main Story', 'Main + Extras', 'Completionist', 'All Styles', 'Co-Op', 'Vs.']:
		game_df[key] = names_times[key] if key in names_times else 'NA'
		game_df[key] = names_times[key] if key in names_times else ''

	profile = {
		'Type': 'NA',
		'Developers': 'NA',
		'Publishers': 'NA', 
		'Playable On': 'NA',
		'Genres': 'NA', 
		'NA': 'NA',
		'EU': 'NA',
		'JP': 'NA',
		'Type': '',
		'Developers': '', 
		'Publishers': '', 
		'Playable On': '',
		'Genres': '', 
		'NA': '',
		'EU': '',
		'JP': ''
	}
	profile_info = sel.css('div.profile_info')
	for info in profile_info:
		info_title = info.xpath('./strong/text()').extract_first().replace(':', '').strip()
		info_text = info.xpath('./text()').extract()[1].strip() 

		
		if ('Developer' == info_title) or ('Developers' == info_title):
			profile['Developers'] = info_text
		elif ('Publisher' == info_title) or ('Publishers' == info_title):
			profile['Publishers'] = info_text
		elif ('Genre' == info_title) or ('Genres' == info_title):
			profile['Genres'] = info_text
		elif info_title not in ['Updated']: 
			profile[info_title] = info_text

	for key, value in profile.items():
		game_df[key] = value

	global all_games_df
	all_games_df = pd.concat([all_games_df, game_df])

all_games_df = pd.DataFrame()

parse_game(eyes_sel)
parse_game(peggle_sel)
parse_game(witcher_sel)
parse_game(blood_sel)
parse_game(idarb_sel)


all_games_df.sort_values('title', inplace=True)
all_games_df.index = pd.RangeIndex(start=0, stop=len(all_games_df))

# csv
all_games_df.to_csv('all-games-test.csv', index=None)

print(all_games_df)
print(all_games_df.info())