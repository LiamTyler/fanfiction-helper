from difflib import SequenceMatcher
from c_shared import *

def StrSimilar( a,b ):
    return SequenceMatcher( None, a, b ).ratio()

class RelationshipType( IntEnum ):
    ROMANTIC = 0,
    PLATONIC = 1

class Relationship:
    def __init__( self, characters, type ):
        self.characters = characters
        self.type = type

def ParseStoryDescKeyNumVal( desc, key, startPos = 0, endMarker = ' ' ):
        start = desc.find( key, startPos )
        if start == -1:
            return [ 0, startPos ]
        else:
            start += len( key )
        pos = desc.find( endMarker, start )
        s = desc[start : pos]
        s = s.replace( ',', '')
        return [ int( s ), pos ]  

def GetPrefixInCurrentSentence( string, pos, maxLen=25 ):
    begin = pos
    while begin >= max( 0, pos - maxLen ):
        if string[begin] == '.':
            break
        # Catch end of normal sentence "! ", but not exclamation tags like "girl!Harry"
        if string[begin] == '!' and string[begin+1]==' ':
            break
        begin -= 1
    begin += 1

    return string[begin:pos]

def EncodeStr( s ):
    return s.encode() + b'\0'

def EncodeNum( num ):
    return str( num ).encode() + b'\0'

def EncodeStrList( stringList ):
    L = len( stringList )
    d = EncodeNum( L )
    for s in stringList:
        d += EncodeStr( s )
    return d

class Story:

    def __init__( self ):
        self.title          = ""
        self.contentRating  = "" # K, K+, T, or M
        self.author         = ""
        self.author_link    = ""
        self.description    = ""
        self.story_id       = ""
        self.genres         = []
        self.characters     = []
        self.relationships  = []
        self.fandoms        = []
        self.words          = 0
        self.numReviews     = 0
        self.numFavorites   = 0
        self.numFollows     = 0
        self.numChapters    = 0
        self.publishDate    = 0
        self.chap1Beginning = ""
        self.flags          = 0
        self.myRating       = 0 # out of 10
        self.updateDates    = []
        self.freeformTags   = []
        self.storySource    = "" # FF or AO3

    def HasFlag( self, flag ):
        return self.flags & 1 << int(flag)

    def SetFlag( self, flag ):
        self.flags |= 1 << int(flag)

    def ClearFlag( self, flag ):
        if self.HasFlag( flag ):
            self.flags -= 1 << int(flag)

    def IsSlash( self ):
        return self.HasFlag( StoryFlags.IS_SLASH_AUTO ) or self.HasFlag( StoryFlags.IS_SLASH_MANUAL )

    def GetUrl( self, chap = 1 ):
        link = "https://www.fanfiction.net/s/" + self.story_id + "/" + str( chap ) + "/"
        return link

    def GetNetworkRepr( self ):
        d = EncodeStr( self.storySource ) + \
            EncodeStr( self.title ) + \
            EncodeStr( self.author ) + \
            EncodeStr( self.author_link ) + \
            EncodeStr( self.description ) + \
            EncodeStrList( self.fandoms ) + \
            EncodeStrList( self.characters )
        d += EncodeNum( len( self.relationships ) )
        for r in self.relationships:
            d += EncodeStr( r.characters[0] )
            d += EncodeStr( r.characters[1] )
            d += EncodeNum( int( r.type ) )
        d += EncodeStrList( self.freeformTags )
        d += EncodeStrList( [str(x) for x in self.updateDates ] )

        d += EncodeStr( self.story_id )
        d += EncodeNum( self.flags )
        d += EncodeNum( self.words )
        d += EncodeNum( self.numReviews )
        d += EncodeNum( self.numFavorites )
        d += EncodeNum( self.numFollows )
        d += EncodeNum( self.numChapters )
        d += EncodeStrList( self.genres )
        d += EncodeStr( self.contentRating )
        
        return d

    def ParseFF( self, url, inFandom, titleSection, descSection ):
        self.storySource = ""
        if "www.fanfiction.net/" in url:
            self.storySource = "FF"
        elif "archiveofourown.org/" in url:
            self.storySource = "AO3"
        
        div3 = descSection.find( "</div></div></div>" )
        descSection = descSection[:div3 + len( "</div></div></div>" )]

        pos = titleSection.find( '"/s/' )
        start = pos + 1
        pos = titleSection.find( '"><img', start )
        story_link = titleSection[start : pos]
        self.story_id = story_link[3:story_link.find( '/', 3 )]

        start = titleSection.find( '>', pos + 2 ) + 1
        pos = titleSection.find( '</a>', start )
        self.title = titleSection[start : pos]

        pos = titleSection.find( 'by <a href="', pos )
        start = titleSection.find( '"', pos ) + 1
        pos = titleSection.find( '>', pos )
        self.author_link = titleSection[start : pos-1]

        start = pos + 1
        pos = titleSection.find( '</a>', pos )
        self.author = titleSection[start : pos]

        start = descSection.find( '>' ) + 1
        pos = descSection.find( '<div class', start )
        self.description = descSection[start : pos].lower()

        if "-Crossovers/" in url:
            start = descSection.find( "Crossover - ", pos ) + len( "Crossover - " )
            end = descSection.find( " - Rated:", pos )
            fandoms = descSection[start:end]
            #fandoms = fandoms.replace( "&amp;", "&" )
            fandomsList = fandoms.split( " & " )
            if len( fandomsList ) < 2 or len( fandomsList ) > 4:
                print( "Invalid number of fandoms in string '" + fandoms + "'" )
            elif len( fandomsList ) == 2:
                self.fandoms = fandomsList
            else:
                mostSimilarIndex = 0
                mostSimilarValue = 0
                for i in range( 0, len( fandomsList ) ):
                    v = StrSimilar( inFandom, " & ".join( fandomsList[:i+1] ) )
                    if v > mostSimilarValue:
                        mostSimilarIndex = i
                        mostSimilarValue = v
                fandom1 = " & ".join( fandomsList[:mostSimilarIndex+1] )
                fandom2 = " & ".join( fandomsList[mostSimilarIndex+1:] )
                self.fandoms = [ fandom1, fandom2 ]
                
        else:
            self.fandoms = [ inFandom ]

        start = descSection.find( "Rated: ", pos ) + len( "Rated: " )
        pos = descSection.find( ' ', start )
        self.contentRating = descSection[start : pos]

        start = pos + 3
        pos = descSection.find( ' ', start )
        #self.language = descSection[start : pos]

        # genres
        chap_start = descSection.find( "Chapters", pos )
        if chap_start != pos + 3:
            genresStr = descSection[pos + 3 : chap_start - 3]
            genres = genresStr.split('/')
            for genre in genres:
                if genre == "Comfort":
                    continue
                if genre == "Hurt":
                    self.genres.append( "Hurt/Comfort" )
                else:
                    self.genres.append( genre )

        [ self.numChapters, pos ]  = ParseStoryDescKeyNumVal( descSection, "Chapters: ", pos )
        [ self.words, pos ]        = ParseStoryDescKeyNumVal( descSection, "Words: ", pos )
        [ self.numReviews, pos ]   = ParseStoryDescKeyNumVal( descSection, "Reviews: ", pos )
        [ self.numFavorites, pos ] = ParseStoryDescKeyNumVal( descSection, "Favs: ", pos )
        [ self.numFollows, pos ]   = ParseStoryDescKeyNumVal( descSection, "Follows: ", pos )
        [ updateDate, pos ]        = ParseStoryDescKeyNumVal( descSection, "Updated: <span data-xutime=\"", pos, '"' )
        [ self.publishDate, pos ]  = ParseStoryDescKeyNumVal( descSection, "Published: <span data-xutime=\"", pos, '"' )
        if updateDate == 0:
            self.updateDates = [ self.publishDate ]
        else:
            self.updateDates = [ self.publishDate, updateDate ]

        # complete
        completePos = descSection.find( " - Complete", pos )
        isComplete = False
        if completePos != -1:
            self.SetFlag( StoryFlags.IS_COMPLETE )
            isComplete = True
        self._identifier = self.title + "_" + self.author + "_" + self.story_id

        # characters
        pos = descSection.rfind( "</span>", pos ) + len( "</span>" )
        if not isComplete and descSection[pos] != ' ':
            return
        if isComplete and completePos == pos:
            return
        pos += 3
        end = descSection.find( "</div>", pos )
        if isComplete:
            end = completePos

        characterStr = descSection[pos:end]
        characterStr = descSection[pos:end]
        characterStr = characterStr.replace( "] ", "], " )
        characters = [ s.strip() for s in characterStr.split( ',' ) ]
        inPairing = False
        currentPairing = []
        for character in characters:
            name = character.strip()
            if character[0] == '[':
                name = name[1:]
                inPairing = True
            if character[-1] == ']':
                name = name[:-1]
                currentPairing.append( len( self.characters ) )
                self.relationships.append( currentPairing )
                currentPairing = []
                inPairing = False

            self.characters.append( name )
            if inPairing:
                currentPairing.append( len( self.characters )-1 )

        # expand out relationships: [ Harry/Hermione/Fleur ] -> [Harry/Hermione, Harry/Fleur, Hermione/Fleur]
        rel = self.relationships
        self.relationships = []
        for r in rel:
            for i in range(len(r)):
                for j in range( i + 1, len(r)):
                    self.relationships.append( Relationship( [ self.characters[r[i]], self.characters[r[j]] ], RelationshipType.ROMANTIC ) )

    def __str__( self ):
        s = "'" + self.title + "' by '" + self.author + "'"

        # s = "Title: " + self.title + '\n' + \
        #     "Author: " + self.author + " -> " + self.author_link + '\n' + \
        #     "Description: " + self.description + '\n' + \
        #     "Fandoms: " + str( self.fandoms ) + '\n' + \
        #     "Characters: " + str( self.characters ) + '\n' + \
        #     "Relationships: " + str( self.relationships ) + '\n' + \
        #     "Freeform Tags: " + str( self.freeformTags ) + '\n' + \
        #     "Update Infos: " + str( self.updateDates ) + '\n' + \
        #     "Flags: " + str( self.flags ) + '\n' + \
        #     "StoryID: " + str( self.story_id ) + '\n' + \
        #     "Num Words: " + str( self.words ) + '\n' + \
        #     "Num Reviews: " + str( self.numReviews ) + '\n' + \
        #     "Num Favorites: " + str( self.numFavorites ) + '\n' + \
        #     "Num Follows: " + str( self.numFollows ) + '\n' + \
        #     "Num Chapters: " + str( self.numChapters ) + '\n' + \
        #     "Genres: " + str( self.genres ) + '\n' + \
        #     "StorySource: " + self.storySource + '\n' + \
        #     "ContentRating: " + self.contentRating + '\n'

        #"Update Date: " + time.strftime( '%m/%d/%Y', time.localtime( self.updateDate ) ) + '\n'
        return s

    def __repr__( self ):        
        return self.__str__()
        

# data = already split by '\0'
def StoryFromNetworkBytes( data, i ):
    s = Story()
    s.storySource = int( data[i] ); i += 1
    s.title = data[i]; i += 1
    s.author = data[i]; i += 1
    s.description = data[i]; i += 1
    numCharacters = int( data[i] ); i += 1
    for _ in range( numCharacters ):
        s.characters.append( data[i] ); i += 1
    s.story_id = data[i]; i += 1
    s.flags = int( data[i] ); i += 1
    s.words = int( data[i] ); i += 1
    s.numChapters = int( data[i] ); i += 1
    s.numReviews = int( data[i] ); i += 1
    s.numFavorites = int( data[i] ); i += 1
    s.numFollows = int( data[i] ); i += 1
    s.contentRating = ContentRatingStringFromNum( int( data[i] ) ); i += 1

    return s, i