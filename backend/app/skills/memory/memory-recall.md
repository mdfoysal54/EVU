---
name: memory-recall
description: Systematically query and verify past context prior to planning and execution.
tags:
  - memory
  - retrieval
  - context
---

# Memory Recall

Before executing tasks or proposing solutions:

1. Extract core entities, task objectives, and project boundaries from current prompt.
2. Query episodic memory for previous user preferences, run histories, and system constraints.
3. Search semantic/hierarchical nodes for decisions made in related scopes.
4. Filter out superseded memories; retain only verified high-confidence lessons.