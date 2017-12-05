import requests
import schedule
import re
import datetime
from lxml import etree
import collections
import time
import argparse
import json

print('Welcome to temporobo!')
print('A robot to log your work on neoxam JIRA 8 hours a day. Make both you and your neoxam family happy.')
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

def workon(aNiceDay):
    print('Going to log work for' + str(aNiceDay))
    dayfmt = "%Y-%m-%dT%H:%M:%S"
    startOfDay = aNiceDay + 'T00:00:00'
    endOfDay = aNiceDay + 'T23:59:59'
    startOfDay = datetime.datetime.strptime(startOfDay, dayfmt)
    endOfDay = datetime.datetime.strptime(endOfDay, dayfmt)
    startOfDay = int(startOfDay.timestamp() * 1000)
    endOfDay = int(endOfDay.timestamp() * 1000)

# Get the stream activities
    streamUrl = 'https://support.neoxam.com/activity?streams=user+IS+'+user+'&streams=update-date+BETWEEN+' + str(startOfDay) + '+' + str(endOfDay)
    result = requests.get(streamUrl, auth=(user, pwd))

    tree = etree.fromstring(result.text)

    entries = tree.findall('./entry', tree.nsmap)

    def extractTitle(rawTitle):
        isRead = True
        result = ''
        for c in rawTitle:
            if(c == '<'):
                isRead = False
            elif(c == '>'):
                isRead = True
            elif(isRead):
                result += c
        return result

    def getTextOrElse(e, default):
            if(e is not None):
                return e.text
            else:
                return default

    timefmt = '%Y-%m-%dT%H:%M:%S.%fZ'
    idPattern = re.compile('((NDF|NDR)-\d+)')
    def findIdInTitle(title):
        result = idPattern.search(title)
        if result is not None:
            return result.group(1)
        else:
            return None

    class Activity:
        """User's JIRA activity"""
        def __init__(self, e):
            rawTitle = extractTitle(getTextOrElse(e.find('./title',e.nsmap), "can't get title"))
            self.title = ' '.join(rawTitle.split())
            # self.issueId = getTextOrElse(e.find('./activity:object/title', e.nsmap), findIdInTitle(self.title))
            self.issueId = findIdInTitle(self.title)
            self.author = getTextOrElse(e.find('./author/name', e.nsmap), "can't get author")
            timestring = getTextOrElse(e.find('./published', e.nsmap), "can't get timestamp")
            self.date = datetime.datetime.strptime(timestring, timefmt)


    activities = list(map(lambda e: Activity(e), entries))

    for a in activities:
        print("==================================")
        print('title: ' + a.title)
        print('issue id: ' + (a.issueId or ""))
        print('author: ' + a.author)
        print('date: ' + str(a.date))

    issueIds = list(map(lambda a: a.issueId, activities))

    issueFrequency = collections.Counter(issueIds)

    sumFrequency = sum(issueFrequency.values())
    print('There are total '+str(sumFrequency)+' activities on ' +aNiceDay)

    totalSeconds = 8 * 3600

    for issue in issueFrequency.keys():
        time.sleep(1)
        frequency = issueFrequency[issue]
        print(str(frequency)+' activities on issue '+issue)
        secondSpent = int(totalSeconds * frequency / sumFrequency)
        header = {'Content-Type':'application/json'}
        payload = json.dumps({'comment':'work', 'timeSpentSeconds':secondSpent})
        url = 'https://support.neoxam.com/rest/api/2/issue/'+issue+'/worklog'
        r = requests.post(url, data=payload, headers=header, auth=(user, pwd))
        if r.status_code == 201:
            print('Successfully log '+str(secondSpent)+' seconds work to issue '+issue)
        else:
            print('Failed to log '+str(secondSpent)+' seconds work to issue '+issue)

def workNow():
    currentTime = datetime.datetime.now()
    currentDay = currentTime.strftime("%Y-%m-%d")
    print('Now is ' + str(currentTime) +", I'm going to work.")
    workon(currentDay)
    print('Job is done. See you tomorrow')

if today is not None:
    workon(today)
else:
    print('The robot will log your work on JIRA at 19:00 every day')
    schedule.every().day.at('19:00').do(workNow)
    while True:
        schedule.run_pending()
        time.sleep(1)

