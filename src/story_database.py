import pickle
from story import Story, Character

class StoryDB:
    def __init__( self, stories = [] ):
        self.stories = stories

    def BinarySearch( self, story ):
        start = 0
        end   = len( self.stories )
        if end == 0:
            return [ False, 0 ]

        #print( "start = ", start, ", end = ", end )
        while start < end:
            #print( "start = ", start, ", end = ", end )
            mid = ( start + end ) // 2
            if self.stories[mid] < story:
                start = mid + 1
            elif self.stories[mid] > story:
                end = mid - 1
            else:
                return [ True, mid ]

        #print( "len = ", len(self.stories), ", start = ", start, ", end = ", end )
        if start >= len( self.stories ) or start > end:
            return [ False, start ]
        if self.stories[start] > story:
            return [ False, start - 1 ]
        else:
            return [ False, start ]
        

    def Exists( self, story ):
        [ present, index ] = self.BinarySearch( story )
        return present
    
    def SearchTitle( self, title ):
        return [ s for s in self.stories if s.title == title ]

    def Insert( self, story ):
        self.stories.append( story )
        #[ present, index ] = self.BinarySearch( story )
        #if present:
        #    return
        #self.stories = self.stories[:index] + [ story ] + self.stories[index:]

    def Serialize( self, filename ):
        with open( filename, "wb" ) as file:
            pickle.dump( self.stories, file )
    
    def Deserialize( self, filename ):
        with open( filename, "rb" ) as file:
            self.stories = pickle.load( file )

def LoadStoryDB( filename ):
    db = StoryDB()
    db.Deserialize( filename )
    return db

# returns dictionary is key = name (string), value = either M, F, or U (unknown) (char)
def LoadCharacterDictionary( filename ):
    db = dict()
    file = open( filename, "r" )
    for line in file:
        endOfName = line.find( "\"", 1 )
        name = line[1:endOfName]
        gender = line[-2]
        db[name] = gender

    return db

def LoadExclusionKeywords( filename ):
    try:
        f = open( filename, "r" )
    except:
        print( "Could not open file '" + filename + "'" )
        return []

    keywords = [ l.strip() for l in f.readlines() ]
    return [ w for w in keywords if w != "" ]