import requests
import time
from story_database import *
import bs4
import undetected_chromedriver.v2 as uc
from filters import *
import socket
import os

def ShouldShutdown():
    return os.path.exists( "shutdown.txt" )

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

def ParseFFSearchPage( url, text ):
    lines = text.split( '\n' )

    fandom = ""
    # get fandom, ex: "Harry-Potter" in www.fanfiction.net/book/Harry-Potter/?whatever
    p = url.find( "www.fanfiction.net/" ) + len( "www.fanfiction.net/" )
    if "-Crossovers/" in url:
        start = p
        end = url.find( '/', start )
        fandom = url[start:end]
        p = fandom.find("-Crossovers")
        fandom = fandom[:p]
    else:
        start = url.find( '/', p ) + 1
        end = url.find( '/', start )
        fandom = url[start:end]


    #global story_links, story_descs
    story_links = [ x.replace( "&amp;", "&" ) for x in lines if "class=\"z-list" in x ]
    story_descs = [ x.replace( "&amp;", "&" ) for x in lines if "class=\"z-indent" in x ]

    stories = []
    for i in range( len( story_links ) ):
        s = Story()
        s.ParseFF( url, fandom, story_links[i], story_descs[i] )
        stories.append( s )

    return stories

def DownloadFFNetStories( baseUrl, maxPages=100000 ):
    #print( "Downloading stories..." )

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 27015        # The port used by the server

    beginUrl = baseUrl + "&p="

    page = 1
    while page <= maxPages:
        url = beginUrl + str( page )
        #print( "Parsing page:", page, "/", maxPages )
        responseUrl, responseText = GetHTMLPage( url )

        # If the urls dont match, then you've requested beyond the last page of stories
        # Note: used to be true, doesnt seem to be anymore?
        if responseUrl != url:
            print( "Reached final page, done processing stories for URL:", baseUrl )
            break

        newStories = ParseFFSearchPage( baseUrl, responseText )
        if len( newStories ) == 0:
            print( "Reached final page, done processing stories for URL:", baseUrl )
            break
            
        if ShouldShutdown():
            break

        for story in newStories:
            #print( "Sending Story:\n", story )
            #print("\n")
            data = EncodeNum( 1 ) + story.GetNetworkRepr()
            s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            if not s:
                print( "Could not create socket" )
            else:
                s.connect( (HOST, PORT) )
                s.sendall( data )
                    
        page += 1