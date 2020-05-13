import requests
import time
from story_database import *

def ParseFFSearchPage( text, characterDB ):
    lines = text.split( '\n' )
    #global story_links, story_descs
    story_links = [ x for x in lines if "class='z-list" in x ]
    story_descs = [ x for x in lines if "class='z-indent" in x ]

    stories = []
    for i in range( len( story_links ) ):
        s = Story()
        s.Parse(story_links[i], story_descs[i], characterDB )
        stories.append( s )
        time.sleep( 1.3 )

    return stories

def DownloadStories( baseUrl, characterDB, maxPages=100000 ):
    print( "Downloading stories..." )
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

    page = 1
    while page <= maxPages:
        url = beginUrl + str( page ) + endUrl
        response = requests.get( url )
        print( "Pages Parsed: ", page )

        # If the urls dont match, then you've requested beyond the last page of stories
        if response.url != url:
            break

        newStories = ParseFFSearchPage( response.text, characterDB )
        for story in newStories:
            storyDB.Insert( story )
        
        #if not page % 5:
        #    print( "Pages Parsed: ", page )
        time.sleep( 1.3 )
        page += 1

    return storyDB