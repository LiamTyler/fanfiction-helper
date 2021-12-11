macro(SET_PLATFORM_DEFINES)
	set(LINUX_PROGRAM   "NOT_IN_USE")
	set(WINDOWS_PROGRAM "NOT_IN_USE")
	set(APPLE_PROGRAM   "NOT_IN_USE")
	if(UNIX AND NOT APPLE)
		set(LINUX_PROGRAM   "IN_USE")
	elseif(WIN32)
		set(WINDOWS_PROGRAM "IN_USE")
	elseif(APPLE)
		set(APPLE_PROGRAM   "IN_USE")
	endif()
endmacro()

function( SET_TARGET_COMPILE_OPTIONS_DEFAULT )
    foreach(arg IN LISTS ARGN)
		set_property(TARGET ${arg} PROPERTY CXX_STANDARD 20)
        if(UNIX AND NOT APPLE)
            target_compile_options(${arg} PUBLIC -Wall -Wno-unused-function -Wno-unused-variable -Wno-unused-but-set-variable -Wno-switch -Wno-format)
            target_compile_options(${arg} PUBLIC $<$<CONFIG:DEBUG>: -g>)
            target_compile_options(${arg} PUBLIC $<$<CONFIG:RELEASE>: -O2>)
        elseif(MSVC)
            target_compile_options(${arg} PUBLIC $<$<CONFIG:DEBUG>: /Od /Oi>)
            target_compile_options(${arg} PUBLIC $<$<CONFIG:RELEASE>: /O2 /Zi /Oi /Ot>)
            target_compile_options(${arg} PRIVATE /MD /MP /Zc:preprocessor /wd5105)
            target_link_options(${arg} PUBLIC $<$<CONFIG:RELEASE>: /DEBUG /LTCG>)
            target_compile_definitions(${arg} PRIVATE -D_CRT_SECURE_NO_WARNINGS -D_ITERATOR_DEBUG_LEVEL=0)
        endif()
    endforeach()
endfunction()


function(SET_TARGET_POSTFIX)
    foreach(arg IN LISTS ARGN)
        set_target_properties(
            ${arg}
            PROPERTIES
            DEBUG_POSTFIX _d
            #RELEASE_POSTFIX _release
        )
    endforeach()
endfunction()

function(SET_TARGET_AS_DEFAULT_VS_PROJECT proj)
    set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT ${proj})
endfunction()