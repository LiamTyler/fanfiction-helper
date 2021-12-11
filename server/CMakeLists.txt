cmake_minimum_required(VERSION 3.0)

project(Server)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(helpful_functions)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set_property(GLOBAL PROPERTY PREDEFINED_TARGETS_FOLDER "CMakePredefinedTargets")
set(CMAKE_SKIP_INSTALL_ALL_DEPENDENCY true)

SET_PLATFORM_DEFINES()

set(ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR})
configure_file(${ROOT_DIR}/cmake/platform_defines.hpp.in ${ROOT_DIR}/shared/platform_defines.hpp)

find_package(OpenMP REQUIRED)

set(SRC
    database.cpp
    database.hpp
    server.cpp
    server.hpp
    story.cpp
    story.hpp
    
    shared/assert.hpp
    shared/core_defines.hpp
    shared/filesystem.cpp
    shared/filesystem.hpp
    shared/logger.cpp
    shared/logger.hpp
    shared/platform_defines.hpp
    shared/serializer.cpp
    shared/serializer.hpp
    
    memory_map/MemoryMapped.cpp
    memory_map/MemoryMapped.h
    
    main.cpp
)

add_executable(${PROJECT_NAME} ${SRC})
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
SET_TARGET_COMPILE_OPTIONS_DEFAULT(${PROJECT_NAME})