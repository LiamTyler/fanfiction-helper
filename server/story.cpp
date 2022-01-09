#include "story.hpp"
#include "shared/serializer.hpp"
#include <unordered_map>


Genre GenreFromString( const std::string& str )
{
    std::unordered_map<std::string, Genre> map =
    {
        { "Adventure", Genre::ADVENTURE },
        { "Angst", Genre::ANGST },
        { "Crime", Genre::CRIME },
        { "Drama", Genre::DRAMA },
        { "Family", Genre::FAMILY },
        { "Fantasy", Genre::FANTASY },
        { "Frienship", Genre::FRIENDSHIP },
        { "General", Genre::GENERAL },
        { "Horror", Genre::HORROR },
        { "Humor", Genre::HUMOR },
        { "Hurt/Comfort", Genre::HURT_COMFORT },
        { "Mystery", Genre::MYSTERY },
        { "Parody", Genre::PARODY },
        { "Poetry", Genre::POETRY },
        { "Romance", Genre::ROMANCE },
        { "Sci-Fi", Genre::SCIFI },
        { "Spiritual", Genre::SPIRITUAL },
        { "Supernatural", Genre::SUPERNATURAL },
        { "Suspense", Genre::SUSPENSE },
        { "Tragedy", Genre::TRAGEDY },
        { "Western", Genre::WESTERN },
    };
    if ( map.find( str ) != map.end() )
    {
        return map[str];
    }
    else
    {
        return Genre::NONE;
    }
}


std::string GenreToString( Genre genre )
{
    std::string strs[] =
    {
         "None",         // NONE
         "Adventure",    // ADVENTURE
         "Angst",        // ANGST
         "Crime",        // CRIME
         "Drama",        // DRAMA
         "Family",       // FAMILY
         "Fantasy",      // FANTASY
         "Friendship",   // FRIENDSHIP
         "General",      // GENERAL
         "Horror",       // HORROR
         "Humor",        // HUMOR
         "Hurt/Comfort", // HURT_COMFORT
         "Mystery",      // MYSTERY
         "Parody",       // PARODY
         "Poetry",       // POETRY
         "Romance",      // ROMANCE
         "Sci-Fi",       // SCIFI
         "Spiritual",    // SPIRITUAL
         "Supernatural", // SUPERNATURAL
         "Suspense",     // SUSPENSE
         "Tragedy",      // TRAGEDY
         "Western",      // WESTERN
    };

    return strs[static_cast<uint8_t>( genre )];
}


void Story::Serialize( Serializer* s ) const
{
    uint16_t* udata16 = reinterpret_cast<uint16_t*>( data.get() );
    uint32_t dataLen = fandomsOffset;
    dataLen += 1 + sizeof( FandomIndex ) * data[fandomsOffset];
    dataLen += 1 + sizeof( CharacterInstance ) * data[charactersOffset];
    dataLen += 1 + sizeof( Relationship ) * data[relationshipsOffset];
    dataLen += 1 + sizeof( FreeformTagIndex ) * data[freeFormTagsOffset];
    dataLen += 2 + sizeof( UpdateInfo ) * reinterpret_cast<uint16_t*>( data.get() + updatesOffset )[0];
    s->Write( dataLen );
    s->Write( data.get(), dataLen );

    uint32_t chap1Len = chap1Beginning ? (uint32_t)strlen( chap1Beginning.get() ) : 0;
    s->Write( chap1Len );
    if ( chap1Beginning )
    {
        s->Write( chap1Beginning.get(), chap1Len );
    }

    s->Write( authorOffset );
    s->Write( authorLinkOffset );
    s->Write( descriptionOffset );
    s->Write( fandomsOffset );
    s->Write( charactersOffset );
    s->Write( relationshipsOffset );
    s->Write( freeFormTagsOffset );
    s->Write( updatesOffset );
    
    s->Write( flags );
    s->Write( storyID );
    s->Write( wordCount );
    s->Write( reviewCount );
    s->Write( favoritesCount );
    s->Write( followCount );
    s->Write( publishDate );
    s->Write( chapterCount );
    s->Write( genres[0] );
    s->Write( genres[1] );
    s->Write( storySource );
    s->Write( contentRating );
    s->Write( myQualityRating );
}


void Story::Deserialize( Serializer* s )
{
    uint32_t dataLen;
    s->Read( dataLen );
    data = std::make_shared<uint8_t[]>( dataLen );
    s->Read( data.get(), dataLen );

    uint32_t chap1Len;
    s->Read( chap1Len );
    if ( chap1Len )
    {
        chap1Beginning = std::make_shared<char[]>( chap1Len + 1 );
        s->Read( chap1Beginning.get(), chap1Len );
        chap1Beginning[chap1Len] = '\0';
    }

    s->Read( authorOffset );
    s->Read( authorLinkOffset );
    s->Read( descriptionOffset );
    s->Read( fandomsOffset );
    s->Read( charactersOffset );
    s->Read( relationshipsOffset );
    s->Read( freeFormTagsOffset );
    s->Read( updatesOffset );

    s->Read( flags );
    s->Read( storyID );
    s->Read( wordCount );
    s->Read( reviewCount );
    s->Read( favoritesCount );
    s->Read( followCount );
    s->Read( publishDate );
    s->Read( chapterCount );
    s->Read( genres[0] );
    s->Read( genres[1] );
    s->Read( storySource );
    s->Read( contentRating );
    s->Read( myQualityRating );
}


const char* Story::Title() const { return (char*)data.get(); }
const char* Story::Author() const { return data ? (char*)data.get() + authorOffset : nullptr; }
const char* Story::Description() const { return data ? (char*)data.get() + descriptionOffset : nullptr; }
const char* Story::AuthorLink() const { return data ? (char*)data.get() + authorLinkOffset : nullptr; }


std::string Story::AuthorLinkFull() const
{
    if ( !data )
        return "";
    std::string authorLink = std::string( (char*)data.get() + authorLinkOffset );
    if ( storySource == StorySource::FF ) return "https://www.fanfiction.net/u/" + authorLink;
    else return "https://archiveofourown.org/users/" + authorLink;
}


std::string Story::StoryLink() const
{
    if ( storySource == StorySource::FF ) return "https://www.fanfiction.net/s/" + std::to_string( storyID );
    else return "https://archiveofourown.org/works/" + std::to_string( storyID );
}


std::vector<FandomIndex> Story::Fandoms() const
{
    uint8_t count = data[fandomsOffset];
    std::vector<FandomIndex> fandomIndices( count );
    FandomIndex* fandoms = reinterpret_cast<FandomIndex*>( data.get() + fandomsOffset + 1 );
    for ( uint8_t i = 0; i < count; ++i )
    {
        fandomIndices[i] = fandoms[i];
    }
    return fandomIndices;
}


std::vector<CharacterInstance> Story::Characters() const
{
    uint8_t count = data[charactersOffset];
    std::vector<CharacterInstance> characterIndices( count );
    CharacterInstance* characters = reinterpret_cast<CharacterInstance*>( data.get() + charactersOffset + 1 );
    for ( uint8_t i = 0; i < count; ++i )
    {
        characterIndices[i] = characters[i];
    }
    return characterIndices;
}


std::vector<Relationship> Story::Relationships() const
{
    uint8_t count = data[relationshipsOffset];
    std::vector<Relationship> relationships( count );
    Relationship* rel = reinterpret_cast<Relationship*>( data.get() + relationshipsOffset + 1 );
    for ( uint8_t i = 0; i < count; ++i )
    {
        relationships[i] = rel[i];
    }
    return relationships;
}


std::vector<FreeformTagIndex> Story::FreeformTags() const
{
    uint8_t count = data[freeFormTagsOffset];
    std::vector<FreeformTagIndex> outTags( count );
    FreeformTagIndex* tags = reinterpret_cast<FreeformTagIndex*>( data.get() + freeFormTagsOffset + 1 );

    for ( uint8_t i = 0; i < count; ++i )
    {
        outTags[i] = tags[i];
    }
    return outTags;
}


time_t Story::GetLastUpdate() const
{
    return reinterpret_cast<UpdateInfo*>( data.get() + updatesOffset + 2 )->date;
}


uint8_t Story::FandomCount() const { return data[fandomsOffset]; }
uint16_t Story::UpdateCount() const { return *(uint16_t*)(data.get() + updatesOffset); }
uint8_t Story::CharacterCount() const { return data[charactersOffset]; }
uint8_t Story::RelationshipCount() const { return data[relationshipsOffset]; }
uint8_t Story::FreeformTagCount() const { return data[freeFormTagsOffset]; }


std::vector<Genre> Story::Genres() const
{
    std::vector<Genre> outGenres;
    for ( int i = 0; i < ARRAY_COUNT( genres ); ++i )
    {
        if ( genres[i] != Genre::NONE )
        {
            outGenres.push_back( genres[i] );
        }
    }
    return outGenres;
}


bool Story::HasFandom( FandomIndex fandom ) const
{
    uint8_t fandomCount = FandomCount();
    FandomIndex* fandoms = reinterpret_cast<FandomIndex*>( data.get() + fandomsOffset + 1 );
    for ( uint8_t i = 0; i < fandomCount; ++i )
    {
        if ( fandoms[i] == fandom ) return true;
    }
    return false;
}


bool Story::HasGenre( Genre genre ) const
{
    if ( genres[0] != Genre::NONE && genres[0] == genre ) return true;
    if ( genres[1] != Genre::NONE && genres[1] == genre ) return true;
    return false;
}


size_t StoryHash( StorySource source, uint32_t storyID )
{
    size_t hash = (static_cast<size_t>( source ) << 32) + storyID;
    return hash;
}