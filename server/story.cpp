#include "story.hpp"
#include "shared/serializer.hpp"


void Story::Serialize( Serializer* s ) const
{
    uint16_t* udata16 = reinterpret_cast<uint16_t*>( data );
    uint32_t dataLen = fandomsOffset;
    dataLen += 1 + sizeof( FandomIndex ) * data[fandomsOffset];
    dataLen += 2 + sizeof( UpdateInfo ) * udata16[updatesOffset];
    dataLen += 1 + sizeof( CharacterInstance ) * data[charactersOffset];
    dataLen += 1 + sizeof( Relationship ) * data[relationshipsOffset];
    dataLen += 1 + sizeof( FreeformTagIndex ) * data[freeFormTagsOffset];
    s->Write( dataLen );
    s->Write( data, dataLen );

    uint32_t chap1Len = chap1Beginning ? (uint32_t)strlen( chap1Beginning ) : 0;
    s->Write( chap1Len );
    if ( chap1Beginning )
    {
        s->Write( chap1Beginning, chap1Len );
    }

    s->Write( authorOffset );
    s->Write( authorLinkOffset );
    s->Write( descriptionOffset );
    s->Write( fandomsOffset );
    s->Write( updatesOffset );
    s->Write( charactersOffset );
    s->Write( relationshipsOffset );
    s->Write( freeFormTagsOffset );
    
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
    data = static_cast<uint8_t*>( malloc( dataLen ) );
    s->Read( data, dataLen );

    uint32_t chap1Len;
    s->Read( chap1Len );
    if ( chap1Len )
    {
        chap1Beginning = static_cast<char*>( malloc( chap1Len + 1 ) );
        s->Read( chap1Beginning, chap1Len );
        chap1Beginning[chap1Len] = '\0';
    }

    s->Read( authorOffset );
    s->Read( authorLinkOffset );
    s->Read( descriptionOffset );
    s->Read( fandomsOffset );
    s->Read( updatesOffset );
    s->Read( charactersOffset );
    s->Read( relationshipsOffset );
    s->Read( freeFormTagsOffset );

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


const char* Story::Title() const { return (char*)data; }
const char* Story::Author() const { return data ? (char*)data + authorOffset : nullptr; }
const char* Story::Description() const { return data ? (char*)data + descriptionOffset : nullptr; }


std::string Story::AuthorLink() const
{
    if ( !data )
        return "";
    std::string authorLink = std::string( (char*)data + authorLinkOffset );
    if ( storySource == StorySource::FF ) return "https://www.fanfiction.net/u/" + authorLink;
    else return "https://archiveofourown.org/users/" + authorLink;
}


std::string Story::StoryLink() const
{
    if ( storySource == StorySource::FF ) return "https://www.fanfiction.net/s/" + std::to_string( storyID );
    else return "https://archiveofourown.org/works/" + std::to_string( storyID );
}


void Story::Fandoms( std::vector<FandomIndex>& fandomIndices ) const
{
    uint8_t count = data[fandomsOffset];
    fandomIndices.resize( count );
    FandomIndex* fandoms = reinterpret_cast<FandomIndex*>( data + fandomsOffset + 1 );
    for ( uint8_t i = 0; i < count; ++i )
    {
        fandomIndices[i] = fandoms[i];
    }
}


time_t Story::GetLastUpdate() const
{
    return reinterpret_cast<UpdateInfo*>( data + updatesOffset + 2 )->date;
}


void Story::Characters( std::vector<CharacterInstance>& characterIndices ) const
{
    uint8_t count = data[charactersOffset];
    characterIndices.resize( count );
    CharacterInstance* characters = reinterpret_cast<CharacterInstance*>( data + charactersOffset + 1 );
    for ( uint8_t i = 0; i < count; ++i )
    {
        characterIndices[i] = characters[i];
    }
}


void Story::Relationships( std::vector<Relationship>& relationships ) const
{
    uint8_t count = data[relationshipsOffset];
    relationships.resize( count );
    Relationship* rel = reinterpret_cast<Relationship*>( data + relationshipsOffset + 1 );
    for ( uint8_t i = 0; i < count; ++i )
    {
        relationships[i] = rel[i];
    }
}


void Story::FreeformTags( std::vector<FreeformTagIndex>& freeformTagIndices ) const
{
    uint8_t count = data[freeFormTagsOffset];
    freeformTagIndices.resize( count );
    FreeformTagIndex* tags = reinterpret_cast<FreeformTagIndex*>( data + freeFormTagsOffset + 1 );
    for ( uint8_t i = 0; i < count; ++i )
    {
        freeformTagIndices[i] = tags[i];
    }
}


void Story::Genres( std::vector<Genre>& outGenres ) const
{
    outGenres.clear();
    for ( int i = 0; i < ARRAY_COUNT( genres ); ++i )
    {
        outGenres.push_back( genres[i] );
    }
}