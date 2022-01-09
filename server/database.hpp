#pragma once

#include "story.hpp"
#include <map>
#include <mutex>
#include <thread>
#include <unordered_map>

class Database
{
public:
    Database();

    void Shutdown();
    void Load( const std::string& dbName );
    void Serialize( const std::string& dbName );

    StoryIndex AddOrUpdateStory( const ParsedStory& pStory, bool* updated = nullptr, bool* needsChap1 = nullptr );
    void AddOrUpdateCharacter( const std::string& name, FandomIndex fandomIndex, Gender gender );

    const Fandom& GetFandom( FandomIndex index ) const                 { return fandoms[index]; }
    const FreeformTag& GetFreeformTag( FreeformTagIndex index ) const  { return freeformTags[index]; }
    const Character& GetCharacter( CharacterIndex index ) const        { return characters[index]; }
    const Story& GetStory( StoryIndex index ) const                    { return stories[index]; }
    uint32_t NumStories() const                                        { return static_cast<uint32_t>( stories.size() ); }
    void StartAutosave()                                               { m_autosaveThread = std::thread( &Database::Autosave, this ); }
    void StopAutosave()                                                { m_stopAutosave = true; }
    const std::vector<Fandom>& GetFandoms() const                      { return fandoms; }
    FandomIndex GetFandomIndexFromName( const std::string& name ) const;
    std::string EncodeStoryForNetwork( StoryIndex storyIndex ) const;

private:
    FandomIndex AddOrGetFandom( const Fandom& fandom );
    FreeformTagIndex AddOrGetFreeformTag( const FreeformTag& fandom );
    CharacterIndex AddOrGetCharacter( const Character& character );

    CharacterInstance GetCharacterFromParsedData( const ParsedCharacter& c, FandomIndex* fandoms, const ParsedStory& pStory );
    Story StoryFromParsedData( const ParsedStory& pStory );
    void Autosave();

    std::vector<Fandom> fandoms;
    std::unordered_map<Fandom, FandomIndex> fandomToIndexMap;

    std::vector<FreeformTag> freeformTags;
    std::unordered_map<FreeformTag, FreeformTagIndex> freeformTagToIndexMap;

    std::vector<Character> characters;
    std::unordered_map<Character, CharacterIndex> characterToIndexMap;
    std::multimap<std::string, CharacterIndex> characterNameToIndicesMap;

    std::vector<Story> stories;
    std::unordered_map<size_t, StoryIndex> storyHashToIndexMap;

    std::string m_dbName;
    std::mutex m_lock;
    std::thread m_autosaveThread;
    bool m_storiesDirty, m_fandomsDirty, m_tagsDirty, m_charactersDirty;
    bool m_stopAutosave;
};

Database* G_GetDatabase();