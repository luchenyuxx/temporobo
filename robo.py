import subprocess
from lxml import etree
from parse import findall

print('Welcome to temporobo!')

# Get the stream activities
result = subprocess.run(['curl', '-u', 'chenyu.lu:963574159lcy', 'https://support.neoxam.com/activity?streams=user+IS+chenyu.lu'], stdout=subprocess.PIPE)

result.stdout.decode('utf-8')

tree = etree.fromstring(result.stdout.decode('utf-8'))

entries = tree.findall('./entry', tree.nsmap)

class Activity:
    """User's JIRA activity"""
    def __init__(self, title, issueId, author, timestamp):
        self.title = title
        self.issueId = issueId
        self.author = author
        self.timestamp = timestamp

    def __init__(self, e):
        self.title = self.getTextOrElse(e.find('./title',e.nsmap), "can't get title")
        #self.title = ''.join(r.fixed[0] for r in findall(">{}<", rawTitle))
        self.issueId = self.getTextOrElse(e.find('./activity:object/title', e.nsmap), "can't get issue id")
        self.author = self.getTextOrElse(e.find('./author/name', e.nsmap), "can't get author")
        self.timestamp = self.getTextOrElse(e.find('./published', e.nsmap), "can't get timestamp")

    def getTextOrElse(self, e, default):
        if(e is not None):
            return e.text
        else:
            return default

activities = list(map(lambda e: Activity(e), entries))

for a in activities:
    print("==================================")
    print(a.title)
    print(''.join(r.fixed[0] for r in findall(">{}<", a.title)))
    print(a.issueId)
    print(a.author)
    print(a.timestamp)
