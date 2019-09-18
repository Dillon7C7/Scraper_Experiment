#!/usr/bin/env python3

import sel_first
import local_db

scraper = sel_first.NakedNewsScraper()
#scraper.get_segment_info('Busts For Laughs')
scraper.scrape_all()
##approved_segments = ('Auditions', 'Behind The Lens', 'Behind the Scenes', 'Boob of the Week',
##   	'Closing Remarks', 'Cooking in the Raw', 'Dating Uncovered',
##   	'Entertainment', 'Flex Appeal', 'Game Spot', 'HollywoodXposed',
##   	'Inside The Box', 'Naked At The Movies', 'Naked Foodie', 'Naked Goes Pop',
##   	'Naked Goes Pot', 'Naked In The Streets', 'Naked News Moves', 'Naked Yogi',
##   	'News off the Top', 'News off the Top Part 2', 'Nude and Improved', 'Odds N Ends',
##   	'Odds N Ends Part 2', 'One on One', 'Pillow Talk', 'Point Of View', 'Pop My Cherry',
##   	'Riding In A Car Naked', 'Sports', 'Talk is Cheap', 'The Schmooze', 'Travels',
##   	'Trending Now', 'Turn it Up', 'Versus', 'Video Blog', "Viewer's Mail", 'Weather', 'Wheels')
##
##ddd = ['A Closer Look', 'All The Rage', 'App-date', 'Auditions', 'Behind The Lens', 'Behind the Scenes', 'Best of', 'Best of Naked News', 'Bloopers', 'Boob Of The Year', 'Boob of the Week', 'Boob-tube', 'Business', 'Christmas Special', 'Closing Remarks', 'Commentary', 'Cooking in the Raw', 'Costume Contest', 'Dating Uncovered', 'Drinking In The Raw', 'Dumb Criminals', 'Entertainment', 'Fashion', 'Flex Appeal', 'Fringe', 'Game Spot', 'Health', 'Health Watch', 'HollywoodXposed', 'Hot Properties', 'Inside The Box', 'International News', 'Know your Wood', 'Legal Briefs', 'Life & Leisure', 'Lily in the UK', 'Locker Talk', 'Media Matters', 'Naked At The Movies', 'Naked Foodie', 'Naked Goes Pop', 'Naked Goes Pot', 'Naked In The Streets', 'Naked League Comic', 'Naked Nerd', 'Naked News Moves', 'Naked Tech', 'Naked Yogi', 'Nerd Bites', 'New Release Rack', 'News off the Top', 'News off the Top Part 2', 'News off the Top Part 3', 'North American News', 'Nude and Improved', 'NudeViews', 'Odds N Ends', 'Odds N Ends Part 2', 'Olympic Report', 'On the Web', 'One From The Vault', 'One on One', 'Pan Am', 'Person of The Year', 'Pillow Talk', 'Point Of View', 'Pop My Cherry', 'Power Play', 'Pranks', 'Riding In A Car Naked', 'Sports', 'Status Update', 'Talk is Cheap', 'The Schmooze', 'Timeline', 'Travels', 'Trending Now', 'Turn it Up', 'Vampire Bites', 'Versus', 'Video Blog', "Viewer's Mail", 'Weather', 'Wheels', 'Year In Review']
##
##db = local_db.Local_Database('local_db.WITHOUT')
##db2 = local_db.Local_Database('local_db.back')
##big_dict = {}
##big_dict2 = {}
##for segg in approved_segments:
##	db.cursor.execute('''SELECT COUNT(*) FROM show_data WHERE segment_type = ? ''', (segg,))	
##	count = db.cursor.fetchone()
##	db2.cursor.execute('''SELECT COUNT(*) FROM show_data WHERE segment_type = ? ''', (segg,))	
##	count2 = db2.cursor.fetchone()
##
##	print('local_db.WITHOUT    local_db.back')
##	print('segment: {0} countW/O: {1}, countBAC: {2}'.format(segg, count, count2))
##
##	big_dict[segg] = {'count':count}
##	big_dict2[segg] = {'count':count}
##
##for x, y in big_dict.items():
##	print(x, y)
##for x, y in big_dict2.items():
##	print(x, y)
##for segg in ddd:
##	if segg not in approved_segments: 
##		print('Deleting segment {0} rows'.format(segg))
##		db.cursor.execute('''DELETE FROM show_data WHERE segment_type = ? ''', (segg,))
##		print('Segment {0} deleted'.format(segg))
##		db.db.commit()
##	else:
##		print('NOT Deleting segment {0}'.format(segg))
