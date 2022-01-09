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
    std::string cmd = "python \"" + std::string( ROOT_DIR ) + "python/scraper.py\"";
    system( cmd.c_str() );
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


void ApplyGenderInfo( const std::string& dbName )
{
    Database db;
    db.Load( dbName );
    auto fandoms = db.GetFandoms();
    for ( FandomIndex fandomIdx = 0; fandomIdx < static_cast<FandomIndex>( fandoms.size() ); ++fandomIdx )
    {
        Fandom fandom = fandoms[fandomIdx];
        std::ifstream in( ROOT_DIR + std::string( "fandom_info/" ) +fandom + ".txt" );
        if ( !in )
        {
            continue;
        }
        LOG( "Applying gender info for fandom '%s'", fandom.c_str() );
        std::string line;
        while ( std::getline( in, line ) )
        {
            auto pos = line.find( '"', 1 );
            std::string name = line.substr( 1, pos - 1 );
            char g = line[pos + 2];
            Gender gender;
            if ( g == 'M' ) gender = Gender::MALE;
            else if ( g == 'F' ) gender = Gender::FEMALE;
            else if ( g == 'O' ) gender = Gender::OTHER;
            else if ( g == 'U' ) gender = Gender::UNKNOWN;
            else
            {
                LOG_WARN( "Gender '%c' not recognized for character '%s'", g, name.c_str() );
                continue;
            }
            db.AddOrUpdateCharacter( name, fandomIdx, gender );
        }
    }
    db.Serialize( dbName );
}


int main()
{
    Logger_Init();
    Logger_AddLogLocation( "stdout", stdout );
    Logger_AddLogLocation( "log_serverCPP", "log_serverCPP.txt" );

    //ApplyGenderInfo( ROOT_DIR "database/database" );
    //return 0;

    G_GetDatabase()->Load( ROOT_DIR "database/database" );
    G_GetDatabase()->StartAutosave();
    extern void HandleClientRequests( size_t inClientSocket, char* data, int bytesReceived );
    if ( !server::Init( HandleClientRequests ) )
    {
        G_GetDatabase()->Shutdown();
        return 0;
    }
    StartPythonScraper();

    std::string cmd;
    while ( true )
    {
        std::cout << "Command: ";
        std::cin >> cmd;
        if ( cmd == "exit" )
        {
            break;
        }
    }

    EndPythonScraper();
    server::Shutdown();
    G_GetDatabase()->Shutdown();
    return 0;
}