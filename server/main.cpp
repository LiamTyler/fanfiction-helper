#include "database.hpp"
#include "shared/filesystem.hpp"
#include "shared/logger.hpp"
#include "server.hpp"
#include "story.hpp"
#include <fstream>
#include <iostream>
#include <thread>

std::thread scraper;

void StartPythonScraper_Internal()
{
    system( "python ../../src/main.py" );
    LOG( "Done with python" );
}

void StartPythonScraper()
{
    if ( PathExists( "shutdown.txt" ) ) DeleteFile( "shutdown.txt" );
    scraper = std::thread( StartPythonScraper_Internal );
}

void EndPythonScraper()
{
    CreateEmptyFile( "shutdown.txt" );
    scraper.join();
    DeleteFile( "shutdown.txt" );
}

enum ServerCmds : uint32_t
{
    INVALID_OR_MISSING  = 0,
    UPDATE_OR_ADD_STORY = 1,

    COUNT
};



template <typename T>
T ParseUNum( char*& str )
{
    size_t n = strtoull( str, &str, 0 );
    ++str;
    return static_cast<T>( n );
}

std::string ParseString( char*& data )
{
    std::string ret( data );
    data += ret.length() + 1;
    return ret;
}


std::vector<std::string> ParseStringVector( char*& data )
{
    std::vector<std::string> v;
    uint32_t length = ParseUNum<uint32_t>( data );
    for ( uint32_t i = 0; i < length; ++i )
    {
        v.emplace_back( ParseString( data ) );
    }
    return v;
}


void HandlePythonScraper( char* data, int bytesReceived )
{
    uint32_t cmd = ParseUNum<uint32_t>( data );
    if ( cmd == INVALID_OR_MISSING )
    {
        LOG_ERR( "Command from client could not be processed, or was missing" );
    }
    //LOG( "Server recieved msg of cmd %u: '%s'", cmd, data );
    if ( cmd == UPDATE_OR_ADD_STORY )
    {
        ParsedStory pStory;
        std::string tmp = data;
        data += tmp.length() + 1;
        if ( tmp == "FF" ) pStory.storySource = StorySource::FF;
        else if ( tmp == "AO3" ) pStory.storySource = StorySource::AO3;
        else pStory.storySource = StorySource::ERROR;

        pStory.title = ParseString( data );
        pStory.author = ParseString( data );
        pStory.authorLink = ParseString( data );
        pStory.description = ParseString( data );
        pStory.fandoms = ParseStringVector( data );
        uint32_t numCharacters = ParseUNum<uint32_t>( data );
        for ( uint32_t i = 0; i < numCharacters; ++i )
        {
            ParsedCharacter c;
            c.name = ParseString( data );
            c.genderModifier = Gender::UNKNOWN;
            pStory.characters.emplace_back( c );
        }

        uint32_t numRelationships = ParseUNum<uint32_t>( data );
        for ( uint32_t i = 0; i < numRelationships; ++i )
        {
            ParsedRelationship r;
            r.character1.name = ParseString( data );
            r.character1.genderModifier = Gender::UNKNOWN;
            r.character2.name = ParseString( data );
            r.character2.genderModifier = Gender::UNKNOWN;
            r.type = ParseUNum<uint32_t>( data ) == 0 ? Relationship::Type::Romantic : Relationship::Type::Platonic;
        }

        pStory.freeformTags = ParseStringVector( data );
        auto updates = ParseStringVector( data );
        pStory.publishDate = std::stoull( updates[0] );

        pStory.storyID = ParseUNum<uint32_t>( data );
        pStory.flags = ParseUNum<StoryFlags>( data );
        pStory.wordCount = ParseUNum<uint32_t>( data );
        pStory.reviewCount = ParseUNum<uint32_t>( data );
        pStory.favoritesCount = ParseUNum<uint32_t>( data );
        pStory.followCount = ParseUNum<uint32_t>( data );
        pStory.chapterCount = ParseUNum<uint16_t>( data );

        auto genres = ParseStringVector( data );
        pStory.genres[0] = genres.size() >= 1 ? GenreFromString( genres[0] ) : Genre::NONE;
        pStory.genres[1] = genres.size() >= 2 ? GenreFromString( genres[1] ) : Genre::NONE;
        std::string contentRating = ParseString( data );
        if ( contentRating == "K" ) pStory.contentRating = ContentRating::K;
        else if ( contentRating == "K+" ) pStory.contentRating = ContentRating::K_PLUS;
        else if ( contentRating == "T" ) pStory.contentRating = ContentRating::T;
        else if ( contentRating == "M" ) pStory.contentRating = ContentRating::M;
        else pStory.contentRating = ContentRating::NONE;

        if ( updates.size() > 1 )
        {
            pStory.updateInfos.push_back( UpdateInfo{ (time_t)std::stoull( updates[1] ), pStory.wordCount } );
        }

        bool updated, needsChap1;
        G_GetDatabase()->AddOrUpdateStory( pStory, &updated, &needsChap1 );
        LOG( "Story %s updated: %u, needs chap1: %u", pStory.title.c_str(), updated, needsChap1 );
    }
    else
    {
        LOG_ERR( "Unknown client cmd %u", cmd );
    }

    //std::string sendMsg = "message recieved";
    //int iSendResult = send( s_clientSocket, sendMsg.c_str(), (int)sendMsg.length() + 1, 0 );
    //if ( iSendResult == SOCKET_ERROR )
    //{
    //    LOG_ERR( "send failed with error: %d", WSAGetLastError() );
    //    clientConnected = false;
    //}
}


float StoryPredictionScore( const Story& story )
{
    float score = 0;
    ContentRating contentRating = story.GetContentRating();
    if ( contentRating == ContentRating::T || contentRating == ContentRating::M ) score += 1;

    bool isComplete = story.HasFlag( StoryFlags::IS_COMPLETE );
    if ( isComplete ) score += 0.5f;

    auto wordCount = story.WordCount();
    if ( wordCount >= 500'000 ) score -= 1;
    else if ( wordCount >= 10'000 ) score += 1;

    if ( story.HasGenre( Genre::ADVENTURE ) ) score += 0.5f;
    if ( story.HasGenre( Genre::ROMANCE ) ) score += 0.5f;
    if ( story.HasGenre( Genre::PARODY ) ) score -= 1;
    if ( story.HasGenre( Genre::HUMOR ) ) score -= 0.5;
    if ( story.HasGenre( Genre::ANGST ) ) score -= 0.25;
    
    return score;
}


void Recommend()
{
    auto db = G_GetDatabase();
    uint32_t numStories = db->NumStories();
    std::vector<std::pair<StoryIndex, float>> storyScores( numStories );
    for ( uint32_t storyIdx = 0; storyIdx < numStories; ++storyIdx )
    {
        storyScores[storyIdx] = { storyIdx, StoryPredictionScore( db->GetStory( storyIdx ) ) };
    }
    std::sort( storyScores.begin(), storyScores.end(), []( const auto& lhs, const auto& rhs ) { return lhs.second > rhs.second; } );
    std::ofstream results( "results.txt" );
    for ( uint32_t storyIdx = 0; storyIdx < numStories; ++storyIdx )
    {
        const char* ratingStr[] = { "None", "K", "K+", "T", "M" };
        const Story& s = db->GetStory( storyScores[storyIdx].first );
        results << storyIdx << ": Rated: " << ratingStr[(int)s.GetContentRating()] << " - ";
        
        auto genres = s.Genres();
        std::string genreStr;
        if ( genres.size() == 1 ) genreStr = GenreToString( genres[0] );
        else if ( genres.size() == 2 ) genreStr = GenreToString( genres[0] ) + "/" + GenreToString( genres[1] );
        results << genreStr << " - ";

        results << "Chapters: " << s.ChapterCount() << " - Words: " << s.WordCount() << " - Reviews: " << s.ReviewCount() << " - Follows: " << s.FollowCount() << " - ";

        std::string charStr;
        auto characters = s.Characters();
        for ( auto c : characters )
        {
            charStr += db->GetCharacter( c.characterIndex ).name + ", ";
        }
        if ( charStr.length() )
        {
            charStr = charStr.substr( 0, charStr.length() - 2 );
        }
        results << charStr;

        if ( s.HasFlag( StoryFlags::IS_COMPLETE ) )
        {
            results << " - Complete";
        }
        results << std::endl;

        results << "\t" << s.Description() << std::endl;
        results << "\t" << s.Title() << ": " << s.StoryLink() << std::endl;
    }
    results.close();
}


int main()
{
    Logger_Init();
    Logger_AddLogLocation( "stdout", stdout );
    Logger_AddLogLocation( "log_serverCPP", "log_serverCPP.txt" );

    G_GetDatabase()->Load( "../database/database" );
    server::Init( HandlePythonScraper );
    //StartPythonScraper();

    std::string cmd;
    while ( true )
    {
        std::cout << "Command: ";
        std::cin >> cmd;
        if ( cmd == "exit" )
        {
            break;
        }
        else if ( cmd == "recommend" )
        {
            Recommend();
        }
    }

    //EndPythonScraper();
    server::Shutdown();
    G_GetDatabase()->Shutdown();
    return 0;
}