from story import *
from story_database import *
from filters import *
from scraper import *

def ClassifyDatabase( dbFilename, slash, excludeList=[] ):
    storyDB = StoryDB()
    storyDB.Deserialize( dbFilename )

    numRules = 6
    ruleCounts = [0]*numRules
    numStories = len(storyDB.stories)
    for i in range(len(storyDB.stories)):
        story = storyDB.stories[i]
        if story.story_link in excludeList:
            numStories -= 1
            continue

        val = IsSlash( story )
        story.isSlash = val > 0
        ruleCounts[val] += 1
        if slash:
            if val == 0:
                print( "(p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title + ", desc = '" + story.description + "'" )
        else:
            if val > 0:
                print( "Rule " + str(val) + " (p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title + ", desc = '" + story.description + "'" )

    print( "\nSummary\n-----------------------------" )
    for i in range( numRules ):
        print( "Rule " + str(i) + ": " + str(ruleCounts[i]) )
    print( "Straight: " + str(ruleCounts[0]), " Gay: " + str(sum(ruleCounts[1:])), " Total:", sum(ruleCounts) )
    print( "Straight %:", ruleCounts[0]/numStories )
    print( "\n" )

    return storyDB


def DownloadStories( bdName, baseUrl ):
    characterDB = LoadCharacterDictionary( "gender_lists/Harry-Potter_Character_Genders.txt" )
    storyDB = DownloadStories( baseUrl, characterDB )
    storyDB.Serialize( bdName )

    return storyDB

#DownloadStories( "databases/hp_stories_gay.bin", "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&_c1=6&_c2=9" ) # gay 664
#DownloadStories( "databases/hp_stories_straight1.bin", "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&_c1=6&_c2=9" ) # straight 155
#DownloadStories( "databases/hp_stories_straight2.bin", "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&_c1=6&_c2=9" ) # straight 264
#DownloadStories( "databases/hp_stories_straight3.bin", "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&_c1=6&_c2=9" ) # straight3 2116

#db = ClassifyDatabase( "databases/hp_stories_gay.bin", True )

excludeList = [
    '/s/2964792/1/And-Still-Can-t-Stop-Hoping',
    '/s/3205105/1/And-the-Truth-Shall-Set-You-Free',
    '/s/2917903/1/All-at-Once',
    '/s/2580283/1/Saving-Connor',
    '/s/2400483/1/Anarkia',
    '/s/2400488/1/Dawn',
]
db = ClassifyDatabase( "databases/hp_stories_straight3.bin", False, excludeList )


#N = len(db.stories)
#for i in range(N):
#    story = db.stories[i]
#    desc = story.description.lower()
#    if not story.isSlash and "slash" in desc and SlashSpecific( desc ) != 2:
#        print( "Story", i, ", desc = '", desc, "'" )

"""
desc = "a story in limerick verse.  hxd femslash.  possible prequel to the mistletoe incident.  harry and draco find themselves in a frightening situation at the halloween feast. "
desc = desc.lower()
pos = desc.find( "slash" )
if pos == -1:
    print( "pos == -1" )

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
if NearbySafeWord( desc, pos ) or word in [ "slashed", "slashing" ]:
    print( "neg/ not slash" )
else:
    print( "slash" )

begin = max( 0, pos - 25 )
end = pos + 10
safeWords = [ "no", "not", "free", "never", "fem" ]
words = re.split( ".|,| |\n", desc[begin:end] )
"""
