from story import *
from story_database import *
from filters import *

def TestDatabase( storyDB, slash, keywordExclusionList = [], storyExcludeList=[] ):
    numRules = 7
    ruleCounts = [0]*numRules
    numStories = len(storyDB.stories)
    for i in range(len(storyDB.stories)):
        story = storyDB.stories[i]
        if story.story_id in storyExcludeList:
            numStories -= 1
            continue

        val = IsSlash( story, keywordExclusionList )
        story.isSlash = val > 0
        ruleCounts[val] += 1
        if slash:
            if val == 0:
                #print( "(p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title + ", desc = '" + story.description + "'" )
                print( "(p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title )
        else:
            if val > 0:
                #print( "Rule " + str(val) + " (p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title + ", desc = '" + story.description + "'" )
                print( "Rule " + str(val) + " (p"+str(1 + i//25) + ", s" + str(i - 25*(i//25)) + "): " + story.title )

    print( "\nSummary\n-----------------------------" )
    for i in range( 1, numRules ):
        print( "Rule " + str(i) + ": " + str(ruleCounts[i]) )
    print( "Straight: " + str(ruleCounts[0]), " Gay: " + str(sum(ruleCounts[1:])), " Total:", sum(ruleCounts) )
    print( "Straight %:", ruleCounts[0]/numStories )
    print( "Gay %:", sum(ruleCounts[1:])/numStories )
    print( "\n" )

    return ruleCounts[0], sum(ruleCounts[1:]), sum(ruleCounts)

def RunTestcaseFile( fandomName, testcaseFilename ):
    fandom = "fandoms/" + fandomName + "/"
    testcaseFilename = fandom + "testcases/" + testcaseFilename
    try:
        f = open( testcaseFilename, "r" )
    except:
        print( "Could not open file '" + testcaseFilename + "'" )
        return

    info = LoadFandomInfo( fandom + "info.txt" )
    keywordExclusionList = info["exclusionKeywords"]
    lines = [ line.strip() for line in f.readlines() ]
    url = lines[0]
    slash = lines[1] == "slash"
    db = LoadStoryDB( fandom + lines[2] )
    storyExcludeList = []
    i = 3
    while lines[i] != '':
        story_link = lines[i]
        # use story_id because some titles with unicode dont seem to parse correctly
        story_id = story_link[3:story_link.find('/', 3)]
        storyExcludeList.append( story_id )
        i += 1

    results = TestDatabase( db, slash, keywordExclusionList, storyExcludeList )

    return db