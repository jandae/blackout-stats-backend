# needed a quick way to store mysql processed data to redis because I just have this weekend to work
# on this 🤪
import mysql.connector
import json
from cache import cacheData
from datetime import datetime, timedelta
from config import Config

try:
	mydb = mysql.connector.connect(
		host=Config.mysql_host,
		user=Config.mysql_user,
		password=Config.mysql_password,
		database=Config.mysql_database
	)

	cursor = mydb.cursor(dictionary=True)
except Exception as e:
	print(e)

def query(query):
	try:
		cursor.execute(query)
		result = cursor.fetchall()
	except Exception as e:
		print(e)
	return result

def totaldaysCount(start = datetime(2020,4,4)):
	delta = datetime.now() - start
	return delta.days

def numToDateRange(start_num, year = 2020):
	start_date = datetime.strptime('{} {} 1'.format(year, start_num), '%Y %W %w').date()
	end_date = start_date + timedelta(days=6)
	return start_date.strftime("%m/%d/%Y") + " - " + end_date.strftime("%m/%d/%Y")

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime)):
        return obj.strftime('%m-%d-%Y')
    raise TypeError ("Type %s not serializable" % type(obj))

def main():
	all_posts_query = "SELECT count(*) as count FROM posts"
	relevant_query = "SELECT count(*) as count FROM posts where category != 'uncategorized'"
	# days_query = "SELECT count(distinct(date)) as count FROM posts where category != 'uncategorized'"
	with_photo_query = "SELECT count(date) as count FROM posts where category != 'uncategorized' and photos > 0"
	avg_duration_query = "SELECT avg(duration) as average FROM posts where category != 'uncategorized' and duration is not null"
	weeks_query = "SELECT count(distinct(date)) as count, week(date) as week FROM posts where category != 'uncategorized' and date is not null group by week"
	last_post_query = "SELECT max(date) as latest FROM posts where category != 'uncategorized'"
	first_post_query = "SELECT min(date) as oldest FROM posts where category != 'uncategorized'"
	days_count_query = "SELECT date, count(date) as count FROM posts where category != 'uncategorized' and date is not null group by date"
	hours_down_query = "SELECT sum(duration) as total FROM posts where category != 'uncategorized' and duration is not null"
	birds_query = "SELECT count(cause) as count FROM posts where cause like '%bird%' or cause like '%crow%'"
	cause_query = "SELECT cause FROM posts where cause is not null"
	areas_query = "SELECT area, count(area) as count FROM areas where parent = 0 group by area"
	category_query = "SELECT category, count(category) as count FROM posts where category != 'uncategorized' group by category"

	all_posts = query(all_posts_query)[0]["count"]
	blackout_posts = query(relevant_query)[0]['count']
	# days = query(days_query)[0]['count']

	with_photo = query(with_photo_query)[0]['count']
	weeks = query(weeks_query)
	avg_duration = round(float(query(avg_duration_query)[0]['average'])/60, 2)
	last_post = query(last_post_query)[0]['latest'].strftime("%B %d, %Y")
	first_post = query(first_post_query)[0]['oldest'].strftime("%B %d, %Y")
	days_count = query(days_count_query)
	days_down = (int(query(hours_down_query)[0]['total'])/60)/24
	hours_down = (days_down % 1)*24
	minutes_down = (hours_down % 1)*60
	days = len(days_count)
	days_count_processed = json.dumps(days_count, default=json_serial) #convert date to string
	birds = query(birds_query)[0]['count']
	causes = query(cause_query)
	areas = query(areas_query)
	capitalize = lambda item: {'category': item["category"].title(), 'count': item["count"]}
	categories = list(map(capitalize, query(category_query)))

	print(areas)
	with open('./util/areas.json', 'w') as outfile:
		json.dump(areas, outfile)

	#process causes
	exclude = ["of", "to", "on", "and", "by", "that"]
	words_count = {}
	for cause in causes:
		cause_words = cause["cause"].lower().strip().split(" ")
		for word in cause_words:
			if not(word in exclude):
				if word in words_count:
					words_count[word]+=1
				else:
					words_count[word] = 1

	words_count_sorted = sorted(words_count.items(), key=lambda kv: kv[1])
	print(words_count_sorted)
	# for word, value in words_count.items():
	# 	print(word, ":", value)

	#compute average per week
	# formula:
	# b - days with blackout
	# w - weeks with blackout
	# t - total number of days with blackout
	# a = w / ((t/7) - w)
	print("weeks with:", len(weeks))
	print("days without:", totaldaysCount()-days)
	print("weeks without:", (totaldaysCount()-days)/7)
	average_days_week = round(len(weeks)/((totaldaysCount()-days)/7), 2)

	#find highest
	highest = 0
	grouped_weeks = {}
	for week in weeks:
		if not (week["count"] in grouped_weeks):
			grouped_weeks[week["count"]] = []

		grouped_weeks[week["count"]].append(week["week"])

		if week["count"] > highest:
			highest = week["count"]

	print("highest:", highest)
	print("highest group weeks:", numToDateRange(grouped_weeks[highest][0]))

	days_percent = round(days/totaldaysCount() * 100, 2)
	print(days)

	updated_at = datetime.now().strftime("%B %d, %Y %H:%M:%S")


	data = {
		'total_all': all_posts,
		'total_blackouts': blackout_posts,
		'total_days': days,
		'total_with_photo': with_photo,
		'average_week_days': average_days_week,
		'average_duration': avg_duration,
		'percent_days': days_percent,
		'last_post': last_post,
		'first_post': first_post,
		'updated_at': updated_at,
		'days_count': days_count_processed,
		'total_days_since': totaldaysCount(),
		'total_days_down': str(int(days_down)),
		'total_hours_down': str(int(hours_down)),
		'total_minutes_down': str(int(minutes_down)),
		'birds': birds,
		'categories': json.dumps(categories)
	}

	print(str(days_down))
	print(str(days_down%1))

	cacheData('computed', data)

if __name__ == '__main__':
	main()