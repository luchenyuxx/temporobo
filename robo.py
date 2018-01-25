import requests
import schedule
import datetime
import collections
import time
import argparse
import json
from helpers import (Activity, getActivities, logWork)

def workon(aNiceDay, user, pwd):
    print('Going to log work for ' + str(aNiceDay))
    dayfmt = "%Y-%m-%dT%H:%M:%S"
    startOfDay = aNiceDay + 'T00:00:00'
    endOfDay = aNiceDay + 'T23:59:59'
    startOfDay = datetime.datetime.strptime(startOfDay, dayfmt)
    endOfDay = datetime.datetime.strptime(endOfDay, dayfmt)

    activities = getActivities(startOfDay, endOfDay, user, pwd)

    if len(activities) == 0:
        print('You have no activities on ' + aNiceDay + ', neoxam family is not happy!')
        return

    for a in activities:
        print("==================================")
        print('title: ' + a.title)
        print('issue id: ' + (a.issueId or ""))
        print('author: ' + a.author)
        print('date: ' + str(a.date))

    issueIds = list(a.issueId for a in activities if a is not None and a.issueId
                    is not None)

    issueFrequency = collections.Counter(issueIds)

    sumFrequency = sum(issueFrequency.values())
    print('There are total '+str(sumFrequency)+' activities on ' +aNiceDay)

    totalSeconds = 8 * 3600

    for issue in issueFrequency.keys():
        time.sleep(1)
        frequency = issueFrequency[issue]
        print(str(frequency)+' activities on issue '+issue)
        secondSpent = int(totalSeconds * frequency / sumFrequency)
        r = logWork(issue, startOfDay, secondSpent, user, pwd)
        if r.status_code == 201:
            print('Successfully log '+str(secondSpent)+' seconds work to issue '+issue)
        else:
            print('Failed to log '+str(secondSpent)+' seconds work to issue '+issue)

def workNow(usr, pwd):
    def r():
        currentTime = datetime.datetime.now()
        currentDay = currentTime.strftime("%Y-%m-%d")
        print('Now is ' + str(currentTime) +", I'm going to work.")
        workon(currentDay, usr, pwd)
        print('Job is done. See you tomorrow')
    return r

if __name__ == '__main__':
    print('Welcome to temporobo!')
    print('A robot to log your work on neoxam JIRA 8 hours a day. Make both you and your neoxam family happy. :)')
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', required=True, help='Your JIRA login')
    parser.add_argument('-p', '--password', required=True, help='Your JIRA password')
    parser.add_argument('-d', '--date', help='The date to log work, format is "YYYY-mm-dd". if empty, the robot work at 19:00 every day.')
    args = parser.parse_args()

    user = args.user
    pwd = args.password
    today = args.date

    if today is not None:
        workon(today, user, pwd)
    else:
        print('The robot will log your work on JIRA at 19:00 every day.')
        schedule.every().day.at('19:00').do(workNow(user, pwd))
        while True:
            schedule.run_pending()
            time.sleep(1)
