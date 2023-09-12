# OpenMunge
*An open-source, cross-platform, end-to-end munge toolchain for Star Wars 
Battlefront II (2005) modding.*

## Overview
OpenMunge is intended to be a modern remake of the original modtools that
were released in 2006 for the original Star Wars Battlefront II (SWBF2). In 
particular, its goals are:
- Output munged files that are identical to those munged by the original
  modtools
- Achieve performance gains through multithreading and job batching
- Be 100% compatible with other open-source, community-led modding tools
- Work on Windows, MacOS, and Linux

It is perhaps useful to state a handful of non-goals to clarify the scope of
the project. OpenMunge is **not** intending to:
- Deviate from the established directory structure and file organization system
  for munging and packing files, as it was designed for the original modtools
- Allow previously-incompatible file types to be used in SWBF2 modded content
  (e.g. `.png` images for textures instead of `.tga`)
- Munge and/or pack assets for any other games, including SWBF (2004)

## Installation
1. Ensure Python 3.10 (minimum) is installed
2. Download the `openmunge` source
3. Done!

## Getting Started
There are a few ways to use OpenMunge, mirroring the ways the original modtools
can be invoked.
1. `python openmunge.py`
2. `python run-batch.py`
3. `python run-munger.py`

| OpenMunge        | Classic Modtools Equivalent            |
|------------------|----------------------------------------|
| `openmunge.py`   | `data_ABC/_BUILD/munge.bat`            |
| `run-batch.py`   | `data_ABC/_BUILD/<category>/munge.bat` |
| `run-munger.py`  | `ToolsFL/bin/____Munge.exe`            |

The arguments that can be given to OpenMunge are very similar to those that are
expected by the original batch files and munge executables.

| openmunge.py    | munge.bat   |
|-----------------|-------------|
| `-w/--worlds`   | `/WORLD`    |
| `-s/--sides`    | `/SIDE`     |
| `-c/--common`   | `/COMMON`   |
| `-l/--load`     | `/LOAD`     |
| `-e/--shell`    | `/SHELL`    |
| `-m/--movies`   | `/MOVIES`   |
| `-z/--localize` | `/LOCALIZE` |
| `-S/--sound`    | `/SOUND`    |
| `-p/--platform` | `/PLATFORM` |
| `-L/--language` | `/LANGUAGE` |
| `-a/--all`      | --          |

OpenMunge has several additional options for configuring the tool.

| Argument                | Required | Description                                                                      |
|-------------------------|:--------:|----------------------------------------------------------------------------------|
| `-P/--project-dir`      |    Y     | The location of `data_ABC` (the mod project)                                     |
| `--config-file`         |    N     | A configuration file to use for setting global options without having to use CLI |
| `-ll/--log-level`       |    N     | The minimum level of log message to display                                      |
| `--swbf2-path`          |    N     | The location of the `GameData` directory for your SWBF2 installation             |
| `--max-concurrent-jobs` |    N     | The number of individual munge jobs that can run simultaneously                  |

## Roadmap
As of the writing of this document, development is still in the early stages.
Eventually the aim is to have every munge capability from the original modtools
present and fully functional, but since the process of reverse-engineering the 
munged data files for the game and then forward-engineering a process for
converting raw assets back to the same format is quite time-consuming and
detail-oriented, reaching this level of feature parity will take months or
years of development time.

That being said, here is a very rough set of goals in no particular order:
- [ ] Worlds
  - [x] World (objects, regions, hints, barriers)
  - [x] Paths
  - [x] AI Planning
  - [ ] Sky
  - [ ] Terrain
- [ ] Common
  - [ ] Effects
  - [ ] Models
  - [ ] Textures
  - [x] ODFs
  - [ ] Animations
  - [ ] Sounds
  - [ ] Scripts
  - [ ] Fonts
  - [ ] Shaders
  - [ ] Localize
  - [ ] Shell
  - [ ] Movies
- [ ] Level Packing
- [ ] GUI (maybe)