from story import *
from story_database import *
from filters import *
from scraper import *
from test import *
import cloudscraper
import undetected_chromedriver.v2 as uc

def DownloadAndSaveStories( fandomName, dbName, baseUrl, maxPages=1000000 ):
    fandom = "fandoms/" + fandomName + "/"
    dbName = fandom + "databases/" + dbName
    info = LoadFandomInfo( fandom + "info.txt" )
    characterDB = info["characterGenders"]
    storyDB = DownloadStories( baseUrl, characterDB, maxPages )
    storyDB.Serialize( dbName )

    return storyDB

#DownloadAndSaveStories( "Harry Potter", "Harry-and-Draco-s-Love-Shack.bin", "https://www.fanfiction.net/community/Harry-and-Draco-s-Love-Shack/11605/99/0/1/0/0/0/0/" )
#DownloadAndSaveStories( "Harry Potter", "Order-of-Stories.bin", "https://www.fanfiction.net/community/Order-of-Stories/10077/99/0/1/0/0/0/0/" )
#DownloadAndSaveStories( "My Hero Academia", "BakuDeku.bin", "https://www.fanfiction.net/community/BakuDeku/132352/99/0/1/0/0/0/0/" )

#db = RunTestcaseFile( "My Hero Academia", "slash1.txt" )
#db = RunTestcaseFile( "Harry Potter", "slash1.txt" )
#db = RunTestcaseFile( "Harry Potter", "straight1.txt" )
#html = GetStoryChapterHTML( "/s/2721625/1/Freedom-And-Not-Peace" )
#html = GetStoryChapterHTML( "/s/1883681/1/Meetings" )
#html = GetStoryChapterHTML( "/s/5639518/1/The-Harem-War" )
#story = db.SearchTitle("The Harem War")[0]

#stories = DownloadAndSaveStories( "Harry Potter", "regular.bin", "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10", 1 )
#print(stories)

#htmlScraper = cloudscraper.create_scraper( browser={'browser': 'chrome','platform': 'windows','mobile': False} )
#page = GetHTMLPage( "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10", htmlScraper )
#page = GetHTMLPage( "https://fanfiction.net/s/13952690/1/The-Devil-s-Smile", htmlScraper )
#page = GetHTMLPage( "https://fanfiction.net/s/13895922/1/The-Girl-Who-Lived-Sort-Of", htmlScraper )

#import undetected_chromedriver as uc
#from selenium import webdriver
#import time



#options = webdriver.ChromeOptions() 
#options = uc.ChromeOptions()
#options.headless=True
#options.add_argument('--headless')
#options.add_argument("start-maximized")
# driver = uc.Chrome(options=options)
url1 = 'https://fanfiction.net/s/13952690/1/The-Devil-s-Smile'
url2 = 'https://fanfiction.net/s/13895922/1/The-Girl-Who-Lived-Sort-Of'
# driver.get(url1)



# f = open( "test2.html", "w" )
# f.write( driver.page_source )
# f.close()


# scraper = cloudscraper.create_scraper()
# html = scraper.get("https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10").content

# s = requests.Session()
# res = s.get('https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10')
# cookies = dict(res.cookies)
# res = s.post('https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10',
#     verify=False, 
#     cookies=cookies)

# response = requests.get( "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10" )
# f = open( 'page.html', 'w' )
# f.write( str( html ) )
# f.close()

if __name__ == "__main__":
    driver = uc.Chrome()
    driver.get( url1 )  # known url using cloudflare's "under attack mode"

    f = open( "test1.html", "w" )
    f.write( driver.page_source )
    f.close()

    driver.get( url2 )  # known url using cloudflare's "under attack mode"
    f = open( "test2.html", "w" )
    f.write( driver.page_source )
    f.close()