# Changelog

All notable changes to PyPad project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Governance Framework (Phase 0)**: Established Single Source of Truth (`PROJECT.md`), Phase Gates (`ROADMAP.md`), Acceptance Standards (`ACCEPTANCE.md`), System Architecture (`ARCHITECTURE.md`), Progress Ledger (`PROGRESS.md`), and Development Constitution (`pypad_constitution.md`).
- **Core Backend Infrastructure (Phase 1-2)**: Auth (JWT), Knowledge Graph endpoints, Course & Chapter management, Workspace Code Runner, Practice submissions, and Dashboard overview.
- **Frontend SPA Baseline (Phase 1)**: Vue 3 + Vite + Tailwind CSS + Monaco Editor + Cytoscape.js views setup.
- **Backend Test Suite**: `tests/test_api.py` covering Auth, Knowledge, Courses, Workspace, Sessions, Practices, Agent, Dashboard (24 tests passed).
- **Sandbox Execution Engine (Phase 5)**: AST security scanning, subprocess isolation with timeout/memory limits, Docker container CGroups hard isolation (`sandbox_runner.py`, `docker_runner.py`). 6 tests passed.
- **Vector RAG Engine (Phase 4)**: TF-IDF cosine similarity search engine (`rag_service.py`). 3 tests passed.
- **Qdrant Vector Database Integration**: Persistent vector storage using Qdrant local mode with fastembed embeddings (`qdrant_rag_service.py`). Composite engine with TF-IDF fallback.
- **Topological Learning Path (Phase 7)**: DAG topological sort with Ebbinghaus forgetting curve decay algorithm (`topological_path.py`). 2 tests passed.
- **Textbook Parser (Phase 3)**: Markdown textbook parsing with heading hierarchy extraction, code block splitting, and automatic KnowledgeNode/KnowledgeEdge generation (`textbook_parser.py`). 2 tests passed.
- **E2E Integration Test (Phase 8)**: Complete 18-step end-to-end test covering the full learning loop: Register → Login → Knowledge Browse → Session → Code Execution → Practice → Mastery → Recommendation → RAG → AI Chat → Textbook Upload → Analytics (`tests/test_e2e.py`). 48 tests passed.
- **Project Documentation**: Fixed `PROGRESS.md` contradictions, updated `ROADMAP.md` with accurate Gate status.

### Changed
- **RAG Engine**: Upgraded from in-memory TF-IDF-only to Composite engine (Qdrant + TF-IDF fallback).
- **PROGRESS.md**: Rewritten to accurately reflect actual project state (~65% complete, Phase 0-2 gates passed).
- **ROADMAP.md**: Updated all Phase Gate checkboxes to reflect verified implementation status.

### Fixed
- `PROGRESS.md` internal contradictions (duplicate sections, conflicting status claims).
