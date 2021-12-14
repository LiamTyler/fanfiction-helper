#include "database.hpp"
#include "shared/logger.hpp"
#include "server.hpp"
#include "story.hpp"
#include <iostream>
#include <thread>

int main()
{
    Logger_Init();
    Logger_AddLogLocation( "stdout", stdout );
    Logger_AddLogLocation( "log_serverCPP", "log_serverCPP.txt" );

    G_GetDatabase()->Load( "database" );
    server::Init();

    std::string a;
    while ( a != "exit" )
    {
        std::cin >> a;
    }
    server::Shutdown();
    G_GetDatabase()->Shutdown();
    return 0;
}