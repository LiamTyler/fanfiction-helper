#include "shared/logger.hpp"
#include "story.hpp"
#include "server.hpp"
#include <iostream>
#include <thread>

int main()
{
    Logger_Init();
    Logger_AddLogLocation( "stdout", stdout );
    Logger_AddLogLocation( "log_serverCPP", "log_serverCPP.txt" );

    server::Init();
    std::string a;
    //std::this_thread::sleep_for( std::chrono::seconds( 5 ) ) ;
    while ( 1 )
    {
        std::cin >> a;
        if ( a.length() )
        {
            break;
        }
    }
    sizeof( Story );
    sizeof( uint8_t* );
    sizeof( std::shared_ptr<uint8_t[]> );
    server::Shutdown();
    return 0;
}