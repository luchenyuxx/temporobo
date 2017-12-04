import subprocess
import re
import datetime
from lxml import etree

print('Welcome to temporobo!')

# Get the stream activities
result = subprocess.run(['curl', '-u', 'chenyu.lu:963574159lcy', 'https://support.neoxam.com/activity?streams=user+IS+chenyu.lu'], stdout=subprocess.PIPE)

result.stdout.decode('utf-8')

tree = etree.fromstring(result.stdout.decode('utf-8'))

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
pattern = re.compile('((NDF|NDR)-\d+)')
def findIdInTitle(title):
    result = pattern.search(title)
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
