import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

class HLTB_Completions_Spider(scrapy.Spider):
	name = 'hltb_completions_spider'

	def start_requests(self):
		start_page = 1
		end_page = 1996
		page_range = range(start_page, end_page+1)
		for page_id in page_range:
			page_url = 'https://howlongtobeat.com/search_results.php?page=%s' % page_id
			yield scrapy.Request(url=page_url, callback=self.parse_page)
	

	def parse_page(self, response):
		global current_page_number
		global current_game_number

		games = response.css('div.search_list_image > a')
		print('Processing page %s (games %s-%s)' % (current_page_number, current_game_number, current_game_number + len(games)))

		for game in games:
			# j'etrait l'ID (vérifiez la longueur du fractionnement au cas où un ID serait manquant).
			raw_id = game.xpath('./@href').extract_first().split('=')
			game_id = raw_id[1] if (len(raw_id) == 2) else 'INVALID'

			# verif de sécu.
			if('' == game_id):
				print('Error parsing game on page (%s)!' % response.url)
				continue

			# génération du lien du jeu.
			game_link = 'https://howlongtobeat.com/game.php?id=%s&s=completions' % game_id

			
			yield response.follow(url=game_link, callback=self.parse_completions)
		
		current_page_number += 1
	

	def parse_completions(self, response):
		global current_game_number

		# ID du jeu
		game_id = response.url.split('id=')[1].split('&s=')[0]
		print('Processing game %s (id=%s)' % (current_game_number, game_id))

		game_df = pd.DataFrame(columns=['id', 'type', 'platform', 'time'])

		
		game_tables = response.xpath('//table[@class="game_main_table"]')
		for table in game_tables:
			
			title = table.xpath('./../../../h3/text()').extract_first().strip()

			if title in ['Main Story', 'Main + Extras', 'Completionists', 'Speed Run - Any%', 'Speed Run - 100%', 'Co-Op Multiplayer']:
				entries = table.xpath('./tbody[@class="spreadsheet"]')
				for entry in entries:
					
					platform = entry.xpath('./tr/td[2]/text()').extract_first()
					platform = platform.strip() if platform != None else 'NA' # if it's valid, strip, otherwise, swap out for NA

					
					time = entry.xpath('./tr/td[3]/text()').extract_first()
					if None == time:
						print('Skipping completion without time.')
						continue 
					time = time.strip() 

					game_df = game_df.append({'id': game_id, 'type': title, 'platform': platform, 'time': time}, ignore_index=True)
				
			else:
				print('Skipping unknown table:', title)

		
		game_df.to_csv('./completions/%s.csv' % game_id, index=None)
		current_game_number += 1
	


current_page_number = 0
current_game_number = 0

process = CrawlerProcess()
process.crawl(HLTB_Completions_Spider)
process.start()

print('Processed', current_page_number, 'pages!')
print('Processed', current_game_number, 'games!')