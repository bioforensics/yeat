# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3] 2023-05-20

### Added
- Support for Bandage (#34)
- Long-read assembly algorithms:
    - Flye and Canu (#37)
- Input read support:
    - Pacbio raw, corrected, and Hifi-reads (#37, #47)
    - Oxford Nanopore raw, corrected, and HAC (#47)

### Changed
- Config file to enable:
    - Support for multi-input samples (#43)
    - Running multiple assembly algorithm with labels (#43)


## [0.2] 2022-11-09

### Added
- Support for FastQC (#5)
- Support for MEGAHIT (#13)
- Support for Unicycler (#14)
- Support for assembly configuration file (#16)
- Commands to run a short or long test suite (#20)
- Custom downsampling flag (#21)
- Custom coverage flag (#23)
- Custom seed flag (#29)
- 3.9 Python version pin for `exit_on_error` parameter and 3.10's incompatibility with SPAdes <v3.15.4 (#23, #29)
- Custom genome size flag (#30)

### Fixed
- Support for uncompressed input files (#31)


## [0.1] 2021-12-01

Initial release!
