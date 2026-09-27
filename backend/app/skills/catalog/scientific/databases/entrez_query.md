---
name: entrez-query-broker
description: Query biological and chemical databases via uniform access APIs.
domain: scientific/databases
version: 1.0.0
tags: databases, pubmed, chembl, uniprot, ncbi
required_tools: web_research
safety_level: standard
---

# Scientific Database Query Broker

## Operational Protocol
1. Map user queries into domain-specific access parameters (e.g., PMID, ChEMBL target, PDB ID).
2. Execute parameterized searches using the unified `ScientificDatabase` connector abstraction.
3. Return results converted directly into `EvidenceRecord` items containing source timestamps and retrieval URLs.