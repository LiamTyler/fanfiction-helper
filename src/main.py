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

DownloadAndSaveStories( "databases/Harry-Potter_Harry-and-Draco-s-Love-Shack.bin", "https://www.fanfiction.net/community/Harry-and-Draco-s-Love-Shack/11605/99/0/1/0/0/0/0/" ) # gay 664
#DownloadAndSaveStories( "databases/Harry-Potter_Order-of-Stories.bin", "https://www.fanfiction.net/community/Order-of-Stories/10077/99/0/1/0/0/0/0/" ) # straight3 ~2100

db = RunTestcaseFile( "testcases/Harry-Potter_slash1.txt" )
# db = RunTestcaseFile( "testcases/Harry-Potter_straight1.txt" )


# N = len(db.stories)
# chapter = 0
# chapter1 = 0
# chapter2 = 0
# prologue = 0
# for i in range(N):
#     story = db.stories[i]
#     desc = story.first1kWords.lower()
#     if "chapter" in desc:
#         chapter += 1
#     if "chapter one" in desc:
#         chapter1 += 1
#     if "chapter 1" in desc:
#         chapter2 += 1
#     if "prologue" in desc:
#         prologue += 1
# 
# print( "Stories with 'chapter':", chapter )
# print( "Stories with 'chapter one':", chapter1 )
# print( "Stories with 'chapter 1':", chapter2 )
# print( "Stories with 'prologue':", prologue )
# print( "Total:", chapter1 + chapter2 + prologue, "/", chapter )

#story = db.SearchTitle("Æternus-Praestolatio")[0]
#chap = story.first1kWords

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