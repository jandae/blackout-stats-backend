# needed a quick way to store mysql processed data to redis because I just have this weekend to work
# on this 🤪

import mysql.connector
import json
import redis
import datetime
import time

mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="",
	database="blackout-stats"
)

redis_host = "localhost"
redis_port = 6379
redis_password = ""

try:
	r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
except Exception as e:
	print(e)

cursor = mydb.cursor(dictionary=True)

def query(query):
	cursor.execute(query)
	result = cursor.fetchall()
	return result

def cacheData(key, value):
	try:
		r.set(key, value)
	except Exception as e:
		print(e)

def getCached(key):
	msg = r.get(key)
	return msg

def totaldaysCount(start = datetime.datetime(2020,4,4)):
	delta = datetime.datetime.now() - start
	return delta.days

def numToDate(week_num, year = 2020):
	time.asctime(time.strptime('{} {} 1'.format(year, week_num), '%Y %W %w'))

def main():
	all_posts_query = "SELECT count(*) as count FROM posts"
	relevant_query = "SELECT count(*) as count FROM posts where category != 'uncategorized'"
	days_query = "SELECT count(distinct(date)) as count FROM posts where category != 'uncategorized'"
	with_photo_query = "SELECT count(date) as count FROM posts where category != 'uncategorized' and photos > 0"
	avg_duration_query = "SELECT avg(duration) as average FROM posts where category != 'uncategorized' and duration is not null"
	weeks_query = "SELECT count(distinct(date)) as count, week(date) as week FROM posts where category != 'uncategorized' and date is not null group by week"

	all_posts = query(all_posts_query)[0]["count"]
	blackout_posts = query(relevant_query)[0]['count']
	days = query(days_query)[0]['count']
	with_photo = query(with_photo_query)[0]['count']
	weeks = query(weeks_query)
	avg_duration = round(float(query(avg_duration_query)[0]['average'])/60, 2)

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
	print(grouped_weeks[highest][0])

	print("highest group weeks:", )

	cacheData('total:all', all_posts)
	cacheData('total:blackouts', blackout_posts)
	cacheData('total:days', days)
	cacheData('total:days', days)
	cacheData('total:with_photo', with_photo)
	cacheData('average:week_days', average_days_week)
	cacheData('average:duration', avg_duration)

	days_percent = round(int(getCached('total:days'))/totaldaysCount() * 100, 2)

	print("all:",getCached('total:all'))
	print("blackout posts:", getCached('total:blackouts'))
	print("days:", getCached('total:days'), "/", totaldaysCount())
	print("days percent:", days_percent)
	print("post photo:", getCached('total:with_photo'), "/", getCached('total:blackouts'))
	print("Average days per week:", getCached('average:week_days'))
	print("Average duration:", getCached('average:duration'))

if __name__ == '__main__':
	main()