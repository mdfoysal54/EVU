---
name: memory-consolidation
description: Compress, summarize, and resolve conflicting observations over time.
tags:
  - memory
  - consolidation
  - hierarchy
---

# Memory Consolidation

During periodic or background context maintenance:

1. Group related observations and session turns by URI scope.
2. Run map-reduce chunk summarization over long message sequences.
3. Detect contradictory decisions; mark older, unreinforced nodes as archived.
4. Elevate recurring observations to high-level abstract nodes.