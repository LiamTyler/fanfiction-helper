#pragma once

/*
 * With a normal #if, accidentally using wrong symbol will not give error, but just get interpreted as 0.
 * With a normal #ifdef, accidentally using the wrong symbol just skips the inteded path with no error.
 * This will helps catch those instances, since using the wrong symbol will give a divide by zero compile error.
 */
#define IN_USE 9
#define NOT_IN_USE ( -9 )
#define USING( x ) ( 9 / ( x ) == 1 )

#define ARRAY_COUNT( array ) ( static_cast< int >( sizeof( array ) / sizeof( array[0] ) ) )
#define PG_UNUSED( x ) (void) ( x );
#define PG_NO_WARN_UNUSED( x ) (void) ( x );

// requires c++20 for __VA_OPT__
#define _VA_SIZE_HELPER( _1,_2,_3,_4,_5,_6,_7,_8,_9,_10,_11,_12,_13,_14,_15,_16,_17,_18,_19,_20,_21,_22,_23,_24,_25,_26,_27,_28,_29,_30,_31,_32, COUNT, ... ) COUNT
#define VA_SIZE( ... ) _VA_SIZE_HELPER(__VA_ARGS__ __VA_OPT__(,) 32,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0)

#define _PG_CAT( A, B ) A ## B
#define _PG_SELECT( NAME, NUM ) _PG_CAT( NAME, NUM )
#define _PG_VA_SELECT( NAME, ... ) _PG_SELECT( NAME, VA_SIZE(__VA_ARGS__)) (__VA_ARGS__)

// to use: define "WRAPF" and then call PG_WRAP_VARGS. Example:
// #define WRAPF( X ) decltype(X)
// PG_WRAP_VARGS( 1, 'a', "hello" )
// #undef WRAPFs
#define WRAPF( X ) decltype(X)
#define PG_WRAP_VARGS( ... ) _PG_VA_SELECT( _PG_WRAP, __VA_ARGS__ )

// requires /Zc:preprocessor flag in MSVC for standard conforming preprocessor
#define _PG_WRAP0( )
#define _PG_WRAP1( _1 ) WRAPF(_1)
#define _PG_WRAP2( _1,_2 ) WRAPF(_1),WRAPF(_2)
#define _PG_WRAP3( _1,_2,_3 ) WRAPF(_1),WRAPF(_2),WRAPF(_3)
#define _PG_WRAP4( _1,_2,_3,_4 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4)
#define _PG_WRAP5( _1,_2,_3,_4,_5 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5)
#define _PG_WRAP6( _1,_2,_3,_4,_5,_6 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5),WRAPF(_6)
#define _PG_WRAP7( _1,_2,_3,_4,_5,_6,_7 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5),WRAPF(_6),WRAPF(_7)
#define _PG_WRAP8( _1,_2,_3,_4,_5,_6,_7,_8 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5),WRAPF(_6),WRAPF(_7),WRAPF(_8)
#define _PG_WRAP9( _1,_2,_3,_4,_5,_6,_7,_8,_9 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5),WRAPF(_6),WRAPF(_7),WRAPF(_8),WRAPF(_9)
#define _PG_WRAP10( _1,_2,_3,_4,_5,_6,_7,_8,_9,_10 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5),WRAPF(_6),WRAPF(_7),WRAPF(_8),WRAPF(_9),WRAPF(_10)
#define _PG_WRAP11( _1,_2,_3,_4,_5,_6,_7,_8,_9,_10,_11 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5),WRAPF(_6),WRAPF(_7),WRAPF(_8),WRAPF(_9),WRAPF(_10),WRAPF(_11)
#define _PG_WRAP12( _1,_2,_3,_4,_5,_6,_7,_8,_9,_10,_11,_12 ) WRAPF(_1),WRAPF(_2),WRAPF(_3),WRAPF(_4),WRAPF(_5),WRAPF(_6),WRAPF(_7),WRAPF(_8),WRAPF(_9),WRAPF(_10),WRAPF(_11),WRAPF(_12)


#define PG_DEFINE_ENUM_FLAG_OPERATORS( ETYPE ) \
extern "C++" { \
inline constexpr ETYPE operator | ( ETYPE a, ETYPE b ) { return static_cast<ETYPE>( static_cast<std::underlying_type_t<ETYPE>>( a ) | static_cast<std::underlying_type_t<ETYPE>>( b ) ); } \
inline constexpr ETYPE operator & ( ETYPE a, ETYPE b ) { return static_cast<ETYPE>( static_cast<std::underlying_type_t<ETYPE>>( a ) & static_cast<std::underlying_type_t<ETYPE>>( b ) ); } \
inline constexpr ETYPE operator ^ ( ETYPE a, ETYPE b ) { return static_cast<ETYPE>( static_cast<std::underlying_type_t<ETYPE>>( a ) ^ static_cast<std::underlying_type_t<ETYPE>>( b ) ); } \
inline constexpr ETYPE operator ~ ( ETYPE a ) { return static_cast<ETYPE>( ~static_cast<std::underlying_type_t<ETYPE>>( a ) ); } \
inline ETYPE & operator |= ( ETYPE& a, ETYPE b ) { return (ETYPE &)(((std::underlying_type_t<ETYPE> &)a) |= ((std::underlying_type_t<ETYPE>)b)); } \
inline ETYPE & operator &= ( ETYPE& a, ETYPE b ) { return (ETYPE &)(((std::underlying_type_t<ETYPE> &)a) &= ((std::underlying_type_t<ETYPE>)b)); } \
inline ETYPE & operator ^= ( ETYPE& a, ETYPE b ) { return (ETYPE &)(((std::underlying_type_t<ETYPE> &)a) ^= ((std::underlying_type_t<ETYPE>)b)); } \
}