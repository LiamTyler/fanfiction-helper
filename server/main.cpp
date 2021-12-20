#include "database.hpp"
#include "shared/filesystem.hpp"
#include "shared/logger.hpp"
#include "server.hpp"
#include "story.hpp"
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
        // TODO: Relationships

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

int main()
{
    Logger_Init();
    Logger_AddLogLocation( "stdout", stdout );
    Logger_AddLogLocation( "log_serverCPP", "log_serverCPP.txt" );

    G_GetDatabase()->Load( "../database/database" );
    server::Init( HandlePythonScraper );
    StartPythonScraper();

    std::string a;
    while ( true )
    {
        std::cin >> a;
        if ( a == "exit" )
        {
            break;
        }
    }

    EndPythonScraper();
    server::Shutdown();
    G_GetDatabase()->Shutdown();
    return 0;
}