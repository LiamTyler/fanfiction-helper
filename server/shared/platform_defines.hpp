#pragma once

/*
 * This is an AUTO GENERATED file from cmake/platform_defines.hpp.in. This will be overwritten whenever
 * cmake is run again, careful when editing.
 */

#include "core_defines.hpp"

#define ROOT_DIR "C:/Users/Liam Tyler/Documents/fanfiction-manager/"

#define LINUX_PROGRAM   NOT_IN_USE
#define WINDOWS_PROGRAM IN_USE
#define APPLE_PROGRAM   NOT_IN_USE


#ifdef CMAKE_DEFINE_DEBUG_BUILD
#define DEBUG_BUILD IN_USE
#else
#define DEBUG_BUILD NOT_IN_USE
#endif

#ifdef CMAKE_DEFINE_RELEASE_BUILD
#define RELEASE_BUILD IN_USE
#else
#define RELEASE_BUILD NOT_IN_USE
#endif
