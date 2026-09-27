---
name: memory-save
description: Gate and persist long-term state without introducing noise.
tags:
  - memory
  - storage
  - gate
---

# Memory Save

When saving state to memory:

1. Evaluate against write gate criteria (importance, novelty, durability).
2. Compute SHA-256 content fingerprint to prevent duplicate inserts within the active window.
3. Structure observations with precise tool actions, query intent, and actionable output.
4. Attach scope metadata (user_id, project_uri, context_type).