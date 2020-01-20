import requests
import time
import pickle

def WriteToFile( x, fname ):
    file = open( fname, "w" )
    lines = x.split( '\n' )
    for l in lines:
        file.write( l + "\n" )


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
        self.pairings     = []
        self.complete     = False
        self.numReviews   = 0
        self.numFavorites = 0
        self.numFollows   = 0
        self.numChapters  = 0
        self.updateDate   = 0
        self.publishDate  = 0
        self._identifier  = ""
        

    def Parse( self, titleSection, descSection ):
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

        characterStr = descSection[pos : end]
        s = characterStr.split( "] [" )
        hasPairings = characterStr.find( '[' ) != -1
        for pair in s:
            p = pair.replace( '[', '' )
            p = pair.replace( ']', '' )
            p = pair.split( ", " )
            pairing = []
            for c in p:
                self.characters.append( c )
                pairing.append( c )
            if hasPairings:
                self.pairings.append( pairing )


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
        
        s = "Title: " + self.title + ", Author: " + self.author
        
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
        [ present, index ] = self.BinarySearch( story )
        if present:
            return
        self.stories = self.stories[:index] + [ story ] + self.stories[index:]
        

def ParsePage( text ):
    lines = text.split( '\n' )
    story_links = [ x for x in lines if "class='z-list" in x ]
    story_descs = [ x for x in lines if "class='z-indent" in x ]

    stories = []
    for i in range( len( story_links ) ):
        s = Story()
        s.Parse(story_links[i], story_descs[i] )
        stories.append( s )

    return stories

def DownloadStories( baseUrl ):
    storyDB = StoryDB()
    for pageIndex in range( 3 ):
        page = requests.get( baseUrl + "&p=" + str( pageIndex + 1 ) )

        newStories = ParsePage( page.text )
        if len( newStories ) == 0:
            break
        for story in newStories:
            storyDB.Insert( story )
        
        time.sleep( 0.800 )
        print( "Parsing page: ", pageIndex )

    return storyDB
    

def SerializeStories( filename, stories ):
    with open( filename, "wb" ) as file:
        pickle.dump( stories, file )

def DeserializeStories( filename ):
    stories = []
    with open( filename, "rb" ) as file:
        stories = pickle.load( file )

    return stories

DOWNLOAD = False
filename = "hp_stories.bin"
stories = None
if DOWNLOAD:
    stories = DownloadStories( "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&_c1=6&_c2=9" )
    SerializeStories( filename, stories.stories )
else:
    stories = StoryDB()
    stories.stories = DeserializeStories( filename )
