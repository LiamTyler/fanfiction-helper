#pragma once

#include "shared/core_defines.hpp"
#include <string>
#include <memory>
#include <vector>

enum class StorySource : uint8_t
{
    NONE  = 0,
    FF    = 1,
    AO3   = 2,
    COUNT = 3
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

Genre GenreFromString( const std::string& str );
std::string GenreToString( Genre genre );

enum class Gender : uint8_t
{
    UNKNOWN,
    MALE,
    FEMALE,
    OTHER
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

using Fandom = std::string;
using FandomIndex = uint16_t;
constexpr FandomIndex UNKNOWN_OR_INVALID_FANDOM = UINT16_MAX;

using FreeformTag = std::string;
using FreeformTagIndex = uint32_t;


struct Character
{
    std::string name;
    FandomIndex fandomIndex;
    Gender gender;

    bool operator==( const Character& c ) const { return name == c.name && fandomIndex == c.fandomIndex; }
};
using CharacterIndex = uint32_t;

template <>
struct std::hash<Character>
{
    size_t operator()( const Character& c ) const
    {
        return std::hash<std::string>()( c.name );
    }
};

struct CharacterInstance
{
    CharacterIndex characterIndex;
    Gender currentGender;
};


struct Relationship
{
    enum class Type : uint8_t
    {
        Romantic,
        Platonic
    };
    CharacterInstance character1;
    CharacterInstance character2;
    Type type;
};

struct UpdateInfo
{
    time_t date;
    uint32_t wordCount;

    bool operator<( const UpdateInfo& u ) const { return date > u.date; }
};

class Serializer;

class Story
{
    friend class Database;
public:
    Story() = default;

    void Serialize( Serializer* s ) const;
    void Deserialize( Serializer* s );

    const char* Title() const;
    const char* Author() const;
    const char* Description() const;
    const char* AuthorLink() const;
    std::string AuthorLinkFull() const;
    std::string StoryLink() const;
    std::vector<FandomIndex> Fandoms() const;
    std::vector<CharacterInstance> Characters() const;
    std::vector<Relationship> Relationships() const;
    std::vector<FreeformTagIndex> FreeformTags() const;
    time_t GetLastUpdate() const;
    uint8_t FandomCount() const;
    uint16_t UpdateCount() const;
    uint8_t CharacterCount() const;
    uint8_t RelationshipCount() const;
    uint8_t FreeformTagCount() const;

    void SetFlag( StoryFlags flag ) { flags |= flag; }
    void RemoveFlag( StoryFlags flag ) { flags = flags & ~flag; }
    uint32_t StoryID() const { return storyID; }
    uint32_t WordCount() const { return wordCount; }
    uint32_t ReviewCount() const { return reviewCount; }
    uint32_t FavoriteCount() const { return favoritesCount; }
    uint32_t FollowCount() const { return followCount; }
    uint32_t ChapterCount() const { return chapterCount; }
    time_t PublishDate() const { return publishDate; }

    std::vector<Genre> Genres() const;
    StorySource GetStorySource() const { return storySource; }
    ContentRating GetContentRating() const { return contentRating; }
    uint8_t MyQualityRating() const { return myQualityRating; }
    void SetMyQualityRating( int rating ) { myQualityRating = static_cast<uint8_t>( rating ); }

    bool HasFlag( StoryFlags flag ) const { return (flags & flag) != StoryFlags::NONE; }
    bool HasFandom( FandomIndex fandom ) const;
    bool HasGenre( Genre genre ) const;

private:
    std::shared_ptr<uint8_t[]> data;
    std::shared_ptr<char[]> chap1Beginning;
    time_t publishDate;

    // uint16_t titleIndex; always 0
    uint16_t authorOffset;
    uint16_t authorLinkOffset;
    uint16_t descriptionOffset;
    uint16_t fandomsOffset;
    uint16_t charactersOffset;
    uint16_t relationshipsOffset;
    uint16_t freeFormTagsOffset;
    uint16_t updatesOffset;

    StoryFlags flags;
    uint32_t storyID;
    uint32_t wordCount;
    uint32_t reviewCount;
    uint32_t favoritesCount;
    uint32_t followCount;
    uint16_t chapterCount;

    Genre genres[2];
    StorySource storySource;
    ContentRating contentRating;
    uint8_t myQualityRating; // out of 10
};
using StoryIndex = uint32_t;

size_t StoryHash( StorySource source, uint32_t storyID );


struct ParsedCharacter
{
    std::string name;
    Gender genderModifier = Gender::UNKNOWN;
};

struct ParsedRelationship
{
    ParsedCharacter character1;
    ParsedCharacter character2;
    Relationship::Type type;
};

struct ParsedStory
{
    std::string title;
    std::string author;
    std::string authorLink;
    std::string description;
    std::vector<std::string> fandoms;
    std::vector<ParsedCharacter> characters;
    std::vector<ParsedRelationship> relationships;
    std::vector<std::string> freeformTags;
    std::vector<UpdateInfo> updateInfos;

    time_t publishDate;
    std::string chap1Beginning;
    StoryFlags flags;
    uint32_t storyID;
    uint32_t wordCount;
    uint32_t reviewCount;
    uint32_t favoritesCount;
    uint32_t followCount;
    uint16_t chapterCount;

    Genre genres[2];
    StorySource storySource;
    ContentRating contentRating;
};