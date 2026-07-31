# AegisLLM
Autonomous framework for benchmarking, attacking, and defending Large Language Models against prompt injection, jailbreaks, tool abuse, and agentic threats.



                   AegisLLM
                        │
    ┌───────────────────┼────────────────────┐
    │                   │                    │
 Attack Engine     Defense Engine     Evaluation Engine
    │                   │                    │
    ▼                   ▼                    ▼
Prompt Injection   Regex Filter        Metrics
Jailbreak          ML Classifier       Leaderboard
Tool Abuse         Embeddings          Reports
Memory Poisoning   LLM Judge           Dashboard
Context Overflow   Hybrid Defense      Visual Analytics
