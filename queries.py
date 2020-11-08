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
	print("highest group weeks:", numToDateRange(grouped_weeks[highest][0]))

	days_percent = round(int(blackout_posts)/totaldaysCount() * 100, 2)

	data = {
		'total_all': all_posts,
		'total_blackouts': blackout_posts,
		'total_days': days,
		'total_with_photo': with_photo,
		'average_week_days': average_days_week,
		'average_duration': avg_duration,
		'percent_days': days_percent
	}

	cacheData('computed', data)

if __name__ == '__main__':
	main()