#pragma once

#include "shared/core_defines.hpp"
#include <string>
#include <vector>

enum class StorySource : uint8_t
{
    FF,
    AO3,
    COUNT
};

enum class ContentRating : uint8_t
{
    NONE,
    K,
    K_PLUS,
    T,
    M,
    COUNT
};

enum class Genre : uint8_t
{
    NONE,
    ADVENTURE,
    ANGST,
    CRIME,
    DRAMA,
    FAMILY,
    FANTASY,
    FRIENDSHIP,
    GENERAL,
    HORROR,
    HUMOR,
    HURT_COMFORT,
    MYSTERY,
    PARODY,
    POETRY,
    ROMANCE,
    SCIFI,
    SPIRITUAL,
    SUPERNATURAL,
    SUSPENSE,
    TRAGEDY,
    WESTERN,

    COUNT
};

enum class StoryFlags : uint32_t
{
    NONE                 = 0,
    IS_COMPLETE          = 1 << 0,
    IS_ABANDONED         = 1 << 1,
    IS_SLASH_AUTO        = 1 << 2,
    IS_SLASH_MANUAL      = 1 << 3,
    HAVE_READ_ENTIRELY   = 1 << 4,
    HAVE_READ_PARTIALLY  = 1 << 5,
    INTERESTED           = 1 << 6,
    NOT_INTERESTED       = 1 << 7,

    COUNT = 8
};
PG_DEFINE_ENUM_FLAG_OPERATORS( StoryFlags );

struct Fandom
{
    std::string name;
};
using FandomIndex = uint16_t;

enum class Gender : uint8_t
{
    UNKNOWN,
    MALE,
    FEMALE,
    OTHER
};

struct Character
{
    std::string name;
    FandomIndex fandomIndex;
    Gender gender;
};
using CharacterIndex = uint32_t;

struct CharacterInstance
{
    CharacterIndex characterIndex;
    Gender currentGender;
};

struct FreeformTag
{
    std::string name;
};
using FreeformTagIndex = uint32_t;

struct Relationship
{
    enum class Type : uint8_t
    {
        Romantic,
        Platonic
    };
    CharacterIndex character1;
    CharacterIndex character2;
    Type type;
};

struct UpdateInfo
{
    time_t date;
    uint32_t wordCount;
};

class Serializer;

class Story
{
public:
    Story() = default;

    void Serialize( Serializer* s ) const;
    void Deserialize( Serializer* s );

    const char* Title() const;
    const char* Author() const;
    const char* Description() const;
    std::string AuthorLink() const;
    std::string StoryLink() const;
    void Fandoms( std::vector<FandomIndex>& fandomIndices ) const;
    time_t GetLastUpdate() const;
    void Characters( std::vector<CharacterInstance>& characters ) const;
    void Relationships( std::vector<Relationship>& relationships ) const;
    void FreeformTags( std::vector<FreeformTagIndex>& freeformTagIndices ) const;

    bool HasFlag( StoryFlags flag ) const { return (flags & flag) != StoryFlags::NONE; }
    void SetFlag( StoryFlags flag ) { flags |= flag; }
    uint32_t StoryID() const { return storyID; }
    uint32_t WordCount() const { return wordCount; }
    uint32_t ReviewCount() const { return reviewCount; }
    uint32_t FavoriteCount() const { return favoritesCount; }
    uint32_t FollowCount() const { return followCount; }
    uint32_t ChapterCount() const { return chapterCount; }
    time_t PublishDate() const { return publishDate; }

    void Genres( std::vector<Genre>& genres ) const;
    StorySource GetStorySource() const { return storySource; }
    ContentRating GetContentRating() const { return contentRating; }
    uint8_t MyQualityRating() const { return myQualityRating; }
    void SetMyQualityRating( int rating ) { myQualityRating = static_cast<uint8_t>( rating ); }

private:
    uint8_t* data;
    char* chap1Beginning;
    time_t publishDate;

    // uint16_t titleIndex; always 0
    uint16_t authorOffset;
    uint16_t authorLinkOffset;
    uint16_t descriptionOffset;
    uint16_t fandomsOffset;
    uint16_t updatesOffset;
    uint16_t charactersOffset;
    uint16_t relationshipsOffset;
    uint16_t freeFormTagsOffset;

    StoryFlags flags = static_cast<StoryFlags>( 0 );
    uint32_t storyID = 0;
    uint32_t wordCount;
    uint32_t reviewCount;
    uint32_t favoritesCount;
    uint32_t followCount;
    uint16_t chapterCount;

    Genre genres[2] = { Genre::NONE, Genre::NONE };
    StorySource storySource;
    ContentRating contentRating;
    uint8_t myQualityRating; // out of 10
};
