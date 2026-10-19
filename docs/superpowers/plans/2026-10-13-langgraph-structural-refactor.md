# LitAgent LangGraph Structural Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the monolithic LangGraph implementation with a readable orchestration graph while preserving the current Router, Planner, Executor, search, read, RAG, HITL, checkpoint, and FastAPI behavior.

**Architecture:** Preserve the old implementation byte-for-byte as `agent/graph_legacy.py` and create the maintained graph in `agent/graph.py`. The maintained graph owns only state, node functions, routing functions, graph registration, and SQLite checkpoint creation. Existing tools, services, and RAG functions remain the implementations used by nodes. A single reusable `paper_search_node` handles both direct paper search and planner search steps; planner search results are cached in `search_results`, and paper content/analysis are cached in state.

**Tech Stack:** Python 3.14, LangGraph, LangChain, FastAPI, SQLite checkpointing, pytest/unittest-compatible standard library tests.

## Global Constraints

- Do not add business capabilities, a PDF parser, an MCP provider, memory, or UI.
- Do not modify the old graph implementation; move it unchanged to `agent/graph_legacy.py`.
- Keep the maintained graph focused on State, Nodes, Edges, Conditional Edges, and Checkpoint.
- Use one generic `paper_search_node`; do not create `paper_search_step` or `planner_paper_search_node`.
- Search once per planner workflow and reuse `search_results` for selection/reasoning.
- Read each selected paper once and reuse `paper_contents` and `paper_analyses`.
- A missing full text must interrupt with title, DOI, and a user PDF target path; it must not route back to Executor.
- Do not commit or push changes.

---

### Task 1: Establish regression tests for the new graph contract

**Files:**
- Create: `mini-agent/tests/test_graph_refactor.py`
- Read-only reference: `mini-agent/agent/graph.py`

**Interfaces:**
- Tests will import `ResearchState`, `build_research_graph`, and pure routing helpers from the maintained graph.
- Tests will inject fake models and monkeypatch existing tool/service functions so no network or Chroma dependency is needed.

- [ ] **Step 1: Write failing tests for the required public graph shape**

  Assert that the new graph exposes the expected state keys, registers exactly the required maintained nodes, contains valid edge targets, and has no legacy node names such as `planner_paper_search` or `planner_final`.

- [ ] **Step 2: Write failing tests for routing and progress invariants**

  Cover route selection, approval selection, executor action selection, plan completion, valid action normalization, and that a completed capability step increments `current_step` exactly once.

- [ ] **Step 3: Write failing tests for search/read reuse**

  Execute a planner search step twice against a state that already has `search_results` and assert the injected search function is called once. Execute paper-read against cached `paper_contents` and assert the reader/resolver are not called again.

- [ ] **Step 4: Write a failing test for the full-text interrupt payload**

  Supply a paper whose resolver returns `need_fulltext`, invoke `paper_read_node` through a compiled graph, and assert the interrupt payload includes `title`, `doi`, and a PDF target path and that the graph checkpoint does not point to `executor` as a retry loop.

- [ ] **Step 5: Run the focused tests and verify expected failures**

  Run from `mini-agent`:

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests\test_graph_refactor.py -q
  ```

  Expected: FAIL because the maintained graph contract is not implemented yet.

### Task 2: Preserve the old graph and create the minimal maintained graph skeleton

**Files:**
- Rename: `mini-agent/agent/graph.py` → `mini-agent/agent/graph_legacy.py` (content unchanged)
- Create: `mini-agent/agent/graph.py`
- Create: `mini-agent/agent/__init__.py` if needed for stable imports

**Interfaces:**
- Produces `build_research_graph(model, checkpoint_path="data/checkpoints.sqlite")`.
- Produces `ResearchState` with only explicit workflow fields: `user_query`, `route`, `search_query`, `search_results`, `selected_papers`, `paper_contents`, `paper_analyses`, `plan`, `current_step`, `step_action`, `step_results`, `answer`, `messages`, `trace`, `approved`, and `pending_fulltext`.

- [ ] **Step 1: Rename the original file without changing its contents**

  Use a file move operation and verify the hash/content of `graph_legacy.py` matches the pre-change `graph.py`.

- [ ] **Step 2: Add the new state definition and imports**

  Use `TypedDict`/`NotRequired`, `operator.add` only for append-only `trace`, `step_results`, and `messages`, and avoid duplicated `search_query` or a global status field.

- [ ] **Step 3: Add checkpoint construction**

  Resolve the default SQLite path relative to the project working directory, create `SqliteSaver`, and compile the graph with the checkpointer. Keep the builder construction separate from node business calls.

- [ ] **Step 4: Run import and compile tests**

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests\test_graph_refactor.py -q
  ```

  Expected: shape tests move closer to passing; behavior tests remain red until nodes are implemented.

### Task 3: Implement focused nodes and reusable capability helpers

**Files:**
- Modify: `mini-agent/agent/graph.py`
- Modify only if required for an existing-interface cleanup: `mini-agent/services/fulltext_resolver.py`, `mini-agent/tools/paper_reader.py`, `mini-agent/agent/paper_search_pipeline.py`, `mini-agent/rag/pipeline.py`

**Interfaces:**
- Nodes: `router_node`, `planner_node`, `executor_node`, `direct_answer_node`, `rewrite_query_node`, `rag_node`, `paper_search_node`, `paper_read_node`, `reasoning_node`, `final_answer_node`, `approval_node`, `cancel_node`.
- Pure routing helpers: `route_from_state`, `approval_route`, `action_route`, `plan_route`.
- Internal helpers: `normalize_action`, `parse_plan_response`, `step_text`, `append_step_result`, `paper_key`, `fulltext_request`.

- [ ] **Step 1: Implement router and planner nodes**

  Router invokes the existing router factory and returns only `route` plus a concise trace entry. Planner asks the model for `SEARCH_QUERY` and numbered `PLAN` lines, initializes `current_step` to `0`, and does not call tools.

- [ ] **Step 2: Implement executor as a dispatcher only**

  Executor reads `plan[current_step]`, asks the model for one of `paper_search`, `paper_read`, `rag`, or `reasoning`, normalizes harmless formatting such as backticks, logs only `[Executor] step=... action=...`, and returns `step_action` without performing work.

- [ ] **Step 3: Implement one generic paper search node**

  For a direct route, search `user_query`; for a planner step, use the planner `search_query` or current step. If `search_results` already exists for the workflow, reuse it. Otherwise call the existing `search_papers` tool exactly once, normalize its list/string result, save it as `search_results`, and select from that cache without a second API call. Direct route produces the final answer through the existing paper-search agent only where necessary; the planner path stores structured results for later steps.

- [ ] **Step 4: Implement reusable paper read and analysis caching**

  For selected papers not present in `paper_contents`, call the existing reader and resolver once. Cache ready content. When content is ready, call the model once for the current extraction task and cache the structured result in `paper_analyses`; later method/dataset/advantages/limitations steps read the cache. When content is missing, call `interrupt` with an object containing `type`, `message`, `papers`, `title`, `doi`, and `pdf_target_path` under `data/workspace/{thread_id}/`, then stop that graph path without incrementing `current_step` or returning to Executor.

- [ ] **Step 5: Implement RAG, reasoning, final answer, direct answer, approval, and cancel nodes**

  Reuse existing `rewrite_query` and `answer_with_rag` implementations. Reasoning consumes cached `step_results`, `search_results`, `paper_contents`, and `paper_analyses`; it does not search or reread papers. Final answer consumes the accumulated results. Approval remains the only external-search gate for the direct paper-search route.

- [ ] **Step 6: Run focused tests and refactor only after green**

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests\test_graph_refactor.py -q
  ```

  Expected: PASS with no debug-print assertions and no network calls.

### Task 4: Register the readable graph topology

**Files:**
- Modify: `mini-agent/agent/graph.py`

**Interfaces:**
- The compiled graph exposes the canonical node names and only valid conditional edge destinations.

- [ ] **Step 1: Register all nodes exactly once**

  Register `router`, `direct_answer`, `rewrite_query`, `rag`, `approval`, `paper_search`, `cancel`, `planner`, `executor`, `paper_read`, `reasoning`, and `final_answer`.

- [ ] **Step 2: Add simple-route edges**

  Connect `START → router`; route to `direct_answer`, `rewrite_query`, `approval`, or `planner`; connect direct answer/RAG/paper search/cancel to `END`.

- [ ] **Step 3: Add planner loop edges**

  Connect `planner → executor`; route executor actions to the four reusable capability nodes; connect each successful capability to `plan_route`; route `continue → executor` and `finish → final_answer → END`.

- [ ] **Step 4: Add interrupt-safe paper-read behavior**

  Ensure the missing-fulltext branch pauses at `paper_read` via LangGraph interrupt, and the normal edge after a completed read goes only to `plan_route`, never directly to `executor` before the completion check.

- [ ] **Step 5: Run graph topology assertions**

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests\test_graph_refactor.py -q
  ```

### Task 5: Switch supported entry points and clean only confirmed dead experimental code

**Files:**
- Modify: `mini-agent/api/main.py` only for import compatibility if required
- Modify: `mini-agent/main.py`
- Modify: `mini-agent/test.py`
- Modify: `mini-agent/start_interrupt.py`
- Modify: `mini-agent/resume_interrupt.py`
- Modify: `mini-agent/check_checkpoint.py`
- Delete only after reference checks: confirmed unused experimental modules, if any

**Interfaces:**
- All maintained entry points import `build_research_graph` from the new `agent.graph`.
- FastAPI request/response shape remains unchanged.

- [ ] **Step 1: Search references before deletion or renaming**

  ```powershell
  rg -n --glob '!mini-agent/.venv/**' "graph_legacy|agent\.graph|build_research_graph|paper_html|paper_pdf|paper_search_mcp" mini-agent
  ```

- [ ] **Step 2: Update only graph imports and stale state assumptions**

  Keep API endpoints, request models, thread ID handling, streaming events, and checkpoint config unchanged unless the new state contract requires a field rename.

- [ ] **Step 3: Remove confirmed dead graph-only imports and debug code**

  Do not delete tools/services referenced by any non-graph module. Remove only imports or experimental files proven unused by the reference scan.

- [ ] **Step 4: Run compile/import checks**

  ```powershell
  .\.venv\Scripts\python.exe -m compileall -q agent api tools services rag
  .\.venv\Scripts\python.exe -c "from api.main import app, graph; print(type(app).__name__, type(graph).__name__)"
  ```

### Task 6: Verify the refactor and document the handoff

**Files:**
- Modify: `mini-agent/README.md` only if the actual node names/topology changed from the documented architecture
- Create: `mini-agent/docs/superpowers/specs/2026-10-13-langgraph-structural-refactor-design.md`

- [ ] **Step 1: Run the complete available test suite excluding virtualenv files**

  ```powershell
  .\.venv\Scripts\python.exe -m pytest -q --ignore=.venv
  ```

- [ ] **Step 2: Run static/reference checks**

  Confirm no legacy node names remain in the maintained graph, no `print` statements remain in it, all imports compile, all registered edge targets exist, and `graph_legacy.py` remains unchanged.

- [ ] **Step 3: Generate the final Mermaid topology**

  Document the actual compiled graph, not an aspirational graph.

- [ ] **Step 4: Record remaining TODOs**

  Explicitly list full-text PDF parsing, temporary workspace upload plumbing, better paper selection, error/retry handling, and any existing experimental modules intentionally retained because they are still referenced.

