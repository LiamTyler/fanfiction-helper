from story import *
import re
import string

def NegativeInNeighborhood( desc, pos, width=25 ):
    begin = max( 0, pos - width )
    end = pos + 10
    safeWords = [ "no", "not", "free", "never", "fem" ]
    #words = re.split( "\.|,| |\n|!", desc[begin:end] )
    words = desc[begin:end]
    for safe in safeWords:
        if safe in words:
            return True

    return False

# returns 0 if no slash at all
# returns 1 if slash, but safe word
# returns 2 if slash and no safe word
def SlashSpecific( desc ):
    pos = desc.find( "slash" )
    if pos == -1:
        return 0

    delim = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
    begin = pos
    while begin >= 0 and not desc[begin] in delim:
        begin -= 1
    begin += 1

    l = len(desc)
    end = pos
    while end < l and not desc[end] in delim:
        end += 1
    
    word = desc[begin:end]
    if NegativeInNeighborhood( desc, pos ) or word in [ "slashed", "slashing" ]:
        return 1
    
    return 2

# returns integer:
# 0 ==> not slash
# > 0 ==> which rule identified it as slash
def IsSlash( story ):
    # Rule 1: Check for explicit male pairings
    for pair in story.pairings:
        numMales = 0
        for characterIndex in pair:
            numMales += story.characters[characterIndex].currentGender == 'M'

        if numMales > 1:
            return 1

    desc = story.description.lower() 
    # Rule 2: Check for slash, but not "no slash", "slashed", "slashes", etc
    val = SlashSpecific( desc )
    if val == 1:
        return 0
    elif val == 2:
        return 2

    # Rule 3: Check description for telling keywords without "no" or "not" in front of them
    keywords = [ "yaoi", "mpreg", "m-preg", "m/m"]
    for keyword in keywords:
        pos = desc.find( keyword )
        if pos != -1:
            begin = max(0, pos-8)
            # Could be "not yaoi", "no m/m", etc
            if "no" not in desc[begin:pos] and "fem" not in desc[begin:pos]:
                return 3

    # Rule 4: Check first 1K words of story for match, like rule 2
    #val = SlashSpecific( desc )
    #if val > 0:
    #    if val == 1:
    #        return 0
    #    else:
    #        return 4

    # Rules 5: if the genre == romance, every character is male, and numCharacters > 1, probably slash?
    numMales = 0
    for char in story.characters:
        numMales += char.currentGender == 'M'
    if "Romance" in story.genres and numMales > 1 and numMales == len(story.characters):
        return 5

    return 0
