---
name: genomics-sequence-analysis
description: Analyze DNA, RNA, and protein sequences, alignments, and mutations.
domain: scientific/biology
version: 1.0.0
tags: biology, genomics, dna, rna, blast, fasta
required_tools: python_exec
safety_level: standard
---

# Genomics Sequence Analysis

## Operational Protocol
1. Validate incoming sequence strings (check for valid FASTA headers and IUPAC nucleotide/amino acid codes).
2. For BLAST/homology queries, prepare uniform inputs without raw multiline formatting errors.
3. Quantify GC-content, ORF candidates, or mutations against a reference sequence.
4. Always report sequence lengths, accession IDs, and alignment scores with statistical thresholds ($E < 10^{-5}$).