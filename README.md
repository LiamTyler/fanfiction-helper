# Fanfiction Helper

Project to provide better filtering, recommendations, and notifications from fanfiction stories. A C++ server is spawned, which manages a database of stories. It regularly spawns a python script, which scrapes through different fanfiction pages and sends the info for the stories back to the server. The user can then run the python GUI to view the different stories.

Eventually, the server will be able to track which stories you like and dislike, give recommendations, etc

## Building + Running
```
mkdir build
cd build
cmake -G "Visual Studio 16 2019" -Ax64 ..
```

Build and run the c++ server from that cmake project, and then run the python/gui.py while the server is running. Type "exit" in the server's console/command line to shut it down