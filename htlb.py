import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

class HLTB_Spider(scrapy.Spider):
	name = 'hltb_spider'

	def start_requests(self):
		min_page = 1
		max_page = 1996
		page_range = range(min_page, max_page+1)
		for page_id in page_range:
			page_url = 'https://howlongtobeat.com/search_results.php?page=%s' % page_id
			# print("Parsing search page:", page_id)
			yield scrapy.Request(url=page_url, callback=self.parse_page)
	

	def parse_page(self, response):
		games = response.css('div.search_list_image > a')
		for game in games:
			# ID de l'extrait (vérifiez la longueur du fractionnement au cas où un ID est manquant).
			raw_id = game.xpath('./@href').extract_first().split('=')
			game_id = raw_id[1] if (len(raw_id) == 2) else 'INVALID'

			# Vérif de la sécurité.
			if('' == game_id):
				print('Error parsing game on page (%s)!' % response.url)
				continue

			# Création lien du jeu 
			game_link = 'https://howlongtobeat.com/game.php?id=%s' % game_id
			# print('\tParsing game w/ id:', game_id)

			# Page e de jeu
			yield response.follow(url=game_link, callback=self.parse_game)
		
	

	def parse_game(self, response):
		game_df = pd.DataFrame()

		# ID du jeu.
		game_df['id'] = [response.url.split('=')[1]]

		# Titre.
		game_df['title'] = [response.css('div.profile_header::text').extract_first().strip()] # preceded by \n and followed by space, so strip

		# Temps de jeu
		all_times = response.css('div.game_times > li')
		time_names = all_times.xpath('./h5/text()').extract()
		time_times = all_times.xpath('./div/text()').extract()
		# Suppression de tous les espaces, remplacez '--' par 'NA', remplacez '1/2' par '.5'.
		time_times = [s.strip().replace('--', 'NA').replace('½', '.5') for s in time_times]
		# Il existe deux formats de temps : Mins' et 'Hours'.
		# Si 'Mins', convertion en fraction d'heures, mais reconvertion en chaîne de caractères pour la cohérence.
		# Si 'Hours', il suffit de l'enlever.
		time_times = [str(float(s.split(' ')[0]) / 60.0) if 'Mins' in s else s.split(' ')[0] for s in time_times]
		# Je loop à travers comme un dict ici car toutes les pages de jeu n'ont pas toutes les entrées, et je ne veux pas de valeurs manquantes.
		names_times = dict(zip(time_names, time_times))
		for key in ['Main Story', 'Main + Extras', 'Completionist', 'All Styles', 'Co-Op', 'Vs.']:
			game_df[key] = names_times[key] if key in names_times else 'NA'

		# Profil (information de jeu).
		profile = {
			'Type': 'NA',
			'Developers': 'NA', # inclu 'Developer' et 'Developers'
			'Publishers': 'NA', # inclu 'Publisher' et 'Publishers'
			'Playable On': 'NA',
			'Genres': 'NA', # inclu 'Genre' et 'Genres'
			'NA': 'NA',
			'EU': 'NA',
			'JP': 'NA'
		}
		profile_info = response.css('div.profile_info')
		for info in profile_info:
			info_title = info.xpath('./strong/text()').extract_first().replace(':', '').strip()
			info_text = info.xpath('./text()').extract()[1].strip() 

			# Traiter les cas particuliers, et sinon, insérer simplement en utilisant le titre comme clé.
			if ('Developer' == info_title) or ('Developers' == info_title):
				profile['Developers'] = info_text
			elif ('Publisher' == info_title) or ('Publishers' == info_title):
				profile['Publishers'] = info_text
			elif ('Genre' == info_title) or ('Genres' == info_title):
				profile['Genres'] = info_text
			elif info_title not in ['Updated']: # ignorer la liste
				profile[info_title] = info_text

		for key, value in profile.items():
			game_df[key] = value

		
		global all_games_df
		all_games_df = pd.concat([all_games_df, game_df], sort=False)
	


all_games_df = pd.DataFrame()

process = CrawlerProcess()
process.crawl(HLTB_Spider)
process.start()

# trier par titre et réinitialiser l'index
all_games_df.sort_values('title', inplace=True)
all_games_df.index = pd.RangeIndex(start=0, stop=len(all_games_df))

# CSV
all_games_df.to_csv('all-games.csv', index=None)
# print(all_games_df)