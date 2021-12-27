#include "database.hpp"
#include "shared/assert.hpp"
#include "shared/filesystem.hpp"
#include "shared/logger.hpp"
#include "shared/serializer.hpp"
#include <algorithm>
#include <functional>

#define DEBUG_DATABASE NOT_IN_USE
#if USING( DEBUG_DATABASE )
#define DLOG( ... ) LOG( __VA_ARGS__ )
#else
#define DLOG( ... )
#endif // 


Database::Database()
{
    m_storiesDirty = m_fandomsDirty = m_tagsDirty = m_charactersDirty = m_stopAutosave = false;
}


void Database::Shutdown()
{
    m_stopAutosave = true;
    if ( m_autosaveThread.joinable() )
    {
        m_autosaveThread.join();
    }
    else
    {
        Serialize( m_dbName );
    }
}


void Database::Load( const std::string& dbName )
{
    m_storiesDirty = m_fandomsDirty = m_tagsDirty = m_charactersDirty = m_stopAutosave = false;
    m_dbName = dbName;
    std::string storyDBName        = dbName + "_stories.bin";
    std::string charactersDBName   = dbName + "_characters.txt";
    std::string fandomsDBName      = dbName + "_fandoms.txt";
    std::string freeformtagsDBName = dbName + "_freeformTags.txt";

    Serializer s;
    if ( !s.OpenForRead( storyDBName ) )
    {
        LOG_WARN( "No database with name %s found. Continuing with new database...", dbName.c_str() );
        m_autosaveThread = std::thread( &Database::Autosave, this );
        return;
    }

    uint32_t numStories;
    s.Read( numStories );
    stories.resize( numStories );
    for ( uint32_t i = 0; i < numStories; ++i )
    {
        stories[i].Deserialize( &s );
        size_t hash = StoryHash( stories[i].storySource, stories[i].storyID );
        storyHashToIndexMap[hash] = i;
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

    m_autosaveThread = std::thread( &Database::Autosave, this );
}


void Database::Serialize( const std::string& dbName )
{
    m_lock.lock();
    if ( m_charactersDirty || m_fandomsDirty || m_tagsDirty || m_storiesDirty )
    {
        LOG( "Serializing %s", dbName.c_str() );
    }

    if ( m_charactersDirty )
    {
        char genderStr[] = { 'U', 'M', 'F', 'O' };
        std::ofstream in( dbName + "_characters.txt" );
        for ( const auto& c : characters )
        {
            in << c.name << ',' << genderStr[(uint8_t)c.gender] << ',' << std::to_string( c.fandomIndex ) << "\n";
        }
        m_charactersDirty = false;
    }

    if ( m_fandomsDirty )
    {
        std::ofstream in( dbName + "_fandoms.txt" );
        for ( const auto& f : fandoms )
        {
            in << f << "\n";
        }
        m_fandomsDirty = false;
    }

    if ( m_tagsDirty )
    {
        std::ofstream in( dbName + "_freeformTags.txt" );
        for ( const auto& f : freeformTags )
        {
            in << f << "\n";
        }
        m_tagsDirty = false;
    }

    if ( m_storiesDirty )
    {
        Serializer s;
        s.OpenForWrite( dbName + "_stories.bin" );
        uint32_t numStories = static_cast<uint32_t>( stories.size() );
        s.Write( numStories );
        for ( uint32_t i = 0; i < numStories; ++i )
        {
            stories[i].Serialize( &s );
        }
        m_storiesDirty = false;
    }
    m_lock.unlock();
}


static bool FandomListFind( uint8_t numFandoms, FandomIndex* fandoms, FandomIndex lookFor )
{
    for ( uint8_t i = 0; i < numFandoms; ++i )
    {
        if ( fandoms[i] == lookFor ) return true;
    }
    return false;
}


StoryIndex Database::AddOrUpdateStory( const ParsedStory& pStory, bool* outShouldServerKeepUpdating, bool* outNeedsChap1 )
{
    bool shouldServerKeepUpdating = false;
    bool needsChap1 = false;
    bool dirty = false;

    StoryIndex storyIndex = 0;
    size_t hash = StoryHash( pStory.storySource, pStory.storyID );
    auto it = storyHashToIndexMap.find( hash );
    if ( it != storyHashToIndexMap.end() )
    {
        DLOG( "DB: Updating story %s", pStory.title.c_str() );
        Story& story = stories[it->second];
        Story newStory = StoryFromParsedData( pStory );

        uint16_t data1Len = story.freeFormTagsOffset + story.data[story.freeFormTagsOffset] * sizeof( FreeformTagIndex );
        uint16_t data2Len = newStory.freeFormTagsOffset + newStory.data[newStory.freeFormTagsOffset] * sizeof( FreeformTagIndex );
        if ( data1Len != data2Len || memcmp( story.data.get(), newStory.data.get(), data1Len ) )
        {
            shouldServerKeepUpdating = dirty = true;
            ParsedStory combinedData = pStory;
            UpdateInfo* updates = reinterpret_cast<UpdateInfo*>( story.data.get() + story.updatesOffset + 2 );
            uint16_t updateCount = story.UpdateCount();
            for ( uint16_t i = 0; i < updateCount; ++i )
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
            dirty = false;
            if ( !pStory.chap1Beginning.empty() )
            {
                story.chap1Beginning = std::make_shared<char[]>( pStory.chap1Beginning.length() + 1 );
                strcpy( story.chap1Beginning.get(), pStory.chap1Beginning.c_str() );
                dirty = true;
            }
            dirty = dirty || story.wordCount != pStory.wordCount;
            dirty = dirty || story.reviewCount != pStory.reviewCount;
            dirty = dirty || story.favoritesCount != pStory.favoritesCount;
            dirty = dirty || story.followCount != pStory.followCount;
            dirty = dirty || story.chapterCount != pStory.chapterCount;
            dirty = dirty || story.genres[0] != pStory.genres[0];
            dirty = dirty || story.genres[1] != pStory.genres[1];
            dirty = dirty || story.contentRating != pStory.contentRating;
            dirty = dirty || ((story.flags & StoryFlags::IS_COMPLETE) != (pStory.flags & StoryFlags::IS_COMPLETE));

            shouldServerKeepUpdating = story.wordCount != pStory.wordCount || story.chapterCount != pStory.chapterCount;

            if ( dirty )
            {
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
        }
        
        needsChap1 = story.chap1Beginning == nullptr;
        storyIndex = it->second;
    }
    else
    {
        DLOG( "DB: Adding new story %s", pStory.title.c_str() );
        shouldServerKeepUpdating = dirty = needsChap1 =  true;
        Story newStory = StoryFromParsedData( pStory );
        stories.push_back( newStory );
        storyIndex = static_cast<StoryIndex>( stories.size() - 1 );
        storyHashToIndexMap[hash] = storyIndex;
    }
    
    m_storiesDirty = m_storiesDirty || dirty;
    if ( outShouldServerKeepUpdating ) *outShouldServerKeepUpdating = shouldServerKeepUpdating;
    if ( outNeedsChap1 ) *outNeedsChap1 = needsChap1;

    return storyIndex;
}


FandomIndex Database::GetFandomIndexFromName( const std::string& name ) const
{
    auto it = fandomToIndexMap.find( name );
    if ( it == fandomToIndexMap.end() ) return UNKNOWN_OR_INVALID_FANDOM;
    else return it->second;
}


std::string Database::EncodeStoryForNetwork( StoryIndex storyIndex ) const
{
    const Story& s = stories[storyIndex];
    std::string e;
    e.reserve( 8192 );
    e += std::to_string( (uint8_t)s.storySource ) + '\0';
    e += s.Title(); e += '\0';
    e += s.Author(); e += '\0';
    e += s.Description(); e += '\0';

    auto characters = s.Characters();
    e += std::to_string( characters.size() ) + '\0';
    for ( auto c : characters )
    {
        const auto& chr = GetCharacter( c.characterIndex );
        e += chr.name + '\0';
    }

    e += std::to_string( s.storyID ) + '\0';
    e += std::to_string( (uint32_t)s.flags ) + '\0';
    e += std::to_string( s.wordCount ) + '\0';
    e += std::to_string( s.chapterCount ) + '\0';
    e += std::to_string( s.reviewCount ) + '\0';
    e += std::to_string( s.favoritesCount ) + '\0';
    e += std::to_string( s.followCount ) + '\0';
    e += std::to_string( (uint8_t)s.contentRating ) + '\0';

    return e;
}


FandomIndex Database::AddOrGetFandom( const Fandom& fandom )
{
    FandomIndex ret;
    auto it = fandomToIndexMap.find( fandom );
    if ( it == fandomToIndexMap.end() )
    {
        ret = static_cast<FandomIndex>( fandoms.size() );
        DLOG( "DB: Adding new fandom %s to slow %u", fandom.c_str(), ret );
        fandoms.push_back( fandom );
        fandomToIndexMap[fandom] = ret;
        m_fandomsDirty = true;
    }
    else
    {
        DLOG( "DB: Found fandom %s in slot %u", fandom.c_str(), it->second );
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
        m_tagsDirty = true;
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
        DLOG( "DB: Adding new character %s (%u) (%u) to slot %u", character.name.c_str(), character.fandomIndex, character.gender, ret );
        characters.push_back( character );
        characterToIndexMap[character] = ret;
        characterNameToIndicesMap.insert( { character.name, ret } );
        m_charactersDirty = true;
    }
    else
    {
        DLOG( "DB: Found character %s (%u) (%u) in slot %u", character.name.c_str(), character.fandomIndex, character.gender, it->second );
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
        if ( pStory.fandoms.size() == 1 )
        {
            fandomIndex = fandoms[0];
        }
        else if ( characterMatchCount == 1 )
        {
            fandomIndex = characters[charactersWithThisName.first->second].fandomIndex;
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
    PG_ASSERT( dataLen <= UINT16_MAX );

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
    PG_ASSERT( data - (char*)newStory.data.get() == newStory.fandomsOffset );

    uint8_t numFandoms = static_cast<uint8_t>( pStory.fandoms.size() );
    reinterpret_cast<uint8_t*>( data )[0] = numFandoms;
    data += sizeof( uint8_t );
    FandomIndex* fandoms = reinterpret_cast<FandomIndex*>( data );
    for ( const auto& fandom : pStory.fandoms )
    {
        reinterpret_cast<FandomIndex*>( data )[0] = AddOrGetFandom( fandom );
        data += sizeof( FandomIndex );
    }

    PG_ASSERT( data - (char*)newStory.data.get() == newStory.updatesOffset );
    reinterpret_cast<uint16_t*>( data )[0] = static_cast<uint16_t>( pStory.updateInfos.size() );
    data += sizeof( uint16_t );
    auto updateDates = pStory.updateInfos;
    std::sort( updateDates.begin(), updateDates.end() );
    for ( const auto& updateInfo : updateDates )
    {
        reinterpret_cast<UpdateInfo*>( data )[0] = updateInfo;
        data += sizeof( UpdateInfo );
    }

    PG_ASSERT( data - (char*)newStory.data.get() == newStory.charactersOffset );
    reinterpret_cast<uint8_t*>( data )[0] = static_cast<uint8_t>( pStory.characters.size() );
    data += sizeof( uint8_t );
    for ( const auto& c : pStory.characters )
    {
        reinterpret_cast<CharacterInstance*>( data )[0] = GetCharacterFromParsedData( c, fandoms, pStory );
        data += sizeof( CharacterInstance );
    }

    PG_ASSERT( data - (char*)newStory.data.get() == newStory.relationshipsOffset );
    reinterpret_cast<uint8_t*>( data )[0] = static_cast<uint8_t>( pStory.relationships.size() );
    data += sizeof( uint8_t );
    for ( const auto& r : pStory.relationships )
    {
        Relationship rel;
        rel.character1 = GetCharacterFromParsedData( r.character1, fandoms, pStory );
        rel.character2 = GetCharacterFromParsedData( r.character2, fandoms, pStory );
        rel.type = r.type;
        reinterpret_cast<Relationship*>( data )[0] = rel;
        data += sizeof( Relationship );
    }

    PG_ASSERT( data - (char*)newStory.data.get() == newStory.freeFormTagsOffset );
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


void Database::Autosave()
{
    float secondsElapsed;
    while ( !m_stopAutosave )
    {
        secondsElapsed = 0;
        auto begin = std::chrono::steady_clock::now();
        while ( !m_stopAutosave && secondsElapsed < 60 )
        {
            auto end = std::chrono::steady_clock::now();
            std::this_thread::sleep_for( std::chrono::seconds( 1 ) );
            secondsElapsed = (float)std::chrono::duration_cast<std::chrono::seconds>( end - begin ).count();
        }
        Serialize( m_dbName );
    }
}


static Database s_database;
Database* G_GetDatabase()
{
    return &s_database;
}