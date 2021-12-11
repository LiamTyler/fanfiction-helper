import pickle
from story import Story, Character

class StoryDB:
    def __init__( self, stories = [] ):
        self.stories = stories
        self.storyIdToIndexMap = {}
        for i in range( len( stories ) ):
            self.storyIdToIndexMap[stories[i]] = i

    def Exists( self, story ):
        return story in self.storyIdToIndexMap
    
    def SearchTitle( self, title ):
        return [ s for s in self.stories if s.title == title ]

    def Insert( self, story ):
        if story in self.storyIdToIndexMap:
            return
        self.stories.append( story )
        self.storyIdToIndexMap[story] = len( self.stories ) - 1

    def GetIndex( self, story ):
        return self.storyIdToIndexMap[story]

    def Serialize( self, filename ):
        with open( filename, "wb" ) as file:
            pickle.dump( self.stories, file )
            pickle.dump( self.storyIdToIndexMap, file )
    
    def Deserialize( self, filename ):
        with open( filename, "rb" ) as file:
            self.stories = pickle.load( file )
            self.storyIdToIndexMap = pickle.load( file )

def LoadStoryDB( filename ):
    db = StoryDB()
    db.Deserialize( filename )
    return db

def LoadFandomInfo( filename ):
    ret = dict()
    try:
        f = open( filename, "r", encoding="utf8" )
    except:
        print( "Could not open file '" + filename + "'" )
        return ret
    lines = [ line.strip() for line in f.readlines() if line[0] != '#' ]
    ret["regularLink"] = lines[0]
    ret["slashExclusionKeywords"] = [ x.lower() for x in lines[2].split(',') if x != '' ]

    genders = dict()
    for line in lines[4:]:
        endOfName = line.find( "\"", 1 )
        name = line[1:endOfName]
        gender = line[-1]
        genders[name] = gender

    ret["characterGenders"] = genders

    return ret