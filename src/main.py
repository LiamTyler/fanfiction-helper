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
    dbName = fandomPath + "databases/regular.bin"
    if exists( dbName ):
        storyDB = LoadStoryDB( dbName )
    else:
        storyDB = StoryDB()

    storyDB = DownloadStories( info["regularLink"], info["slashExclusionKeywords"], info["characterGenders"], storyDB, maxPages )
    storyDB.Serialize( dbName )

    return storyDB

def ScanAllFandoms():
    dirs = [name for name in os.listdir( "fandoms/" ) if os.path.isdir( "fandoms/" + name )]
    for fandom in dirs:
        fandomPath = "fandoms/" + fandom + "/"
        ScanSingleFandom( fandomPath, 1 )

def Menu():
    dirs = [name for name in os.listdir( "fandoms/" ) if os.path.isdir( "fandoms/" + name )]
    for i in range( len( dirs ) ):
        fandom = dirs[i]
        fandomPath = "fandoms/" + fandom + "/"
        info = LoadFandomInfo( fandomPath + "info.txt" )
        print( i, ": ", fandom, ": ", info["regularLink"], sep="" )

if __name__ == "__main__":
    #if os.path.isdir( "../fandoms/" ):
    #Menu()
    #ScanSingleFandom( "fandoms/Harry Potter/", 4 )
    #ScanAllFandoms()
    #db = DownloadAndSaveStories( "Harry Potter", "regular.bin", "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10", 5 )
    #db = LoadStoryDB( "fandoms/Harry Potter/databases/regular.bin" )
    #print ( len( db.stories ), len( db.storyIdToIndexMap ) )
    #for s in db.stories:
    #    print( s )

    #app = QApplication( [] )
    #window = MainWindow()
    #app.exec_()

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 27015        # The port used by the server

    while( 1 ):
        data = ""
        with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as s:
            s.connect( (HOST, PORT) )
            s.sendall( b'Hello, world' )
            data = s.recv(1024)

        print('Received', repr(data))
        time.sleep( 2 )