#pragma once

#include "story.hpp"
#include <map>
#include <unordered_map>

class Database
{
public:
    Database();

    void Load( const std::string& dbName );
    void Serialize( const std::string& dbName ) const;

    StoryIndex AddOrUpdateStory( const ParsedStory& pStory, bool& updated, bool& needsChap1 );
    FandomIndex AddOrGetFandom( const Fandom& fandom );
    FreeformTagIndex AddOrGetFreeformTag( const FreeformTag& fandom );
    CharacterIndex AddOrGetCharacter( const Character& character );

    const Fandom& GetFandom( FandomIndex index ) const                 { return fandoms[index]; }
    const FreeformTag& GetFreeformTag( FreeformTagIndex index ) const  { return freeformTags[index]; }
    const Character& GetCharacter( CharacterIndex index ) const        { return characters[index]; }
    const Story& GetStory( StoryIndex index ) const                    { return stories[index]; }

private:
    CharacterInstance GetCharacterFromParsedData( const ParsedCharacter& c, FandomIndex* fandoms, const ParsedStory& pStory );
    Story StoryFromParsedData( const ParsedStory& pStory );

    std::vector<Fandom> fandoms;
    std::unordered_map<Fandom, FandomIndex> fandomToIndexMap;

    std::vector<FreeformTag> freeformTags;
    std::unordered_map<FreeformTag, FreeformTagIndex> freeformTagToIndexMap;

    std::vector<Character> characters;
    std::unordered_map<Character, CharacterIndex> characterToIndexMap;
    std::multimap<std::string, CharacterIndex> characterNameToIndicesMap;

    std::vector<Story> stories;
    std::unordered_map<size_t, StoryIndex> storyHashToIndexMap;
};