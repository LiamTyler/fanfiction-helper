from story import *
from story_database import *
from filters import *
from scraper import *
from test import *

def DownloadAndSaveStories( fandomName, dbName, baseUrl ):
    fandom = "fandoms/" + fandomName + "/"
    dbName = fandom + "databases/" + dbName
    characterDB = LoadCharacterDictionary( fandom + "genders.txt" )
    storyDB = DownloadStories( baseUrl, characterDB )
    storyDB.Serialize( dbName )

    return storyDB

#DownloadAndSaveStories( "Harry-Potter", "Harry-and-Draco-s-Love-Shack.bin", "https://www.fanfiction.net/community/Harry-and-Draco-s-Love-Shack/11605/99/0/1/0/0/0/0/" ) # gay 664
#DownloadAndSaveStories( "Harry-Potter", "Order-of-Stories.bin", "https://www.fanfiction.net/community/Order-of-Stories/10077/99/0/1/0/0/0/0/" ) # straight3 ~2100

#db = RunTestcaseFile( "Harry-Potter", "slash1.txt" )
db = RunTestcaseFile( "Harry-Potter", "straight1.txt" )

"""
N = len(db.stories)
counts = [0]*5
for i in range(N):
    story = db.stories[i]
    if story.isSlash:
        continue
    desc = story.description.lower()
    if "hpdm" in desc:
        counts[0] += 1
        print( i//25 + 1, story.title, desc )
    if "dmhp" in desc:
        counts[1] += 1
    if "hp-dm" in desc:
        counts[2] += 1

print( counts )
"""


story = db.SearchTitle("It Can't Be Love")[0]

desc = story.description.lower()
pos = desc.find( "slash" )
if pos == -1:
    print("no match")

delim = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
begin = pos
while begin >= 0 and not desc[begin] in delim:
    begin -= 1
begin += 1

l = len(desc)
end = pos
while end < l and not desc[end] in delim:
    end += 1
    
word = desc[begin:end]
if NearbySafeWord( desc, pos ) or word in [ "noslash", "nonslash", "slashed", "slashes", "slashing", "femslash" ]:
    print( "safe" )

print("end")