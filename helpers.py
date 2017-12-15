import requests
import json
import datetime
from lxml import etree
import re

def _removeTags(string):
    """ remove html tags from the input string """
    chars = []
    isRead = True
    for c in string:
        if(c == '<'):
            isRead = False
        elif c=='>':
            isRead = True
        elif isRead:
            chars.append(c)
    return ''.join(chars)

JIRA_ID_PATTERN = re.compile('([A-Z]+-\d+)')
def _findIssueId(string):
    """ find JIRA issue id in a string """
    result = JIRA_ID_PATTERN.search(string)
    if result is not None:
        return result.group(1)
    else:
        return 'Unknown Id'

def _textOrElse(tree, default):
    " get tree text, if tree is None, return default "
    if tree is not None:
        return tree.text
    else:
        return default

NEOXAM_STREAM_URL = 'https://support.neoxam.com/activity?streams=user+IS+{user}+&streams=update-date+BETWEEN+{startTime}+{endTime}'
def _getActivityStream(startMilli, endMilli, user, password):
    """ get activity stream through http request """
    url = NEOXAM_STREAM_URL.format(user=user, startTime=startMilli, endTime=endMilli)
    result = requests.get(url, auth=(user, password))
    return result.text

def getActivities(startTime, endTime, user, password):
    "request activity stream and parse it into a list of Activity objects"
    startMilli = int(startTime.timestamp() * 1000)
    endMilli = int(endTime.timestamp() * 1000)
    rawStream = _getActivityStream(startMilli, endMilli, user, password)
    tree = etree.fromstring(rawStream)
    entries = tree.findall('./entry', tree.nsmap)
    activities = list(map(lambda e: Activity(e), entries))
    return activities

NEOXAM_LOG_WORK_URL = 'https://support.neoxam.com/rest/api/2/issue/{issueId}/worklog'
def logWork(issueId, startTime, secondSpent, user, password):
    "send post request to server to log user's work, return the server response"
    timeString = startTime.strftime('%Y-%m-%d') + 'T15:00:00.000+0000'
    url = NEOXAM_LOG_WORK_URL.format(issueId=issueId)
    header = {'Content-Type':'application/json'}
    payload = json.dumps({'comment':'work', 'timeSpentSeconds':secondSpent, 'started':timeString})
    response = requests.post(url, data=payload, headers=header, auth=(user, password))
    return response

class Activity:
    "User's JIRA activity"
    def __init__(self, tree):
        "initial from a xml tree object"
        rawTitle = _removeTags(_textOrElse(tree.find('./title', tree.nsmap), "can't get title"))
        self.title = ' '.join(rawTitle.split())
        self.issueId = _findIssueId(self.title)
        self.author = _textOrElse(tree.find('./author/name', tree.nsmap), "can't get author")
        timestring = _textOrElse(tree.find('./published', tree.nsmap), "can't get timestamp")
        timefmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        self.date = datetime.datetime.strptime(timestring, timefmt)
