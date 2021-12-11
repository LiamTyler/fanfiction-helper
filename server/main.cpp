#include "shared/logger.hpp"
#include "story.hpp"
#include "server.hpp"
#include <iostream>

int main()
{
    Logger_Init();
    Logger_AddLogLocation( "stdout", stdout );

    server::Init();
    std::string a;
    while ( 1 )
    {
        std::cin >> a;
        if ( a.length() )
        {
            break;
        }
    }
    server::Shutdown();
    return 0;
}