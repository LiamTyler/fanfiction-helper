import requests
import time
from story_database import *
import bs4
import undetected_chromedriver.v2 as uc
from filters import *
import socket

g_htmlScraper = None

def GetHTMLPage( url ):
    global g_htmlScraper
    if not g_htmlScraper:
        g_htmlScraper = uc.Chrome()
    g_htmlScraper.get( url )
    
    page = g_htmlScraper.page_source
    return g_htmlScraper.current_url, page

def GetStoryChapterHTML( story ):
    url = story.GetUrl()
    newUrl, text = GetHTMLPage( url )
    if text:
        soup = bs4.BeautifulSoup( text, 'html.parser' )
        a = soup.body.find( 'div', attrs={'id':'storytext'} )
        return a
    else:
        return ""

def GetStoryFirst1KWords( story ):
    time.sleep( 1 )
    # Try to get the beginning authors note from chapter 1, if it exists / detectable.
    html = GetStoryChapterHTML( story )
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

def ParseFFSearchPage( text ):
    lines = text.split( '\n' )

    #global story_links, story_descs
    story_links = [ x for x in lines if "class=\"z-list" in x ]
    story_descs = [ x for x in lines if "class=\"z-indent" in x ]

    stories = []
    for i in range( len( story_links ) ):
        s = Story()
        s.ParseFF( story_links[i], story_descs[i] )
        stories.append( s )

    return stories

def DownloadFFNetStories( baseUrl, maxPages=100000 ):
    print( "Downloading stories..." )

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 27015        # The port used by the server

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
        endUrl = baseUrl[baseUrl.find( '/', i+1 ):]
    else:
        beginUrl += "&p="

    page = 1
    while page <= maxPages:
        url = beginUrl + str( page ) + endUrl
        print( "Parsing page:", page, "/", maxPages )
        responseUrl, responseText = GetHTMLPage( url )

        # If the urls dont match, then you've requested beyond the last page of stories
        if responseUrl != url:
            print( "Page", page, "does not exist" )
            break

        newStories = ParseFFSearchPage( responseText )

        for story in newStories:
            data = story.GetNetworkRepr()
            #data = str( len( data ) + 1 ).encode() + b'\0' + str( 1 ).encode() + b'\0' + data
            data = str( 1 ).encode() + b'\0' + data
            s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            if not s:
                print( "Could not create socket" )
            else:
                s.connect( (HOST, PORT) )
                s.sendall( data )
                    
        page += 1