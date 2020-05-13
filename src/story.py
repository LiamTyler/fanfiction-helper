import time
import requests
from bs4 import BeautifulSoup

# M = Male, F = Female, U = Unknown/Unimportant
# Sometimes authors change character genders, which would be reflecte in currentGender (if parsed correctly)
class Character:
    def __init__( self, name, originalGender='U', currentGender='U' ):
        self.name           = name
        self.originalGender = originalGender
        self.currentGender  = currentGender

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

def GetStoryChapterText( chapterLink ):
    url = "https://fanfiction.net" + chapterLink
    r = requests.get( url )
    soup = BeautifulSoup( r.text, 'html.parser' )
    a = soup.body.find( 'div', attrs={'id':'storytext'} )
    return a.get_text( "\n" )

class Story:
    def __init__( self ):
        self.title        = ""
        self.rating       = ""
        self.words        = 0
        self.language     = ""
        self.author       = ""
        self.author_link  = ""
        self.description  = ""
        self.story_link   = ""
        self.story_id     = ""
        self.genres       = []
        self.characters   = []
        self.pairings     = [] # indices into self.characters array
        self.isSlash      = False
        self.complete     = False
        self.numReviews   = 0
        self.numFavorites = 0
        self.numFollows   = 0
        self.numChapters  = 0
        self.updateDate   = 0
        self.publishDate  = 0
        self.first1kWords = ""
        self._identifier  = ""

    def Parse( self, titleSection, descSection, characterDB={} ):
        # story_link
        pos = titleSection.find( "class=stitle")
        start = titleSection.find( '"', pos ) + 1
        pos = titleSection.find( '"><img', start )
        self.story_link = titleSection[start : pos]
        self.story_id = self.story_link[3:self.story_link.find( '/', 3 )]

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
        self.description = descSection[start : pos]

        # rating
        start = descSection.find( "Rated: ", pos ) + len( "Rated: " )
        pos = descSection.find( ' ', start )
        self.rating = descSection[start : pos]

        # language
        start = pos + 3
        pos = descSection.find( ' ', start )
        self.language = descSection[start : pos]

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
        [ self.updateDate, pos ]   = ParseStoryDescKeyNumVal( descSection, "Updated: <span data-xutime='", pos, "'" )
        [ self.publishDate, pos ]  = ParseStoryDescKeyNumVal( descSection, "Published: <span data-xutime='", pos, "'" )
        if self.updateDate == 0:
            self.updateDate = self.publishDate

        # complete
        completePos = descSection.find( " - Complete", pos )
        self.complete = completePos != -1
        self._identifier = self.title + "_" + self.author + "_" + self.story_id

        # characters
        pos = descSection.find( "</span>", pos ) + len( "</span>" )
        if not self.complete and descSection[pos] != ' ':
            return
        if self.complete and completePos == pos:
            return
        pos += 3
        end = descSection.find( "</div>", pos )
        if self.complete:
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
            if character.name not in characterDB:
                continue
            dbGender = characterDB[character.name]
            character.originalGender = dbGender
            character.currentGender = dbGender
            # check the description to see if any of the genders were swapped
            desc = story.description.lower()
            firstAndLast = character.name.split( ' ' )
            lens = [ len(name) for name in firstAndLast ]
            longestName = firstAndLast[lens.index(max(lens))].lower()
            pos = desc.find( longestName )
            while pos != -1:
                prefix = GetPrefixInCurrentSentence( desc, pos, 8 )
                if "fem" in prefix or "girl" in prefix:
                    print( "SWAP!", desc )
                    character.currentGender = 'F'
                    break
                if " male" in prefix or " boy" in prefix:
                    print( "SWAP!", desc )
                    character.currentGender = 'M'
                    break
                pos = desc.find( longestName, pos + 1 )

        self.first1kWords = GetStoryChapterText( self.story_link )[:1000]

    def __lt__( self, other ):
        return self._identifier < other._identifier

    def __eq__( self, other ):
        return self._identifier == other._identifier

    def __ne__( self, other ):
        return not( self.__eq__( self, other ) )

    def __repr__( self ):
        g = "[]"
        if len( self.genres ) == 1:
            g = self.genres[0]
        if len( self.genres ) > 1:
            g = " & "
            g = g.join( self.genres )
        
        s = self.title
        
        """
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
        

