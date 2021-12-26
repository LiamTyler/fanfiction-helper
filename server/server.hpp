#pragma once

#include <functional>

namespace server
{

using ClientHandlerFunc = std::function<void( size_t, char*, int )>;
bool Init( ClientHandlerFunc clientHandler );
void Shutdown();

} // namespace server