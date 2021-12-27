from enum import IntEnum

SERVER_CMD_UPDATE_OR_ADD_STORY = 1
SERVER_CMD_REQUEST_FANDOMS = 2
SERVER_CMD_REQUEST_FANDOM_STORIES = 3

def GenreStringFromNum( g ):
    genres = [
        "None",
        "Adventure",
        "Angst",
        "Crime",
        "Drama",
        "Family",
        "Fantasy",
        "Frienship",
        "General",
        "Horror",
        "Humor",
        "Hurt/Comfort",
        "Mystery",
        "Parody",
        "Poetry",
        "Romance",
        "Sci-Fi",
        "Spiritual",
        "Supernatural",
        "Suspense",
        "Tragedy",
        "Western"
    ]
    return genres[g]
    
def ContentRatingStringFromNum( r ):
    ratings = [ "NR", "G", "T", "M", "E" ]
    return ratings[r]

class StoryFlags( IntEnum ):
    NONE = 0,
    IS_COMPLETE = 1,
    IS_ABANDONED = 2,
    IS_SLASH_AUTO = 3,
    IS_SLASH_MANUAL = 4,
    HAVE_READ_ENTIRELY = 5,
    HAVE_READ_PARTIALLY = 6,
    NOT_INTERESTED = 7,
    INTERESTED = 8,
    COUNT = 9

class StorySource( IntEnum ):
    NONE = 0,
    FF = 1,
    AO3 = 2,
    COUNT = 3