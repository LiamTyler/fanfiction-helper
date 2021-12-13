#include "database.hpp"
#include "shared/assert.hpp"
#include "shared/filesystem.hpp"
#include "shared/logger.hpp"
#include "shared/serializer.hpp"
#include <algorithm>
#include <functional>
#include <mutex>


Database::Database()
{
}


void Database::Load( const std::string& dbName )
{
    std::string storyDBName        = dbName + "_stories.bin";
    std::string charactersDBName   = dbName + "_characters.txt";
    std::string fandomsDBName      = dbName + "_fandoms.txt";
    std::string freeformtagsDBName = dbName + "_freeformTags.txt";

    std::string backup_storyDBName        = dbName + "_stories_BACKUP.bin";
    std::string backup_charactersDBName   = dbName + "_characters_BACKUP.txt";
    std::string backup_fandomsDBName      = dbName + "_fandoms_BACKUP.txt";
    std::string backup_freeformtagsDBName = dbName + "_freeformTags_BACKUP.txt";
    if ( PathExists( backup_storyDBName ) || PathExists( backup_charactersDBName ) || PathExists( backup_fandomsDBName ) || PathExists( backup_freeformtagsDBName ) )
    {
        LOG_WARN( "BACKUP DB for %s found! Program likely crashed/exited when it was mid-save. Loading backup...", dbName.c_str() );
        CopyFile( storyDBName, backup_storyDBName, true );
        CopyFile( charactersDBName, backup_charactersDBName, true );
        CopyFile( fandomsDBName, backup_fandomsDBName, true );
        CopyFile( freeformtagsDBName, backup_freeformtagsDBName, true );
        DeleteFile( backup_storyDBName );
        DeleteFile( backup_charactersDBName );
        DeleteFile( backup_fandomsDBName );
        DeleteFile( backup_freeformtagsDBName );
    }

    Serializer s;
    s.OpenForRead( storyDBName );
    uint32_t numStories;
    s.Read( numStories );
    stories.resize( numStories );
    for ( uint32_t i = 0; i < numStories; ++i )
    {
        stories[i].Deserialize( &s );
    }

    {
        std::ifstream in( charactersDBName );
        std::string line;
        while ( std::getline( in, line ) )
        {
            Character c;
            size_t pos = line.find( ',' );
            c.name = line.substr( 0, pos );

            char gender = line[pos + 1];
            if ( gender == 'M' ) c.gender = Gender::MALE;
            else if ( gender == 'F' ) c.gender = Gender::FEMALE;
            else if ( gender == 'O' ) c.gender = Gender::OTHER;
            else c.gender = Gender::UNKNOWN;

            line = line.substr( pos + 3 );
            c.fandomIndex = static_cast<FandomIndex>( std::stoul( line ) );

            CharacterIndex index = static_cast<CharacterIndex>( characters.size() );
            characters.push_back( c );
            characterToIndexMap[c] = index;
            characterNameToIndicesMap.insert( { c.name, index } );
        }
    }

    {
        std::ifstream in( fandomsDBName );
        std::string line;
        while ( std::getline( in, line ) )
        {
            fandomToIndexMap[line] = static_cast<FandomIndex>( fandoms.size() );
            fandoms.push_back( line );
        }
    }

    {
        std::ifstream in( freeformtagsDBName );
        std::string line;
        while ( std::getline( in, line ) )
        {
            freeformTagToIndexMap[line] = static_cast<FreeformTagIndex>( freeformTags.size() );
            freeformTags.push_back( line );
        }
    }
}


void Database::Serialize( const std::string& dbName ) const
{
    CopyFile( dbName + "_stories.bin",      dbName + "_stories_BACKUP.bin",      true );
    CopyFile( dbName + "_characters.txt",   dbName + "_characters_BACKUP.txt",   true );
    CopyFile( dbName + "_fandoms.txt",      dbName + "_fandoms_BACKUP.txt",      true );
    CopyFile( dbName + "_freeformTags.txt", dbName + "_freeformTags_BACKUP.txt", true );

    Serializer s;
    s.OpenForWrite( dbName + "_stories.bin" );
    uint32_t numStories = static_cast<uint32_t>( stories.size() );
    s.Write( numStories );
    for ( uint32_t i = 0; i < numStories; ++i )
    {
        stories[i].Serialize( &s );
    }

    {
        char genderStr[] = { 'U', 'M', 'F', 'O' };
        std::ofstream in( dbName + "_characters.txt" );
        for ( const auto& c : characters )
        {
            in << c.name << ',' << genderStr[(uint8_t)c.gender] << ',' << std::to_string( c.fandomIndex ) << "\n";
        }
    }

    {
        std::ofstream in( dbName + "_fandoms.txt" );
        for ( const auto& f : fandoms )
        {
            in << f << "\n";
        }
    }

    {
        std::ofstream in( dbName + "_freeformTags.txt" );
        for ( const auto& f : freeformTags )
        {
            in << f << "\n";
        }
    }

    DeleteFile( dbName + "_stories.bin" );
    DeleteFile( dbName + "_characters.txt" );
    DeleteFile( dbName + "_fandoms.txt" );
    DeleteFile( dbName + "_freeformTags.txt" );
}


static bool FandomListFind( uint8_t numFandoms, FandomIndex* fandoms, FandomIndex lookFor )
{
    for ( uint8_t i = 0; i < numFandoms; ++i )
    {
        if ( fandoms[i] == lookFor ) return true;
    }
    return false;
}


StoryIndex Database::AddOrUpdateStory( const ParsedStory& pStory, bool& updated, bool& needsChap1 )
{   size_t hash = (static_cast<size_t>( pStory.storySource ) << 32) + pStory.storyID;
    uint32_t index = 0;
    auto it = storyHashToIndexMap.find( hash );
    if ( it != storyHashToIndexMap.end() )
    {
        Story& story = stories[it->second];
        Story newStory = StoryFromParsedData( pStory );

        uint16_t data1Len = story.freeFormTagsOffset + story.data[story.freeFormTagsOffset] * sizeof( FreeformTagIndex );
        uint16_t data2Len = newStory.freeFormTagsOffset + newStory.data[newStory.freeFormTagsOffset] * sizeof( FreeformTagIndex );
        if ( data1Len != data2Len || memcmp( story.data.get(), newStory.data.get(), data1Len ) )
        {
            updated = true;
            ParsedStory combinedData = pStory;
            UpdateInfo* updates = reinterpret_cast<UpdateInfo*>( story.data.get() + story.updatesOffset + 2 );
            for ( uint16_t i = 0; i < story.UpdateCount(); ++i )
            {
                combinedData.updateInfos.push_back( updates[i] );
            }
            combinedData.flags = story.flags;

            newStory = StoryFromParsedData( combinedData );
            StoryFlags flags = story.flags;
            std::shared_ptr<char[]> chap1Beginning = story.chap1Beginning ? story.chap1Beginning : newStory.chap1Beginning;
            story = newStory;
            story.flags = flags;
            story.chap1Beginning = chap1Beginning;
            if ( (pStory.flags & StoryFlags::IS_COMPLETE) != StoryFlags::NONE ) story.SetFlag( StoryFlags::IS_COMPLETE );
            else story.RemoveFlag( StoryFlags::IS_COMPLETE );
        }
        else
        {
            updated = false;
            if ( !pStory.chap1Beginning.empty() )
            {
                story.chap1Beginning = std::make_shared<char[]>( pStory.chap1Beginning.length() + 1 );
                strcpy( story.chap1Beginning.get(), pStory.chap1Beginning.c_str() );
            }

            story.wordCount = pStory.wordCount;
            story.reviewCount = pStory.reviewCount;
            story.favoritesCount = pStory.favoritesCount;
            story.followCount = pStory.followCount;
            story.chapterCount = pStory.chapterCount;
            story.genres[0] = pStory.genres[0];
            story.genres[1] = pStory.genres[1];
            story.contentRating = pStory.contentRating;
            if ( (pStory.flags & StoryFlags::IS_COMPLETE) != StoryFlags::NONE ) story.SetFlag( StoryFlags::IS_COMPLETE );
            else story.RemoveFlag( StoryFlags::IS_COMPLETE );
        }
        
        needsChap1 = story.chap1Beginning == nullptr;
        return it->second;
    }
    else
    {
        needsChap1 = updated = true;
        Story newStory = StoryFromParsedData( pStory );
        stories.push_back( newStory );
        return static_cast<StoryIndex>( stories.size() - 1 );
    }    
}


FandomIndex Database::AddOrGetFandom( const Fandom& fandom )
{
    FandomIndex ret;
    auto it = fandomToIndexMap.find( fandom );
    if ( it == fandomToIndexMap.end() )
    {
        ret = static_cast<FandomIndex>( fandoms.size() );
        fandoms.push_back( fandom );
        fandomToIndexMap[fandom] = ret;
    }
    else
    {
        ret = it->second;
    }

    return ret;
}


FreeformTagIndex Database::AddOrGetFreeformTag( const FreeformTag& tag )
{
    FreeformTagIndex ret;
    auto it = freeformTagToIndexMap.find( tag );
    if ( it == freeformTagToIndexMap.end() )
    {
        ret = static_cast<FreeformTagIndex>( freeformTags.size() );
        freeformTags.push_back( tag );
        freeformTagToIndexMap[tag] = ret;
    }
    else
    {
        ret = it->second;
    }

    return ret;
}


CharacterIndex Database::AddOrGetCharacter( const Character& character )
{
    CharacterIndex ret;
    auto it = characterToIndexMap.find( character );
    if ( it == characterToIndexMap.end() )
    {
        ret = static_cast<CharacterIndex>( characters.size() );
        characters.push_back( character );
        characterToIndexMap[character] = ret;
        characterNameToIndicesMap.insert( { character.name, ret } );
    }
    else
    {
        ret = it->second;
    }

    return ret;
}


CharacterInstance Database::GetCharacterFromParsedData( const ParsedCharacter& c, FandomIndex* fandoms, const ParsedStory& pStory )
{
    uint8_t numFandoms = static_cast<uint8_t>( pStory.fandoms.size() );
    FandomIndex fandomIndex = UNKNOWN_OR_INVALID_FANDOM; 
    auto charactersWithThisName = characterNameToIndicesMap.equal_range( c.name );
    size_t characterMatchCount = std::distance( charactersWithThisName.first, charactersWithThisName.second );

    if ( pStory.storySource == StorySource::FF )
    {
        if ( characterMatchCount == 1 )
        {
            fandomIndex = charactersWithThisName.first->second;
        }
        else if ( characterMatchCount > 1 )
        {
            uint8_t numMatches = 0;
            for ( auto it = charactersWithThisName.first; it != charactersWithThisName.second; ++it )
            {
                if ( characters[it->second].fandomIndex != UNKNOWN_OR_INVALID_FANDOM && FandomListFind( numFandoms, fandoms, characters[it->second].fandomIndex ) )
                {
                    fandomIndex = characters[it->second].fandomIndex;
                    ++numMatches;
                }
            }
            if ( numMatches > 2 )
            {
                LOG_ERR( "Character '%s' somehow matched with %u of the fandoms in this FF.net story %s (%u)", c.name.c_str(), numMatches, pStory.title.c_str(), pStory.storyID );
                fandomIndex = UNKNOWN_OR_INVALID_FANDOM;
            }
            else if ( numMatches == 2 )
            {
                fandomIndex = UNKNOWN_OR_INVALID_FANDOM;
                if ( pStory.fandoms.size() == 2 )
                {
                    LOG_WARN( "Character '%s' exists in both fandoms %s and %s. Can't deduce fandom. FF.net story %s (%u)", c.name.c_str(), pStory.fandoms[0].c_str(), pStory.fandoms[1].c_str(), pStory.title.c_str(), pStory.storyID );
                }
                else
                {
                    LOG_ERR( "Character '%s' has 2 matches, but more (%u) fandoms. Shouldn't happen in FF.net? Story %s (%u)", c.name.c_str(), pStory.fandoms.size(), pStory.title.c_str(), pStory.storyID );
                }
            }
        }
    }
    else
    {
        LOG_ERR( "Have not implemented character adding/deduction for anything other than FF.net yet!" );
    }

    Character newC = { c.name, fandomIndex, Gender::UNKNOWN };
    CharacterInstance instance;
    instance.characterIndex = AddOrGetCharacter( newC );
    instance.currentGender = c.genderModifier;
    return instance;
}


Story Database::StoryFromParsedData( const ParsedStory& pStory )
{
    Story newStory;
    size_t dataLen = 0;
    dataLen += pStory.title.length() + 1;
    newStory.authorOffset = static_cast<uint16_t>( dataLen );
    dataLen += pStory.author.length() + 1;
    newStory.authorLinkOffset = static_cast<uint16_t>( dataLen );
    dataLen += pStory.authorLink.length() + 1;
    newStory.descriptionOffset = static_cast<uint16_t>( dataLen );
    dataLen += pStory.description.length() + 1;
    newStory.fandomsOffset = static_cast<uint16_t>( dataLen );
    dataLen += 1 + sizeof( FandomIndex ) * pStory.fandoms.size();
    newStory.updatesOffset = static_cast<uint16_t>( dataLen );
    dataLen += 2 + sizeof( UpdateInfo ) * pStory.updateInfos.size();
    newStory.charactersOffset = static_cast<uint16_t>( dataLen );
    dataLen += 1 + sizeof( CharacterInstance ) * pStory.characters.size();
    newStory.relationshipsOffset = static_cast<uint16_t>( dataLen );
    dataLen += 1 + sizeof( Relationship ) * pStory.relationships.size();
    newStory.freeFormTagsOffset = static_cast<uint16_t>( dataLen );
    dataLen += 1 + sizeof( FreeformTagIndex ) * pStory.freeformTags.size();

    newStory.data = std::make_shared<uint8_t[]>( dataLen );
    char* data = (char*)newStory.data.get();

    strcpy( data, pStory.title.c_str() );
    data += pStory.title.length() + 1;
    strcpy( data, pStory.author.c_str() );
    data += pStory.author.length() + 1;
    strcpy( data, pStory.authorLink.c_str() );
    data += pStory.authorLink.length() + 1;
    strcpy( data, pStory.description.c_str() );
    data += pStory.description.length() + 1;
    strcpy( data, pStory.authorLink.c_str() );
    data += pStory.authorLink.length() + 1;

    uint8_t numFandoms = static_cast<uint8_t>( pStory.fandoms.size() );
    reinterpret_cast<uint8_t*>( data )[0] = numFandoms;
    data += sizeof( uint8_t );
    FandomIndex* fandoms = reinterpret_cast<FandomIndex*>( data );
    for ( const auto& fandom : pStory.fandoms )
    {
        reinterpret_cast<FandomIndex*>( data )[0] = AddOrGetFandom( fandom );
        data += sizeof( FandomIndex );
    }

    reinterpret_cast<uint16_t*>( data )[0] = static_cast<uint16_t>( pStory.updateInfos.size() );
    data += sizeof( uint16_t );
    auto updateDates = pStory.updateInfos;
    std::sort( updateDates.begin(), updateDates.end() );
    for ( const auto& updateInfo : updateDates )
    {
        reinterpret_cast<UpdateInfo*>( data )[0] = updateInfo;
        data += sizeof( UpdateInfo );
    }

    reinterpret_cast<uint8_t*>( data )[0] = static_cast<uint8_t>( pStory.characters.size() );
    data += sizeof( uint8_t );
    for ( const auto& c : pStory.characters )
    {
        reinterpret_cast<CharacterInstance*>( data )[0] = GetCharacterFromParsedData( c, fandoms, pStory );
        data += sizeof( CharacterInstance );
    }

    reinterpret_cast<uint8_t*>( data )[0] = static_cast<uint8_t>( pStory.relationships.size() );
    data += sizeof( uint8_t );
    for ( const auto& r : pStory.relationships )
    {
        Relationship rel;
        rel.character1 = GetCharacterFromParsedData( r.character1, fandoms, pStory );
        rel.character2 = GetCharacterFromParsedData( r.character1, fandoms, pStory );
        rel.type = r.type;
        reinterpret_cast<Relationship*>( data )[0] = rel;
        data += sizeof( Relationship );
    }

    reinterpret_cast<uint8_t*>( data )[0] = static_cast<uint8_t>( pStory.freeformTags.size() );
    data += sizeof( uint8_t );
    for ( const auto& tag : pStory.freeformTags )
    {
        reinterpret_cast<FreeformTagIndex*>( data )[0] = AddOrGetFreeformTag( tag );
        data += sizeof( FreeformTagIndex );
    }

    if ( !pStory.chap1Beginning.empty() )
    {
        newStory.chap1Beginning = std::make_shared<char[]>( pStory.chap1Beginning.length() + 1 );
        strcpy( newStory.chap1Beginning.get(), pStory.chap1Beginning.c_str() );
    }

    newStory.flags = pStory.flags;
    newStory.storyID = pStory.storyID;
    newStory.wordCount = pStory.wordCount;
    newStory.reviewCount = pStory.reviewCount;
    newStory.favoritesCount = pStory.favoritesCount;
    newStory.followCount = pStory.followCount;
    newStory.chapterCount = pStory.chapterCount;
    newStory.publishDate = pStory.publishDate;

    newStory.genres[0] = pStory.genres[0];
    newStory.genres[1] = pStory.genres[1];
    newStory.storySource = pStory.storySource;
    newStory.contentRating = pStory.contentRating;
    newStory.myQualityRating = 0xFF;

    return newStory;
}