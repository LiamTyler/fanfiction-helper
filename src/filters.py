from story import *

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

    # Rule 2: Check description for telling keywords without "no" or "not" in front of them
    desc = story.description.lower()
    keywords = ["slash", "yaoi", "mpreg", "m-preg", "m/m"]
    for keyword in keywords:
        pos = desc.find( keyword )
        if pos != -1:
            begin = max(0, pos-8)
            # Could be "not slash", "no m/m slash", "femmeslash", etc
            if "no" not in desc[begin:pos] and "fem" not in desc[begin:pos]:
                #print(desc, "|", pos, keyword)
                return 2

    # Rules 3: if the genre == romance, every character is male, and numCharacters > 1, probably slash?
    numMales = 0
    for char in story.characters:
        numMales += char.currentGender == 'M'
    if "Romance" in story.genres and numMales > 1 and numMales == len(story.characters):
        return 3

    return 0
