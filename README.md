<<<<<<< HEAD
=======
# EVU

## AI Meta-Orchestrator & Independent AI Platform
>>>>>>> a300924 (fix(auth): resolve database startup and authentication flow)

EVU is a modular AI platform designed to combine its own intelligence, memory, context, agents, tools, research, multimodal capabilities, model routing, evaluation, and continuous learning into one system.

The long-term objective is not to build another application that simply calls OpenAI, Claude, Gemini, or other external AI APIs.

The objective is to build:

> **An AI system that can understand, reason, remember, plan, act, use tools, evaluate its own work, learn from experience, and eventually operate using models trained and controlled by EVU itself.**

External AI models may be used when they provide a meaningful advantage, but they should remain optional specialists rather than becoming the foundation of EVU.

---

# Table of Contents

- [1. Vision](#1-vision)
- [2. What EVU Is](#2-what-evu-is)
- [3. Core Principles](#3-core-principles)
- [4. System Architecture](#4-system-architecture)
- [5. Major Subsystems](#5-major-subsystems)
- [6. AI and Agent Runtime](#6-ai-and-agent-runtime)
- [7. Memory and Context](#7-memory-and-context)
- [8. RAG and Knowledge](#8-rag-and-knowledge)
- [9. Research and Web Intelligence](#9-research-and-web-intelligence)
- [10. Browser and Tools](#10-browser-and-tools)
- [11. Coding Intelligence](#11-coding-intelligence)
- [12. Multimodal Intelligence](#12-multimodal-intelligence)
- [13. Workflow and Pipeline](#13-workflow-and-pipeline)
- [14. Diagram Engine](#14-diagram-engine)
- [15. Observability and Telemetry](#15-observability-and-telemetry)
- [16. EVU Model Lab](#16-evu-model-lab)
- [17. EVU Transformer](#17-evu-transformer)
- [18. Tokenizer](#18-tokenizer)
- [19. Training and Fine-Tuning](#19-training-and-fine-tuning)
- [20. Experience and Learning](#20-experience-and-learning)
- [21. Dataset Engineering](#21-dataset-engineering)
- [22. Evaluation and Benchmarking](#22-evaluation-and-benchmarking)
- [23. Model Registry](#23-model-registry)
- [24. Continuous Improvement](#24-continuous-improvement)
- [25. Independence Architecture](#25-independence-architecture)
- [26. Repository Structure](#26-repository-structure)
- [27. Technology Stack](#27-technology-stack)
- [28. Development Environment](#28-development-environment)
- [29. Running EVU](#29-running-evu)
- [30. Testing](#30-testing)
- [31. Model Lab Development](#31-model-lab-development)
- [32. Development Philosophy](#32-development-philosophy)
- [33. Current State](#33-current-state)
- [34. Remaining Work](#34-remaining-work)
- [35. Roadmap](#35-roadmap)
- [36. Long-Term Architecture](#36-long-term-architecture)
- [37. Independence Test](#37-independence-test)
- [38. Final Vision](#38-final-vision)

---

# 1. Vision

EVU is being developed as a complete AI platform rather than a single chatbot.

The system combines several layers:

```text
                    EVU
                     │
        ┌────────────┼────────────┐
        │            │            │
   Intelligence    Context       Action
        │            │            │
        ▼            ▼            ▼
     Models        Memory        Tools
     Routing       RAG           Agents
     Planning      Research      Browser
     Evaluation    Projects      Code
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
                 Experience
                     │
                     ▼
              Learning System
                     │
                     ▼
                Better EVU