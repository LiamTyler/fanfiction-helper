import requests
import time
import pickle
from story import *

story_links = []
story_descs = []

def WriteToFile( x, fname ):
    file = open( fname, "w" )
    lines = x.split( '\n' )
    for l in lines:
        file.write( l + "\n" )

class StoryDB:
    def __init__( self, stories = [] ):
        self.stories = stories

    def BinarySearch( self, story ):
        start = 0
        end   = len( self.stories )
        if end == 0:
            return [ False, 0 ]

        #print( "start = ", start, ", end = ", end )
        while start < end:
            #print( "start = ", start, ", end = ", end )
            mid = ( start + end ) // 2
            if self.stories[mid] < story:
                start = mid + 1
            elif self.stories[mid] > story:
                end = mid - 1
            else:
                return [ True, mid ]

        #print( "len = ", len(self.stories), ", start = ", start, ", end = ", end )
        if start >= len( self.stories ) or start > end:
            return [ False, start ]
        if self.stories[start] > story:
            return [ False, start - 1 ]
        else:
            return [ False, start ]
        

    def Exists( self, story ):
        [ present, index ] = self.BinarySearch( story )
        return present

    def Insert( self, story ):
        self.stories.append( story )
        #[ present, index ] = self.BinarySearch( story )
        #if present:
        #    return
        #self.stories = self.stories[:index] + [ story ] + self.stories[index:]

    def Serialize( self, filename ):
        with open( filename, "wb" ) as file:
            pickle.dump( self.stories, file )
    
    def Deserialize( self, filename ):
        with open( filename, "rb" ) as file:
            self.stories = pickle.load( file )
        

def ParsePage( text, characterDB ):
    lines = text.split( '\n' )
    #global story_links, story_descs
    story_links = [ x for x in lines if "class='z-list" in x ]
    story_descs = [ x for x in lines if "class='z-indent" in x ]

    stories = []
    for i in range( len( story_links ) ):
        s = Story()
        s.Parse(story_links[i], story_descs[i], characterDB )
        stories.append( s )

    return stories

def IsSlash( story ):
    # Check for explicit male pairings
    for pair in story.pairings:
        numMales = 0
        for characterIndex in pair:
            numMales += story.characters[characterIndex].currentGender == 'M'

        if numMales > 1:
            story.isSlash = True
            #print( "Story:", story.title, "is slash" )
            return True

    # if the genre is romance and every character is male, probably slash
    numMales = 0
    for char in story.characters:
        numMales += char.currentGender == 'M'
    if "Romance" in story.genres and numMales > 1 and numMales == len(story.characters):
        #print( "Story:", story.title, "is Probably slash?" )
        story.isSlash = True
        return True

    # check description for telling keywords without "no" or "not" in front of them
    desc = story.description.lower()
    keywords = ["yaoi", "slash", "mpreg", "m-preg"]
    for keyword in keywords:
        pos = desc.find( keyword )
        if pos != -1:
            if "no" not in desc[pos-5:pos]:
                #print( "Story:", story.title, "is SUSPECTED slash" )
                story.isSlash = True
                return True

    print( "Story:", story.title, "is NOT slash" )
    return False

def DownloadStories( baseUrl, characterDB, maxPages=100000 ):
    storyDB  = StoryDB()
    beginUrl = baseUrl
    endUrl   = ""
    if "www.fanfiction.net/community" in baseUrl:
        i = len(baseUrl)
        numForwardSlashes = 0
        while numForwardSlashes != 6:
            i -= 1
            numForwardSlashes += baseUrl[i] == '/'
        beginUrl = baseUrl[:i+1]
        endUrl = baseUrl[baseUrl.find( '/', i+1):]
    else:
        beginUrl += "&p="

    numStories = 0
    numSlash = 0
    page = 1
    while page < maxPages:
        print( "Parsing page: ", page )
        url = beginUrl + str( page ) + endUrl
        response = requests.get( url )
        
        # If the urls dont match, then you've requested beyond the last page of stories
        if response.url != url:
            break

        newStories = ParsePage( response.text, characterDB )
        numStories += len(newStories)
        for story in newStories:
            if not IsSlash( story ):
                storyDB.Insert( story )
            else:
                numSlash += 1
        
        time.sleep( 1.000 )
        page += 1

    print( "Slash: " + str(numSlash) + "/" + str(numStories) )

    return storyDB

# returns dictionary is key = name (string), value = either M, F, or U (unknown) (char)
def LoadCharacterDictionary( filename ):
    db = dict()
    file = open( filename, "r" )
    for line in file:
        endOfName = line.find( "\"", 1 )
        name = line[1:endOfName]
        gender = line[-2]
        db[name] = gender

    return db


DOWNLOAD = True
filename = "hp_stories.bin"
#baseUrl  = "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&_c1=6&_c2=9"
baseUrl  = "https://www.fanfiction.net/community/Harry-and-Draco-s-Love-Shack/11605/99/0/1/0/0/0/0/" # gay
#baseUrl  = "https://www.fanfiction.net/community/Harry-is-the-man-All-the-Best-of-Bashing-fics/108191/99/0/1/0/0/0/0/" # not gay

storyDB = None
characterDB = LoadCharacterDictionary( "Harry-Potter_Character_Genders.txt" )


if DOWNLOAD:
    storyDB = DownloadStories( baseUrl, characterDB )
    storyDB.Serialize( filename )
else:
    storyDB = StoryDB()
    storyDB.Deserialize( filename )


"""
page = requests.get( baseUrl + "&p=" + str( 1 ) )
newStories = ParsePage( page.text )


pos += 3
end = descSection.find( "</div>", pos )
characterStr = descSection[pos:end]
characterStr = characterStr.replace( "] ", "], " )
characters = [ s.strip() for s in re.split( ',', characterStr ) ]
inPairing = False
currentPairing = []
pairings = []
listcharacters = []
for character in characters:
    name = character.strip()
    print(name)
    if character[0] == '[':
        name = name[1:]
        inPairing = True
    print(name)
    if character[-1] == ']':
        name = name[:-1]
        currentPairing.append( name )
        pairings.append( currentPairing )
        currentPairing = []
        inPairing = False
    print(name)

    listcharacters.append( name )
    if inPairing:
        currentPairing.append( name )
"""
