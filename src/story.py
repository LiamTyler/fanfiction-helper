import time
from enum import IntEnum

# M = Male, F = Female, U = Unknown/Unimportant
# Sometimes authors change character genders, which would be reflecte in currentGender (if parsed correctly)
class Character:
    def __init__( self, name, originalGender='U', currentGender='U' ):
        self.name           = name
        self.originalGender = originalGender
        self.currentGender  = currentGender

    def __eq__( self, o ):
        return self.name == o.name and self.originalGender == o.originalGender and self.currentGender == o.currentGender

    def __repr__( self ):
        return "(" + self.name + ", " + self.currentGender + ")"

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

class StoryFlags( IntEnum ):
    IS_COMPLETE = 1,
    IS_ABANDONED = 2,
    IS_SLASH_AUTO = 3,
    IS_SLASH_MANUAL = 4,
    HAVE_READ_ENTIRELY = 5,
    HAVE_READ_PARTIALLY = 6,
    NOT_INTERESTED = 7,
    INTERESTED = 8

class Story:
    def __init__( self ):
        self.title          = ""
        self.rating         = "" # K, K+, T, or M
        self.author         = ""
        self.author_link    = ""
        self.description    = ""
        self.story_id       = ""
        self.genres         = []
        self.characters     = []
        self.pairings       = [] # indices into self.characters array
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
        d = self.title.encode() + b'\0' + self.author.encode() + b'\0'
        return d

    def ParseFF( self, titleSection, descSection ):
        self.storySource = "FF"
        div3 = descSection.find( "</div></div></div>" )
        descSection = descSection[:div3 + len( "</div></div></div>" )]

        # story_link
        pos = titleSection.find( '"/s/' )
        start = pos + 1
        pos = titleSection.find( '"><img', start )
        story_link = titleSection[start : pos]
        self.story_id = story_link[3:story_link.find( '/', 3 )]

        # title
        start = titleSection.find( '>', pos + 2 ) + 1
        pos = titleSection.find( '</a>', start )
        self.title = titleSection[start : pos]

        # author_link
        pos = titleSection.find( 'by <a href="', pos )
        start = titleSection.find( '"', pos ) + 1
        pos = titleSection.find( '>', pos )
        self.author_link = titleSection[start : pos]

        #author
        start = pos + 1
        pos = titleSection.find( '</a>', pos )
        self.author = titleSection[start : pos]

        # description
        start = descSection.find( '>' ) + 1
        pos = descSection.find( '<div class', start )
        self.description = descSection[start : pos].lower()

        # rating
        start = descSection.find( "Rated: ", pos ) + len( "Rated: " )
        pos = descSection.find( ' ', start )
        self.rating = descSection[start : pos]

        # language
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
                self.pairings.append( currentPairing )
                currentPairing = []
                inPairing = False

            self.characters.append( Character( name ) )
            if inPairing:
                currentPairing.append( len( self.characters )-1 )

        # update genders for characters
        for character in self.characters:
            # check the description to see if any of the genders were swapped
            desc = self.description
            firstAndLast = character.name.split( ' ' )
            lens = [ len(name) for name in firstAndLast ]
            longestName = firstAndLast[lens.index(max(lens))].lower()
            pos = desc.find( longestName )
            while pos != -1:
                prefix = GetPrefixInCurrentSentence( desc, pos, 8 )
                if "fem" in prefix or "girl" in prefix:
                    character.currentGender = 'F'
                    break
                if " male" in prefix or " boy" in prefix:
                    character.currentGender = 'M'
                    break
                pos = desc.find( longestName, pos + 1 )

    def __lt__( self, other ):
        return self.story_id < other.story_id

    def __eq__( self, other ):
        return self.story_id == other.story_id

    def __ne__( self, other ):
        return not( self.__eq__( self, other ) )

    def __hash__( self ):
        return hash( self.story_id )

    def __str__( self ):
        s = "'" + self.title + "' by '" + self.author + "'"
        
        """
        g = "[]"
        if len( self.genres ) == 1:
            g = self.genres[0]
        if len( self.genres ) > 1:
            g = " & "
            g = g.join( self.genres )
        "Title: " + self.title + '\n' + \
            "Num Words: " + str( self.words ) + '\n' + \
            "Num Chapters: " + str( self.numChapters ) + '\n' + \
            "Num Reviews: " + str( self.numReviews ) + '\n' + \
            "Num Favorites: " + str( self.numFavorites ) + '\n' + \
            "Num Follows: " + str( self.numFollows ) + '\n' + \
            "Rating: " + self.rating + '\n' + \
            "Genres: " + g + '\n' + \
            "Characters: " + str( self.characters ) + '\n' + \
            "Pairings: " + str( self.pairings ) + '\n' + \
            "Author: " + self.author + " -> " + self.author_link + '\n' + \
            "Language: " + self.language + '\n' + \
            "Story Link: " + self.story_link + '\n' + \
            "Update Date: " + time.strftime( '%m/%d/%Y', time.localtime( self.updateDate ) ) + '\n' + \
            "Publish Date: " + time.strftime( '%m/%d/%Y', time.localtime( self.publishDate ) ) + '\n' + \
            "Description: " + self.description
        """
        return s

    def __repr__( self ):        
        return self.__str__()
        

