#pragma once

#include "platform_defines.hpp"
#include <cstdio>
#include <cstdlib>


#define _PG_ASSERT_NO_MSG( x )                                                           \
if ( !( x ) )                                                                            \
{                                                                                        \
    printf( "Failed assertion: (%s) at line %d in file %s.\n", #x, __LINE__, __FILE__ ); \
    fflush( stdout );                                                                    \
    abort();                                                                             \
}

#define _PG_ASSERT_WITH_MSG( x, msg )                                                                                   \
if ( !( x ) )                                                                                                           \
{                                                                                                                       \
    printf( "Failed assertion: (%s) at line %d in file %s: %s\n", #x, __LINE__, __FILE__, std::string( msg ).c_str() ); \
    fflush( stdout );                                                                                                   \
    abort();                                                                                                            \
}

#define _PG_GET_ASSERT_MACRO( _1, _2, NAME, ... ) NAME

#include <string>

#if !USING( WINDOWS_PROGRAM )
#define PG_ASSERT( ... ) _PG_GET_ASSERT_MACRO( __VA_ARGS__, _PG_ASSERT_WITH_MSG, _PG_ASSERT_NO_MSG )( __VA_ARGS__ )
#else // #if !USING( WINDOWS_PROGRAM )
#define _PG_EXPAND( x ) x
#define PG_ASSERT( ... ) _PG_EXPAND( _PG_GET_ASSERT_MACRO( __VA_ARGS__, _PG_ASSERT_WITH_MSG, _PG_ASSERT_NO_MSG )( __VA_ARGS__ ) )
#endif // #else // #if !USING( WINDOWS_PROGRAM )