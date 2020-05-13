from story import *
from story_database import *
from filters import *
from scraper import *
from test import *

def DownloadAndSaveStories( bdName, baseUrl ):
    characterDB = LoadCharacterDictionary( "gender_lists/Harry-Potter_Character_Genders.txt" )
    storyDB = DownloadStories( baseUrl, characterDB )
    storyDB.Serialize( bdName )

    return storyDB

#DownloadAndSaveStories( "databases/Harry-Potter_Harry-and-Draco-s-Love-Shack.bin", "https://www.fanfiction.net/community/Harry-and-Draco-s-Love-Shack/11605/99/0/1/0/0/0/0/" ) # gay 664
#DownloadAndSaveStories( "databases/Harry-Potter_Order-of-Stories.bin", "https://www.fanfiction.net/community/Order-of-Stories/10077/99/0/1/0/0/0/0/" ) # straight3 ~2100

#db = RunTestcaseFile( "testcases/Harry-Potter_slash1.txt" )
db = RunTestcaseFile( "testcases/Harry-Potter_straight1.txt" )

N = len(db.stories)
for i in range(N):
    story = db.stories[i]
    if not story.isSlash:
        continue
    desc = story.description.lower()
    for character in story.characters:
        if character.originalGender != character.currentGender:
            print( story.title )


"""
story = db.SearchTitle("King and Queen: Stone and Snow")[0]
desc = story.description.lower()
for character in story.characters:
    firstAndLast = character.name.split( ' ' )
    lens = [ len(name) for name in firstAndLast ]
    longestName = firstAndLast[lens.index(max(lens))].lower()
    print( longestName )
    pos = desc.find( longestName )
    print( pos )
    if pos != -1 and character.originalGender == 'M':
        prefix = GetPrefixInCurrentSentence( desc, pos, 10 )
        print( prefix )
        if "fem" in prefix or "girl" in prefix:
            print( desc )

"""

"""
desc = "reality is tilting.\r\nRedemption is not easily had. Slytherin!Harry Alive!ParentsNo\r\nslash. Subtle Harry/Bellatrix pairing, that"
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

begin = pos
while begin >= max( 0, pos - 25 ) and desc[begin] not in ".!":
    begin -= 1
begin += 1
prefixSafeWords = [ "no", "not", "free", "never", "fem", "implied" ]
window = desc[begin:pos]
splitWords = re.split( "\s+|\.|,|\?|\(|\)|\/|:", window )

url = "https://www.fanfiction.net/s/2539995/1/Return-To-Reality"
r = requests.get( url )
soup = BeautifulSoup( r.text, 'html.parser' )
a = soup.body.find( 'div', attrs={'id':'storytext'} )
chap = a.get_text( "\n" )
"""