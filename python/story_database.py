
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