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

def LoadFandomInfo( filename ):
    ret = dict()
    try:
        f = open( filename, "r", encoding="utf8" )
    except:
        print( "Could not open file '" + filename + "'" )
        return ret
    lines = [ line.strip() for line in f.readlines() if len(line) > 0 and line[0] != '#' ]
    ret["fullname"] = lines[0]
    ret["exclusionKeywords"] = [ x.lower() for x in lines[1].split(',') if x != '' ]

    genders = dict()
    for line in lines[2:]:
        endOfName = line.find( "\"", 1 )
        name = line[1:endOfName]
        gender = line[-1]
        genders[name] = gender

    ret["characterGenders"] = genders

    return ret