# VRCCacheRipper
Script that extracts avatars and worlds from vrc cache

Русская документация: [Тык](Rudoc.md)

# DISCLAIMER: this tool is intended only to recover YOUR OWN avatars/worlds that you have lost source files from, but still have in your cache. The author is not responsible for stealing other people's avatars/worlds

# Usage
Just run ripper.bat

It is recommended to create separate vrchat account(even with visitor rank) for using with ripper
Also you can use without vrchat account if disable naming feature when prompted

# Advanced
Cmdline args and their description for ripper.bat:
- `-s [SIZE] ` maximum size of vrchat avatar in MB
- `-i [path to vrchat cache] ` path to vrchat cache, in case when auto detection does not work (Cache-Windows Player directory)
- `-mins [SIZE] ` minimum size of avatar in MB
- `-asr [path to AssetRipper.exe] ` path to AssetRipper.exe when installed into different directory
- `-j` number of unpacking threads
- and of course `-h` prints help
