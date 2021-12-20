from story import *
from story_database import *
from filters import *
from scraper import *
from test import *
import undetected_chromedriver.v2 as uc
from os.path import exists
import os
from gui import *
import socket

def ScanSingleFandom( fandomPath, maxPages=100000 ):
    info = LoadFandomInfo( fandomPath + "info.txt" )
    DownloadFFNetStories( info["regularLink"], maxPages )

def ScanAllFandoms():
    dirs = [name for name in os.listdir( "fandoms/" ) if os.path.isdir( "fandoms/" + name )]
    for fandom in dirs:
        fandomPath = "fandoms/" + fandom + "/"
        ScanSingleFandom( fandomPath, 1 )

if __name__ == "__main__":
    #ScanAllFandoms()
    print( "Python Scraper spawned" )
    DownloadFFNetStories( "https://www.fanfiction.net/game/League-of-Legends/?&srt=1&lan=1&r=10&len=1" )
    #DownloadFFNetStories( "https://www.fanfiction.net/Tiger-Bunny-%E3%82%BF%E3%82%A4%E3%82%AC%E3%83%BC-%E3%83%90%E3%83%8B%E3%83%BC-Crossovers/8401/0/", 1 )

    print( "Python Scraper closing" )

    
    # s = Story()
    # s.title = "Hello"
    # s.author = "World"

    # HOST = '127.0.0.1'  # The server's hostname or IP address
    # PORT = 27015        # The port used by the server
    # data = s.GetNetworkRepr()
    # sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    # if not sock:
    #     print( "Could not create socket" )
    # else:
    #     sock.connect( (HOST, PORT) )
    #     time.sleep( 10 )
    #     sock.sendall( data )