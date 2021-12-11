#pragma once

#include "story.hpp"

class Database
{
public:
    Database() = default;

    void Load( const std::string& dbName );
    void Serialize( const std::string& dbName ) const;

private:
    std::vector<Fandom> fandoms;
    std::vector<Character> characters;
    std::vector<Story> stories;
};