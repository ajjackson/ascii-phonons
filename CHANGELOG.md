# Change Log

Notable changes are logged here by release. This project follows Semantic Versioning:

- Version numbers take the format X.Y.Z
- X is associated with major API breakage / changes in algorithm and results.
- Y is associated with minor updates and improvements
- Small amounts of code tidying, refactoring and documentation lead to .Z releases

Initial development was quite rapid and partly based on existing
"hacks" and SemVer discipline was limited at this stage, hence the
slightly arbitrary early version numbers.

The changelog format is inspired by [keep-a-changelog](https://github.com/olivierlacan/keep-a-changelog).

## [Unreleased]

### Fixes
    - Orthographic projection flag *actually* enabled in CLI
    - Camera clipping causing problems in orthographic view, reduce draw distance.

## [1.1.0] - 2017-03-14

### Additions
    - Orthographic projection supported in CLI and GUI
    - Arrow normalisation between modes by max arrow length
    - Nonlinear mass rescaling option

### Changes
    - Modified arrow scaling algorithm, defaults
    - Fixed a serious bug in atom position updates
    - Fixed a bug in GIF output

## [1.0.0] - 2016-03-16

### Additions
    - Support for tiled arrays of modes using ImageMagick ("montage" option)
    
### Changes
    - Major API overhaul of options and configuration system
      - Project state and user themes can be saved/loaded via GUI
      - Config format shared with CLI and Python API

## [0.5.0] - 2016-02-22

### Additions
    - New configuration options including bounding box colour

### Changes
    - Outlining now uses Freestyle for a crisper and more customisable appearance
    
## [0.3.0] - 2016-02-09

### Additions
    - Customisable colours

### Changes
    - YAML dependency removed, use ConfigParser for human-friendly config files


## [0.2.2] - 2016-02-08

### Additions
    - Documentation with Sphinx

### Changes
    - Docstrings overhauled to use ReST
    
## [0.2.1] - 2016-02-08

    Initial Release: first "usable" version
    

[Unreleased]: https://github.com/ajjackson/ascii-phonons/compare/1.0.1...master
[1.1.0]: https://github.com/ajjackson/ascii-phonons/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/ajjackson/ascii-phonons/compare/0.5.0...1.0.0
[0.5.0]: https://github.com/ajjackson/ascii-phonons/compare/0.3.0...0.5.0
[0.3.0]: https://github.com/ajjackson/ascii-phonons/compare/0.2.2...0.3.0
[0.2.2]: https://github.com/ajjackson/ascii-phonons/compare/0.2.1...0.2.2
