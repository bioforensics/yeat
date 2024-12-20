# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7] 2024-12-10

### Added
- Short-read assembly algorithms:
    - VelvetOptimizer (#81)
    - Penguin (#82)
- Nanopore-read assembly algorithms:
    - metaMDBG (#85)


## [0.6.1] 2024-07-02

### Changed
- Updated `--grid` and `--grid-args` arguments and Snakemake to be compatible with SLURM (#79)


## [0.6] 2024-04-19

### Added
- Hybrid assembly support (#68, #73)
- `just-yeat-it` CLI command for simple paired-end runs (#74)
- `yeat-auto` CLI command for auto-populating the sample section of the config file (#76)
- Customize downsample, depth of coverage, and genome size per sample (#77)


## [0.5] 2024-01-08

### Added
- Unicycler algorithm for long-read only assembly (#55)
- metaMDBG algorithm for PacBio-HiFi reads (#59)
- DRMAA grid support (#65)

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
