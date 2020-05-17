from story import *
from story_database import *
from filters import *
from scraper import *
from test import *

def DownloadAndSaveStories( fandomName, dbName, baseUrl ):
    fandom = "fandoms/" + fandomName + "/"
    dbName = fandom + "databases/" + dbName
    info = LoadFandomInfo( fandom + "info.txt" )
    characterDB = info["characterGenders"]
    storyDB = DownloadStories( baseUrl, characterDB )
    storyDB.Serialize( dbName )

    return storyDB

#DownloadAndSaveStories( "Harry Potter", "Harry-and-Draco-s-Love-Shack.bin", "https://www.fanfiction.net/community/Harry-and-Draco-s-Love-Shack/11605/99/0/1/0/0/0/0/" )
#DownloadAndSaveStories( "Harry Potter", "Order-of-Stories.bin", "https://www.fanfiction.net/community/Order-of-Stories/10077/99/0/1/0/0/0/0/" )
#DownloadAndSaveStories( "My Hero Academia", "BakuDeku.bin", "https://www.fanfiction.net/community/BakuDeku/132352/99/0/1/0/0/0/0/" )

db = RunTestcaseFile( "My Hero Academia", "slash1.txt" )
#db = RunTestcaseFile( "Harry Potter", "slash1.txt" )
#db = RunTestcaseFile( "Harry Potter", "straight1.txt" )
#html = GetStoryChapterHTML( "/s/2721625/1/Freedom-And-Not-Peace" )
#html = GetStoryChapterHTML( "/s/1883681/1/Meetings" )
#html = GetStoryChapterHTML( "/s/5639518/1/The-Harem-War" )
#story = db.SearchTitle("The Harem War")[0]

"""
desc = story.chap1Beginning
pos = desc.find( "slash" )
begin = pos
while begin >= max( 0, pos - 25 ) and desc[begin] not in ".!":
    begin -= 1
begin += 1
prefixSafeWords = [ "no", "not", "free", "never", "fem", "implied" ]
window = desc[begin:pos]
splitWords = re.split( "\s+|\.|,|\?|\(|\)|\/|:|\"", window )
for safe in prefixSafeWords:
    if safe in splitWords:
        print( "found safe:", safe )

# sometimes there are "slash free", but want to avoid catching something like "contains Slash. Not cannon"
postfixSafeWords = [ "free" ]
window = desc[pos:pos+10]
for safeWord in postfixSafeWords:
    if safeWord in window:
        print( "found safeWord:", safeWord )
"""

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
"""