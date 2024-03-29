#include "filesystem.hpp"
#include "logger.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs = std::filesystem;


std::string BackToForwardSlashes( std::string str )
{
    for ( size_t i = 0; i < str.length(); ++i )
    {
        if ( str[i] == '\\' )
        {
            str[i] = '/';
        }
    }

    return str;
}


void CreateDirectory( const std::string& dir )
{
    fs::create_directories( dir );
}


void CreateEmptyFile( const std::string& path )
{
    std::ofstream out( path );
    out.close();
}


bool CopyFile( const std::string& from, const std::string& to, bool overwriteExisting )
{
    // For some reason, the overwrite_existing option doesnt work on my desktop
    //fs::copy_options options;
    //if ( overwriteExisting )
    //{
    //    options = fs::copy_options::overwrite_existing;
    //}
    //try
    //{
    //    fs::copy( from, to, fs::copy_options::overwrite_existing );
    //}
    //catch ( fs::filesystem_error &e )
    //{
    //    std::cout << "ERROR '" << e.what() << "'" << std::endl;
    //    std::cout << "Equivalent? '" << fs::equivalent( from, to ) << std::endl;
    //}
    if ( !overwriteExisting && PathExists( to ) )
    {
        return true;
    }

    FILE* infile = fopen( from.c_str(), "rb" );
    if ( infile == NULL )
    {
        return false;
    }
 
    fseek( infile, 0L, SEEK_END );
    long numBytes = ftell( infile );
    fseek( infile, 0L, SEEK_SET );
    char* buffer = (char*)malloc( numBytes );
    size_t numRead = fread( buffer, numBytes, 1, infile );
    if ( numRead != 1 )
    {
        return false;
    }
    fclose( infile );

    FILE* outFile = fopen( to.c_str(), "wb" );
    if ( outFile == NULL )
    {
        return false;
    }
    size_t numWritten = fwrite( buffer, numBytes, 1, outFile );
    if ( numWritten != 1 )
    {
        return false;
    }
    fclose( outFile );

    return true;
}


void DeleteFile( const std::string& filename )
{
    try
    {
        fs::remove( filename );
    }
    catch ( std::filesystem::filesystem_error& e )
    {
        PG_NO_WARN_UNUSED( e );
        LOG_ERR( "Failed to delete file. Error: '%s' and code '%d'", e.what(), e.code().value() );
    }
}


void DeleteRecursive( const std::string& path )
{
    fs::remove_all( path );
}


bool PathExists( const std::string& path )
{
    return fs::exists( path );
}


bool IsDirectory( const std::string& path )
{
    return fs::is_directory( path );
}


bool IsFile( const std::string& path )
{
    return fs::is_regular_file( path );
}


bool DirExists( const std::string& dir )
{
    return fs::is_directory( dir );
}


std::string GetCWD()
{
    return BackToForwardSlashes( fs::current_path().string() );
}


std::string GetAbsolutePath( const std::string& path )
{
    return BackToForwardSlashes( fs::absolute( path ).string() );
}


std::string GetFileExtension( const std::string& filename )
{
    std::string ext = fs::path( filename ).extension().string();
    for ( size_t i = 0; i < ext.length(); ++i )
    {
        ext[i] = std::tolower( ext[i] );
    }

    return ext;
}


std::string GetFilenameMinusExtension( const std::string& filename )
{
    return GetParentPath( filename ) + GetFilenameStem( filename );
}


std::string GetFilenameStem( const std::string& filename )
{
    return fs::path( filename ).stem().string();
}


std::string GetRelativeFilename( const std::string& filename )
{
    return fs::path( filename ).filename().string();
}


std::string GetParentPath( std::string path )
{
    if ( path.empty() )
    {
        return "";
    }
    
    path[path.length() - 1] = ' ';
    std::string parent = fs::path( path ).parent_path().string();
    if ( parent.length() )
    {
        parent += '/';
    }
    parent = BackToForwardSlashes( parent );

    return parent;
}


std::string GetRelativePathToDir( const std::string& file, const std::string& parentPath )
{
    return BackToForwardSlashes( fs::relative( file, parentPath ).string() );
}


std::string GetDirectoryStem( const std::string& path )
{
    if ( path.empty() ) return "";
    if ( path[path.length() - 1] == '/' || path[path.length() - 1] == '\\' )
    {
        return GetFilenameStem( path.substr( 0, path.length() - 1 ) );
    }
    else
    {
        return GetFilenameStem( path );
    }
    //std::string ret;
    //auto p = fs::path( path );
    //if ( fs::is_directory( p ) )
    //{
    //    size_t l = path.length();
    //    int end = (int)l - 1;
    //    while ( end > 0 && (path[end] == '/' || path[end] == '\\' ) ) --end;
    //    int start = end - 1;
    //    while ( start >= 0 && (path[start] != '/' && path[start] != '\\' ) ) --start;
    //    start = start < 0 ? 0 : start + 1;
    //    ret = path.substr( start, end - start + 1 );
    //}
}