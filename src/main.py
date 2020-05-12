from story import *
from story_database import *
from filters import *
from scraper import *

filename = "databases/hp_stories_straight1.bin"
#baseUrl = "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&_c1=6&_c2=9"
#baseUrl = "https://www.fanfiction.net/community/Harry-and-Draco-s-Love-Shack/11605/99/0/1/0/0/0/0/" # gay (664)
baseUrl = "https://www.fanfiction.net/community/Harry-is-the-man-All-the-Best-of-Bashing-fics/108191/99/0/1/0/0/0/0/" # straight1 (155)
#baseUrl = "https://www.fanfiction.net/community/Excellent-Harry-Potter-Fanfiction/24898/99/0/1/0/0/0/0/" # straight2 (264)
#baseUrl = "https://www.fanfiction.net/community/Order-of-Stories/10077/99/0/1/0/0/0/0/" # straight3 (2116, 1 of them actually is gay)

storyDB = None
characterDB = LoadCharacterDictionary( "gender_lists/Harry-Potter_Character_Genders.txt" )

DOWNLOAD = True
if DOWNLOAD:
    storyDB = DownloadStories( baseUrl, characterDB )
    storyDB.Serialize( filename )
else:
    storyDB = StoryDB()
    storyDB.Deserialize( filename )

numRules = 4
ruleCounts = [0]*numRules
for i in range(len(storyDB.stories)):
    story = storyDB.stories[i]
    val = IsSlash( story )
    ruleCounts[val] += 1
    if val == 0:
        print( "(p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title )
    #if val > 0:
    #    print( "Rule " + str(val) + " (p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title )

print( "\nSummary\n-----------------------------")
for i in range( numRules ):
    print( "Rule " + str(i) + ": " + str(ruleCounts[i]) )
print( "Straight: " + str(ruleCounts[0]), " Gay: " + str(sum(ruleCounts[1:])), " Total:", sum(ruleCounts))
print( "Straight %:", ruleCounts[0]/len(storyDB.stories))
