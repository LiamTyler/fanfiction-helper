import requests
import time
from story_database import *

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

def DownloadStories( baseUrl, characterDB, maxPages=100000 ):
    storyDB  = StoryDB()

    # community urls differ slightly from regular search urls
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
    while page <= maxPages:
        if not page % 5:
            print( "Parsing page: ", page )
        url = beginUrl + str( page ) + endUrl
        response = requests.get( url )
        
        # If the urls dont match, then you've requested beyond the last page of stories
        if response.url != url:
            break

        newStories = ParsePage( response.text, characterDB )
        numStories += len(newStories)
        for story in newStories:
            storyDB.Insert( story )
        
        time.sleep( 1.000 )
        page += 1

    return storyDB