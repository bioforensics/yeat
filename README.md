# YEAT

YEAT (**Y**our **E**verday **A**ssembly **T**ool) is an all-in-one platform designed to assemble multiple samples of varying read types (both short and long) using a combination of reliable, widely used, and cutting-edge algorithms such as SPAdes and Flye. It utilizes a Snakemake workflow to preprocess sample reads, perform assembly, and postprocess the resulting contigs in parallel.

**Supported Read Types and Assembly Algorithms**

| Read Types  | Algorithms |
| ------------- | ------------- |
| Paired-end  | SPAdes<sup>[1](#reference-1)</sup>, MEGAHIT<sup>[2](#reference-2)</sup>, Unicycler<sup>[3](#reference-3)</sup>, PenguiN<sup>[4](#reference-4)</sup>, VelvetOptimiser<sup>[5](#reference-5)</sup> |
| Single-end | SPAdes<sup>[1](#reference-1)</sup>, MEGAHIT<sup>[2](#reference-2)</sup>, Unicycler<sup>[3](#reference-3)</sup>, PenguiN<sup>[4](#reference-4)</sup>, VelvetOptimiser<sup>[5](#reference-5)</sup> |
| PacBio CLR (<20% error) | Flye<sup>[6](#reference-6)</sup>, Canu<sup>[7](#reference-7)</sup>, Unicycler<sup>[3](#reference-3)</sup> |
| PacBio Corrected (<3% error) | Flye<sup>[6](#reference-6)</sup>, Canu<sup>[7](#reference-7)</sup>, Unicycler<sup>[3](#reference-3)</sup> |
| PacBio HiFi (<1% error) | Flye<sup>[6](#reference-6)</sup>, Canu<sup>[7](#reference-7)</sup>, Hifiasm<sup>[8](#reference-8)</sup>, Hifiasm-meta<sup>[9](#reference-9)</sup>, Unicycler<sup>[3](#reference-3)</sup>, metaMDBG<sup>[10](#reference-10)</sup> |
| ONT Regular (<20% error) | Flye<sup>[6](#reference-6)</sup>, Canu<sup>[7](#reference-7)</sup>, Unicycler<sup>[3](#reference-3)</sup> |
| ONT Corrected (<3% error) | Flye<sup>[6](#reference-6)</sup>, Canu<sup>[7](#reference-7)</sup>, Unicycler<sup>[3](#reference-3)</sup> |
| ONT High-quality (<5% error) | Flye<sup>[6](#reference-6)</sup>, Canu<sup>[7](#reference-7)</sup>, Unicycler<sup>[3](#reference-3)</sup> |

## Installation (for Linux only)

```
git clone https://github.com/bioforensics/yeat.git
cd yeat
conda env create -f environment.yml
conda create -n yeat-metaMDBG -c bioconda "metamdbg>=1.0" -y
conda create -n yeat-velvet -c bioconda "perl-velvetoptimiser>=2.2" -y
conda activate yeat
pip install .
```

## Usage

```
yeat-auto short_reads --files {short_read1} {short_read2} > config.cfg
yeat --outdir {path} config.cfg
```

Run a simple YEAT job without a configuration file for paired-end reads ***only***:

```
just-yeat-it --outdir {path} {short_read1} {short_read2}
```

## References

1. <a id="reference-1"></a>Prjibelski, A., Antipov, D., Meleshko, D., Lapidus, A., & Korobeynikov, A. (2020). Using SPAdes de novo assembler. *Current Protocols in Bioinformatics*, 70, e102. doi: [10.1002/cpbi.102](https://doi.org/10.1002/cpbi.102)
2. <a id="reference-2"></a>Li, D., Luo, R., Liu, C.M., Leung, C.M., Ting, H.F., Sadakane, K., Yamashita, H. and Lam, T.W., 2016. MEGAHIT v1.0: A Fast and Scalable Metagenome Assembler driven by Advanced Methodologies and Community Practices. Methods.
3. <a id="reference-3"></a>Wick RR, Judd LM, Gorrie CL, Holt KE (2017) Unicycler: Resolving bacterial genome assemblies from short and long sequencing reads. PLOS Computational Biology 13(6): e1005595. https://doi.org/10.1371/journal.pcbi.1005595
4. <a id="reference-4"></a>PenguiN: Jochheim A, Jochheim FA, Kolodyazhnaya A, Morice E, Steinegger M, Soeding J. Strain-resolved de-novo metagenomic assembly of viral genomes and microbial 16S rRNAs. Microbiome 12, 187, (2024)
5. <a id="reference-5"></a>https://github.com/tseemann/VelvetOptimiser
6. <a id="reference-6"></a>Mikhail Kolmogorov, Jeffrey Yuan, Yu Lin and Pavel Pevzner, "Assembly of Long Error-Prone Reads Using Repeat Graphs", Nature Biotechnology, 2019 [doi:10.1038/s41587-019-0072-8](https://doi.org/10.1038/s41592-020-00971-x)
7. <a id="reference-7"></a>Koren S, Walenz BP, Berlin K, Miller JR, Phillippy AM. [Canu: scalable and accurate long-read assembly via adaptive k-mer weighting and repeat separation](https://doi.org/10.1101/gr.215087.116). Genome Research. (2017). `doi:10.1101/gr.215087.116`
8. <a id="reference-8"></a>Cheng, H., Asri, M., Lucas, J., Koren, S., Li, H. (2024) Scalable telomere-to-telomere assembly for diploid and polyploid genomes with double graph. *Nat Methods*, **21**:967-970. https://doi.org/10.1038/s41592-024-02269-8
9. <a id="reference-9"></a>Feng, X., Cheng, H., Portik, D. et al. Metagenome assembly of high-fidelity long reads with hifiasm-meta. *Nat Methods* **19**, 671–674 (2022). https://doi.org/10.1038/s41592-022-01478-3
10. <a id="reference-10"></a>Gaetan Benoit, Sebastien Raguideau, Robert James, Adam M. Phillippy, Rayan Chikhi and Christopher Quince [High-quality metagenome assembly from long accurate reads with metaMDBG](https://www.nature.com/articles/s41587-023-01983-6), Nature Biotechnology (2023).
