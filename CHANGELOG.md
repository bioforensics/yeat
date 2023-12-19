# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- Unicycler algorithm for long-read only assembly (#55)
- metaMDBG algorithm for PacBio-HiFi reads (#59)
- Grid support (#65)

### Changed
- Updated config input file format (#64)


## [0.4] 2023-08-23

### Added
- Input fastq read support:
    - Pacbio raw and corrected reads (#47)
    - Oxford Nanopore raw, corrected, and HAC reads (#47)
    - Single-end Illumina reads (#50)
- Support for Nanopore-reads assembly with Flye and Canu (#47, #50)
- New assemblers:
    - Hifiasm and Hifiasm-meta (#49)


## [0.3] 2023-05-20

### Added
- Support for Bandage (#34)
- Support for basic PacBio HiFi-reads assembly with Flye and Canu (#37)

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
