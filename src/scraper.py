import requests
import time
from story_database import *
import bs4
import cloudscraper
from cloudscraper import CloudflareChallengeError

#htmlScraper = None
MAX_CLOUDFLARE_ATTEMPTS = 0
CLOUDFLARE_WAIT_TIME = 2

def InitScraper():
    pass
    #global htmlScraper
    #htmlScraper = cloudscraper.create_scraper( browser={'browser': 'chrome','platform': 'windows','mobile': False} )

def GetHTMLPage( url, htmlScraper = None ):
    if not htmlScraper:
        htmlScraper = cloudscraper.create_scraper( browser={'browser': 'firefox','platform': 'windows','mobile': False} )
    page = None
    try:
        page = htmlScraper.get( url )
    except CloudflareChallengeError as e:
        #print( e, "Retrying..." )
        for index in range( 1, MAX_CLOUDFLARE_ATTEMPTS + 1 ):
            print( "Attempt:", index, "/", MAX_CLOUDFLARE_ATTEMPTS )
            time.sleep(CLOUDFLARE_WAIT_TIME)
            #htmlScraper = cloudscraper.create_scraper( browser={'browser': 'firefox','platform': 'windows','mobile': False} )
            try:
                page = htmlScraper.get( url )
            except CloudflareChallengeError:
                continue
        if page == None:
            print( "Could not get past CloudFlare error for URL:", url )
        
    return page

def GetStoryChapterHTML( chapterLink ):
    url = "https://fanfiction.net" + chapterLink
    r = GetHTMLPage( url )
    if r:
        soup = bs4.BeautifulSoup( r.content, 'html.parser' )
        a = soup.body.find( 'div', attrs={'id':'storytext'} )
        return a
    else:
        return ""

def GetStoryFirst1KWords( story ):
    # Try to get the beginning authors note from chapter 1, if it exists / detectable.
    html = GetStoryChapterHTML( story.story_link )
    if html == "":
        print( "Unable to get first 1K words for story:", story )
        story.chap1Beginning = ""
        return

    text = html.get_text( "\n" ).lower()
    storyBeginKeywords = [ "chapter one", "chapter 1", "prologue" ]
    pos = -1
    for key in storyBeginKeywords:
        pos = text.find( key )
        if pos != -1:
            text = text[:pos]
            break
    # Sometimes authors use a <hr> delimiter instead of "chapter 1" or whatever
    if pos == -1:
        if html.hr:
            allPrevElements = list( html.hr.previous_siblings )[::-1]
            prevText = ""
            for element in allPrevElements:
                currText = ""
                if isinstance( element, bs4.NavigableString ):
                    currText = str( element )
                else:
                    currText = element.get_text( "\n" )
                currText = currText.strip()
                if currText != "":
                    prevText += currText + "\n"
            prevText = prevText.strip()
            if prevText != "":
                text = prevText
    if len(text) > 2000:
        text = text[:2000]
    story.chap1Beginning = text.lower()

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

    return stories

def DownloadStories( baseUrl, characterDB, maxPages=100000 ):
    InitScraper()
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
        response = GetHTMLPage( url )
        print( "Pages Parsed: ", page )

        # If the urls dont match, then you've requested beyond the last page of stories
        if response.url != url:
            break

        newStories = ParseFFSearchPage( response.text, characterDB )

        for story in newStories:
            #time.sleep( 5 )
            print( "Parsing first 1K words from story:", story )
            GetStoryFirst1KWords( story )
            
            storyDB.Insert( story )
        
        #if not page % 5:
        #    print( "Pages Parsed: ", page )
        
        page += 1

    return storyDB