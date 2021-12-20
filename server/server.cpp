#include "server.hpp"
#include "shared/logger.hpp"
#include "story.hpp"
#include <thread>

#if USING ( WINDOWS_PROGRAM )
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment (lib, "Ws2_32.lib")
#else // #if USING ( WINDOWS_PROGRAM )
#error "Need to implement socket code for linux"
#endif // #else // #if USING ( WINDOWS_PROGRAM )

static bool s_serverShouldStop;
constexpr uint32_t MAX_CLIENTS = 40;
static SOCKET s_clientSockets[MAX_CLIENTS];
static std::thread s_clientThreads[MAX_CLIENTS];
static uint32_t s_numClients;
static SOCKET s_listenSocket;
static std::thread s_serverThread;
static bool s_initialized;
static server::ClientHandlerFunc s_clientHandler;

#define PORT "27015"

static void ListenForCommands();

namespace server
{

bool Init( ClientHandlerFunc clientHandler )
{
    s_clientHandler = clientHandler;
    s_initialized = false;
    s_serverShouldStop = false;

    WSADATA wsa;
    int iResult;

    s_listenSocket = INVALID_SOCKET;

    struct addrinfo *result = NULL;
    struct addrinfo hints;
    
	if ( WSAStartup( MAKEWORD( 2, 2 ), &wsa ) != 0 )
	{
        LOG_ERR( "Failed. Error Code : %d", WSAGetLastError() );
		return false;
	}
	
    memset( &hints, 0, sizeof( hints ) );
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags    = AI_PASSIVE;

    iResult = getaddrinfo( NULL, PORT, &hints, &result );
    if ( iResult != 0 )
    {
        LOG_ERR( "getaddrinfo failed with error: %d", iResult );
        WSACleanup();
        return false;
    }

    s_listenSocket = socket( result->ai_family, result->ai_socktype, result->ai_protocol );
    if ( s_listenSocket == INVALID_SOCKET )
    {
        LOG_ERR( "socket failed with error: %ld", WSAGetLastError() );
        freeaddrinfo( result );
        WSACleanup();
        return false;
    }

    iResult = bind( s_listenSocket, result->ai_addr, (int)result->ai_addrlen );
    if ( iResult == SOCKET_ERROR )
    {
        LOG_ERR( "bind failed with error: %d", WSAGetLastError() );
        freeaddrinfo( result );
        closesocket( s_listenSocket );
        WSACleanup();
        return false;
    }

    freeaddrinfo( result );

    iResult = listen( s_listenSocket, 1 );
    if ( iResult == SOCKET_ERROR )
    {
        LOG_ERR( "Listen failed with error: %d", WSAGetLastError() );
        closesocket( s_listenSocket );
        WSACleanup();
        return false;
    }
    for ( uint32_t i = 0; i < MAX_CLIENTS; ++i )
    {
        s_clientSockets[i] = INVALID_SOCKET;
    }
    s_initialized = true;
    s_serverThread = std::thread( ListenForCommands );

    return true;
}


void Shutdown()
{
    if ( s_initialized )
    {
        s_serverShouldStop = true;
        
        for ( uint32_t i = 0; i < MAX_CLIENTS; ++i )
        {
            auto socket = s_clientSockets[i];
            if ( socket != INVALID_SOCKET )
            {
                int result = shutdown( socket, SD_SEND );
                if ( result == SOCKET_ERROR )
                {
                    LOG_ERR( "Failed to shutdown client socket with error: %d", WSAGetLastError() );
                }
                closesocket( socket );
            }
            if ( s_clientThreads[i].joinable() )
            {
                s_clientThreads[i].join();
            }
        }
        closesocket( s_listenSocket );
        s_serverThread.join();
        WSACleanup();
    }
    s_initialized = false;
}

} // namespace server

static bool AddOrUpdateStory( char* data )
{
    ParsedStory pStory;
    pStory.title = std::string( data );
    data += pStory.title.length() + 1;
    pStory.author = std::string( data );
    data += pStory.title.length() + 1;
}


static void HandleClient( uint32_t clientIndex )
{
    SOCKET clientSocket = s_clientSockets[clientIndex];
    constexpr int recvBufferLen = 65536;
    char recvBuffer[recvBufferLen];
    bool clientConnected = true;
    while ( clientConnected && !s_serverShouldStop )
    {
        int bytesReceived = recv( clientSocket, recvBuffer, recvBufferLen, 0 );
        if ( bytesReceived == -1 )
        {
            int err = WSAGetLastError();
            if ( err == WSAETIMEDOUT || errno == WSAEWOULDBLOCK )
            {
                continue;
            }
        }
        else if ( bytesReceived == 0 )
        {
            //LOG( "Client closed connection" );
            clientConnected = false;
        }
        else if ( bytesReceived > 0 )
        {
            s_clientHandler( recvBuffer, bytesReceived );
        }
        else
        {
            LOG_ERR( "Recv return %d bytes received?", bytesReceived );
        }
    }
    closesocket( clientSocket );
    s_clientSockets[clientIndex] = INVALID_SOCKET;
}

static void ListenForCommands() 
{
    while ( !s_serverShouldStop )
    {
        //LOG( "Waiting for client..." );
        SOCKET clientSocket = accept( s_listenSocket, NULL, NULL );
        if ( clientSocket == INVALID_SOCKET )
        {
            if ( !s_serverShouldStop )
            {
                LOG_ERR( "ListenForCommands: accept( s_listenSocket ) failed with error: %d", WSAGetLastError() );
            }
            continue;
        }
        //LOG( "Client connected, waiting for client message" );

        uint32_t i = 0;
        for ( ; i < MAX_CLIENTS; ++i )
        {
            if ( s_clientThreads[i].joinable() )
            {
                s_clientThreads[i].join();
                --s_numClients;
            }
            if ( s_clientSockets[i] == INVALID_SOCKET )
            {
                ++s_numClients;
                s_clientSockets[i] = clientSocket;
                s_clientThreads[i] = std::thread( HandleClient, i );
                break;
            }
        }
        if ( i == MAX_CLIENTS )
        {
            LOG_ERR( "Server is already processing the max of %u clients, none available currently! Skipping connection", MAX_CLIENTS );
        }
    }
}