#pragma once

#include <functional>

namespace server
{

using ClientHandlerFunc = std::function<void( char*, int )>;
bool Init( ClientHandlerFunc clientHandler );
void Shutdown();

} // namespace server