import json
import urllib.request
import csv
from datetime import datetime
from dateutil import parser
import re
import io

def urlToJson(url):
    items = {}

    with urllib.request.urlopen(url) as response:
        items = json.loads(response.read())

    posts = items[0]["posts"]

    with open('posts.json', 'w') as outfile:
        json.dump(posts, outfile)

    return formatPosts(posts)

def formatPosts(posts):
    formatted_posts = []

    for post in posts:
        formatted = {}
        post_id = extractID(post['postUrl'])
        date_time = datetime.strptime(post['postDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
        category = parseCategory(post)
        post_images = len(post["postImages"])

        formatted["table_id"] = "NULL"
        formatted["id"] = post_id if post_id else "NULL"
        formatted["datetime"] = date_time if date_time else "NULL"
        formatted["category"] = category if category else "NULL"
        formatted["text"] = post["postText"] if post["postText"] else "NULL"

        formatted["date"] = "NULL"
        formatted["start_time"] = "NULL"
        formatted["end_time"] = "NULL"
        formatted["duration"] = "NULL"
        formatted["cause"] = "NULL"

        if formatted["category"] != "uncategorized":
            post_meta = parsePostMeta(post["postText"])
            formatted["date"] = post_meta["date"] if post_meta["date"] else "NULL"
            formatted["start_time"] = post_meta["start_datetime"] if post_meta["start_datetime"] else "NULL"
            formatted["end_time"] = post_meta["end_datetime"] if post_meta["end_datetime"] else "NULL"
            formatted["duration"] = post_meta["duration"] if post_meta["duration"] else "NULL"
            formatted["cause"] = post_meta["cause"] if post_meta["cause"] else "NULL"

        formatted["photos"] = post_images if post_images else "NULL"
        comments = post['postComments']['comments']
        formatted["ali_comment"] = findAliComment(comments)

        formatted_posts.append(formatted)

    return formatted_posts

def findAliComment(comments):
    ali_comment = "NULL"

    for comment in comments:
        if comment["name"] == 'Ronald Ali Mangaliag':
            ali_comment = comment["text"]
            break

    return ali_comment

def parseCategory(post):
    category_keywords = {
        "unscheduled":"\nUnscheduled ",
        "scheduled":"\nScheduled",
        "emergency":"\nEmergency",
    }
    text = post["postText"]
    post_category = 'uncategorized'
    for category, keyword in category_keywords.items():
        if keyword in text:
            post_category = category
            break

    return post_category


def findMatch(text, pattern, groups=[1]):
    match = re.search(pattern, text, flags = re.IGNORECASE|re.MULTILINE)
    if match:
        formatted = ""
        for group in groups:
            formatted += match.group(group).strip() + " "
        return formatted.strip()
    return False

def parseCause(text):
    keywords = ["cause", "purpose"]
    cause = "NULL"

    for key in keywords:
        title_pattern = re.search(
            "^"+key+"\s*:\s*(.*)$",
            text,
            flags = re.IGNORECASE|re.MULTILINE
        )

        if title_pattern:
            cause = title_pattern.group(1).strip()
            print(cause)
            break

    return cause


def parsePostMeta(text):

    cause = parseCause(text)
    date = ""
    start_datetime = ""
    end_datetime = ""

    date_keywords = ["DATE"]
    datetime_keywords = ["DATE AND TIME STARTED", "DATE/TIME"]
    start_keywords = ["TIME STARTED"]
    end_keywords = ["restor", "ended", "status"]

    # process date and time on separate lines
    # Sample:
    # Date: October 31, 2020
    # Start time: 4:00 PM
    # End time: 6:00 PM
    for key in date_keywords:
        date_key = "^" + key + ".*:(.*\d\d)$" #pattern: \n[key]:[group2]\n
        date_pattern = findMatch(text, date_key)

        if date_pattern:
            print(key)
            start = ""
            end = ""
            end_date = ""
            date = date_pattern
            print("date:", date)

            for start_key in start_keywords:
                start_pattern = re.search(
                    "^.*" + start_key + ".*\:\s*(\d*\:\d\d)\s*(\w\w)\s*restored at\s*(\d*\:\d\d)\s*(\w\w)",
                    text,
                    flags = re.IGNORECASE|re.MULTILINE
                )

                if start_pattern:
                    start = cleanTime(start_pattern.group(1).strip() + " " + start_pattern.group(2).strip())
                    print("start:", start)
                    end = cleanTime(start_pattern.group(3).strip() + " " + start_pattern.group(4).strip())
                    print("end:", end)
                else:
                    start_pattern = re.search(
                        "^.*" + start_key + ".*\:\s*(\d*\:\d\d)\s*(.*)$",
                        text,
                        flags = re.IGNORECASE|re.MULTILINE
                    )

                    if start_pattern:
                        start = cleanTime(start_pattern.group(1).strip() + " " + start_pattern.group(2).strip())
                        print("start:", start)
                        break

            for end_key in end_keywords:
                # DATE and TIME RESTORED: April 7,2020 , 3:06 PM
                end_pattern = re.search(
                    "^.*" + end_key + ".*:\s*(.*\s*\d*\,*\d\d\d\d)\s*\,*\s(\d*:\d\d)\s*(.*)$",
                    text,
                    flags = re.IGNORECASE|re.MULTILINE
                )

                # End time: 6:00 PM (October 23, 2020)
                end_pattern1 = re.search(
                    "^.*" + end_key + ".*\:\s*(\d*\:\d\d)\s*(\w\w)\s*\((.*)\)$",
                    text,
                    flags = re.IGNORECASE|re.MULTILINE
                )

                if end_pattern:
                    end = cleanTime(end_pattern.group(2).strip() + " " + end_pattern.group(3).strip())
                    print("end:", end)

                    end_date = end_pattern.group(1)
                    print("end date:", end_date)

                    break


                elif end_pattern1:
                    end = cleanTime(end_pattern1.group(1).strip() + " " + end_pattern1.group(2).strip())
                    print("end:", end)

                    end_date = end_pattern1.group(3)
                    print("end date:", end_date)

                    break

                # End time: 6:00 PM
                else:
                    end_pattern = re.search(
                        "^.*" + end_key + ".*:\s*(\d*:\s*\d\d)\s*(.*)$",
                        text,
                        flags = re.IGNORECASE|re.MULTILINE
                    )

                    if end_pattern:
                        end = cleanTime(end_pattern.group(1).strip() + " " + end_pattern.group(2).strip())
                        print("end:", end)


                    break

            if start:
                start_datetime = date + " " + start
                print("start datetime:", start_datetime)
                start_datetime = parser.parse(start_datetime, ignoretz=True) #str to date
            if end:

                if end_date:
                    end_datetime =  parser.parse(end_date + " " + end, ignoretz=True)
                else:
                    end_datetime = date + " " + end
                    print("end datetime:", end_datetime)
                    end_datetime =  parser.parse(end_datetime, ignoretz=True)
            if date:
                date =  parser.parse(date, ignoretz=True)
                date = date.date()

            return {
                "date": date,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "duration": timeDiff(start_datetime, end_datetime),
                "cause": cause
            }

    print("XXXXXXXX")

    # process single line date and time
    # Sample:
    # Date/Time: October 31, 2020 from 3:00 PM to 4:00 PM
    # or
    # Date time started: 0ctober 31, 2020 10:00AM
    start = ""
    end = ""
    date = ""

    for datetime_key in datetime_keywords:
        print(datetime_key)
        # 3235318709854444
        # do this first
        datetime = re.search(
            "^" + datetime_key + ".*\:\s*(.*\,*\s*)\,*\s*from\s*(\d*:\d\d)\s*(\w\w)\s*to\s*(\d*:\d\d)\s*(\w\w)",
            text,
            flags=re.IGNORECASE|re.MULTILINE
        )

        if datetime:
            print("======")
            print(datetime.string)
            print("datetime:", datetime.group())

            date = datetime.group(1).strip()
            print("date:", date)

            start = datetime.group(2).strip() + " " + datetitme.group(3).strip()
            print("start:", start)

            end = datetime.group(4).strip() + " " + datetitme.group(5).strip()
            print("end:", end)

            break
        else:
            # Date time started: 0ctober 31, 2020 10:00AM
            datetime = re.search("^" + datetime_key + ".*:(.*,.*\d\d)\s(\d*\d:\d\d.*)$", text, flags=re.IGNORECASE|re.MULTILINE)

            if datetime:
                print("datetime:", datetime.group())

                date = datetime.group(1)
                print("date:", date)

                start = datetime.group(2)
                print("start:", start)

            break


    if start:
        start_datetime = date + " " + start
        print("start datetime:", start_datetime)
        start_datetime = parser.parse(start_datetime, ignoretz=True) #str to date

    if end:
        end_datetime = date + " " + end
        print("end datetime:", end_datetime)
        end_datetime =  parser.parse(date + " " + end, ignoretz=True)

    if date:
        date =  parser.parse(date, ignoretz=True)
        date = date.date()

    return {
        "date": date,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "duration": timeDiff(start_datetime, end_datetime),
        "cause": cause
    }

def parsePostMeta1(text):
    date = ""
    start_time = ""
    end_time = ""

    #oh the inconsistensies
    keywords = [
        {
            "key": 1,
            "text": "\nDATE:",
            "start_keyword": "\nTIME STARTED:",
            "end_keyword": "\nTIME RESTORED:",
            "alt_keyword": "\nDATE and TIME RESTORED:"
        },
        {
            "key": 2,
            "text": "\nDATE :",
            "start_keyword": "\nTIME STARTED:",
            "end_keyword": "\nTIME RESTORED:",
            "alt_keyword": "\nDATE and TIME RESTORED:"
        },
        {
            "key": 3,
            "text": "\nDATE AND TIME STARTED:",
            "start_keyword": ""
        },
        {
            "key": 4,
            "text": "\nDATE/TIME:",
            "start_keyword": ""
        }
    ]

    for keyword in keywords:
        if keyword["text"] in text:
            if keyword["key"] in [1,2]:
                date = text.split(keyword["text"])[1]
                date = date.split("\n")[0].strip().upper()
                start_time = text.split(keyword["start_keyword"])[1]
                start_time = start_time.split("\n")[0].strip().upper()
                end_time_arr = text.split(keyword["end_keyword"])
                if len(end_time_arr) > 1:
                    end_time = end_time_arr[1]
                    end_time = end_time.split("\n")[0].strip().upper()
            elif keyword["key"] == 3:
                date = text.split(keyword["text"])[1]
                date = date.split("\n")[0].strip().upper()
                date_arr = date.split(" ")
                am_pm = date_arr.pop(len(date_arr)-1)
                time = date_arr.pop(len(date_arr)-1)
                date = " ".join(date_arr)
                start_time = time + ' ' + am_pm
                end_time = ""
            elif keyword["key"] == 4:
                date = text.split(keyword["text"])[1]
                date = date.split("\n")[0].upper()

                if " FROM " in date:
                    date_arr = date.split(" FROM ")
                    date = date_arr[0].strip()

                    start_time = date_arr[1].split(" TO ")[0]
                    end_time = date_arr[1].split(" TO ")[1].split("\n")[0]


        if type(date) is str and date:
            date = parser.parse(date) #str to date
            date = date.date() #remove time

    start_time = cleanTime(start_time)
    end_time = cleanTime(end_time)

    return {
        "date": date,
        "start_time": start_time["human"],
        "end_time": end_time["human"],
		"duration": timeDiff(start_time["time"], end_time["time"])
    }

def cleanTime(time):
    time = time.replace(" ", "").upper() #remove spaces just because


    time_arr = time.split(":")
    # 24 hour format just to be inconsistent
    if time_arr[0] and int(time_arr[0]) > 12 or time_arr[0] == "00":
        time = time.replace("PM", "") #who does that?
        time = time.replace("AM", "")
        time = datetime.strptime(time, "%H:%M")
        return time.strftime("%I:%M %p")
    else:
        ampm = ""
        if "NN" in time:
            time = time.replace("NN", "PM")
            ampm = "PM"
        elif "AM" in time:
            ampm = "AM"
        elif "PM" in time:
            ampm = "PM"
        else:
            return False

        time = time.split(ampm)[0].strip()
        return time + ' ' + ampm

def timeDiff(start, end):

    if start and end:
        time_delta = "NULL"
        # todo make it convert the higher date to next day
        if start > end: # temporary auto detect, sometimes date is not found and inputted wrong
            time_delta = start - end
        else:
            time_delta = end - start
        return time_delta.total_seconds() / 60
    return ""

def fileToJson():
    with open('posts.json') as f:
        posts = json.load(f)
    return formatPosts(posts)

def extractID(url):
    story_string = "https://www.facebook.com/permalink.php?story_fbid="
    video_string = "https://www.facebook.com/benguetelectric/videos/"
    id_string = "&id=793198510733155"
    id = 0

    if story_string in url:
        url = url.replace(story_string, "")
        id = url.replace(id_string, "")
    else:
        url = url.replace(video_string, "")
        url = url.split("/")
        id = url[1]

    return id

def csv_formatter(string):
    string = string.replace('"', "")
    outstream = io.StringIO()   # "fake" output file

    cw = csv.writer(outstream)  # pass the fake file to csv module
    cw.writerow([string])       # write a row

    return outstream.getvalue() # get the contents of the fake file

def writeCSV(posts):
    data_file = open('posts.csv', 'w')
    # create the csv writer object
    csv_writer = csv.writer(data_file)

    # Counter variable used for writing
    # headers to the CSV file
    count = 0

    for post in posts:
        if count == 0:
            # Writing headers of CSV file
            header = post.keys()
            csv_writer.writerow(header)
            count += 1

        post_data = list(post.values())
        post_data[4] = csv_formatter(post_data[4]) # process text to make it csv safe

        # Writing data of CSV file
        csv_writer.writerow(post_data)

    data_file.close()
    return 'done'

# posts = urlToJson('https://api.apify.com/v2/datasets/Nvp0VWzJqop2oZc5N/items?format=json&clean=1')
posts = fileToJson()
writeCSV(posts)
# 3381355871917393