# Tether — Parked Scope (P2 / Later)

Items explicitly deferred to future releases to protect the integrity and rock-solid execution of the P0 core workflow.

- **P2-01: Vector Embeddings & Semantic Clustering**: Integrating `pgvector` or local embeddings for semantic claim clustering. (Reason: Keyword, name, and attribute matching are deterministic and run without embedding keys).
- **P2-02: Live GitHub Webhook Ingestion**: Bi-directional webhook syncing for active multi-developer repos. (Reason: Hermetic evaluation requires deterministic, offline execution with zero network dependence).
- **P2-03: Audio Meeting Transcription Pipeline**: Whisper/speech-to-text models for recorded Zoom or Google Meet audio. (Reason: Outside text-first evidence model; requires large media files).
- **P2-04: Multi-Project Cross-Handover Graphs**: Aggregating knowledge dependencies across 10+ independent repos in an enterprise. (Reason: Scope frozen to one project, one leaver, three sources).
- **P2-05: Automated Leaver Exit Interview Generator**: Interactive conversational agent questioning the departing engineer. (Reason: Violates anti-chatbot principle; knowledge is captured while work happens).
