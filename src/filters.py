from story import *
import re
import string

def GetPrefixInCurrentSentence( string, pos, maxLen=25 ):
    begin = pos
    while begin >= max( 0, pos - maxLen ):
        if string[begin] == '.':
            break
        # Catch end of normal sentence "! ", but not exclamation tags like "girl!Harry"
        if string[begin] == '!' and string[begin+1]==' ':
            break
        begin -= 1
    begin += 1

    return string[begin:pos]

def NearbySafeWord( desc, pos ):
    # Look up to 25 characters back in the current sentence for a safe word
    begin = pos
    while begin >= max( 0, pos - 25 ) and desc[begin] not in ".!":
        begin -= 1
    begin += 1
    prefixSafeWords = [ "no", "not", "free", "never", "fem", "implied" ]
    window = desc[begin:pos]
    splitWords = re.split( "\s+|\.|,|\?|\(|\)|\/|:", window )
    for safe in prefixSafeWords:
        if safe in splitWords:
            return True

    # sometimes there are "slash free", but want to avoid catching something like "contains Slash. Not cannon"
    postfixSafeWords = [ "free" ]
    window = desc[pos:pos+10]
    for safeWord in postfixSafeWords:
        if safeWord in window:
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
    if NearbySafeWord( desc, pos ) or word in [ "noslash", "nonslash", "slashed", "slashes", "slashing", "femslash" ]:
        return 1
    
    return 2

# returns integer:
# 0 ==> not slash
# > 0 ==> which rule identified it as slash
def IsSlash( story, keywordExclusionList=[] ):
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

    # Rule 4: Check for banned fandom-specific keywords in description. Ex: HP/LV, HPDM, etc
    for keyword in keywordExclusionList:
        if keyword in desc:
            return 4

    # Rule 5: Check first chapter for Slash keyword, like rule 2
    # Look up to the first 1k words, but try to find where the authors note ends and the story starts
    # if possible. Not trying to analyze the story contents, just the beginning info if its there
    # TODO: more delimiters, like <hr>, "---------", etc
    desc = story.first1kWords.lower()
    storyBeginKeywords = [ "chapter one", "chapter 1", "prologue" ]
    for key in storyBeginKeywords:
        pos = desc.find( key )
        if pos != -1:
            desc = desc[:pos]
            break
    val = SlashSpecific( desc )
    if val == 1:
        return 0
    elif val == 2:
        return 5

    # Rules 6: if the genre == romance, every character is male, and numCharacters > 1, probably slash?
    numMales = 0
    for char in story.characters:
        numMales += char.currentGender == 'M'
    if "Romance" in story.genres and numMales > 1 and numMales == len(story.characters):
        return 6

    return 0
