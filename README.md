
# LitAgent

LitAgent is a research paper search, reading, and comparison agent built with LangGraph.

It is designed for research scenarios where users need to search academic papers, read paper information, extract key details, and compare multiple papers through a multi-step Agent workflow.

## Features

- Route user requests to different workflows
- Plan complex research tasks automatically
- Execute multi-step tasks with dynamic capability routing
- Search academic papers through OpenAlex
- Read paper metadata and abstracts
- Extract methods, datasets, advantages, and limitations
- Compare multiple papers
- Local RAG with ChromaDB
- Reranking with BGE-Reranker
- LangGraph checkpoint persistence
- Human-in-the-loop approval
- FastAPI Gateway
- Automatic thread creation and reuse

## Architecture

```text
User Request
    ¡ý
FastAPI Gateway
    ¡ý
Thread Management
    ¡ý
Router
    ¡ý
©°©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©´
©¦ direct_answer               ©¦
©¦ local_rag                   ©¦
©¦ paper_search                ©¦
©¦ planner                     ©¦
©¸©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¼
             ¡ý
          Planner
             ¡ý
          Executor
             ¡ý
©°©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©´
©¦ paper_search                ©¦
©¦ paper_read                  ©¦
©¦ local_rag                   ©¦
©¦ reasoning                   ©¦
©¸©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¼
             ¡ý
        Final Answer
             ¡ý
      SQLite Checkpoint
```

## Core Workflow

For a complex research request such as:

```
Find 3 papers about LiDAR tree crown segmentation
and compare their methods, datasets, advantages and limitations.
```

LitAgent can:

```
1. Generate a search query
2. Search relevant papers
3. Select candidate papers
4. Read paper abstracts
5. Extract methods
6. Extract datasets
7. Analyze advantages and limitations
8. Compare the selected papers
9. Generate a final answer
```

## Tech Stack

* Python
* LangGraph
* LangChain
* FastAPI
* ChromaDB
* SQLite
* OpenAlex API
* DeepSeek API
* BGE-M3
* BGE-Reranker

## Project Structure

LitAgent/
©À©¤©¤ api/
©¦   ©¸©¤©¤ main.py
©¦
©À©¤©¤ agent/
©¦   ©À©¤©¤ graph.py
©¦   ©À©¤©¤ router.py
©¦   ©¸©¤©¤ paper_search_pipeline.py
©¦
©À©¤©¤ tools/
©¦   ©À©¤©¤ paper_search.py
©¦   ©¸©¤©¤ paper_reader.py
©¦
©À©¤©¤ rag/
©¦   ©À©¤©¤ embeddings.py
©¦   ©À©¤©¤ retriever.py
©¦   ©À©¤©¤ reranker.py
©¦   ©À©¤©¤ vector_store.py
©¦   ©À©¤©¤ pipeline.py
©¦   ©¸©¤©¤ query_rewriter.py
©¦
©À©¤©¤ data/
©¦   ©À©¤©¤ papers/
©¦   ©À©¤©¤ chroma_db/
©¦   ©¸©¤©¤ checkpoints.sqlite
©¦
©À©¤©¤ test.py
©À©¤©¤ pyproject.toml
©À©¤©¤ .gitignore
©¸©¤©¤ README.md

## Quick Start

### 1. Clone the repository

```
git clone https://github.com/lihua1234567lihua-collab/LitAgent.git
cd LitAgent
```

### 2. Install dependencies

This project uses `uv`.

```
uv sync
```

### 3. Configure environment variables

Create a `.env` file:

```
DEEPSEEK_API_KEY=your_api_key
```

### 4. Run the local test

```
uv run python test.py
```

### 5. Start the API Gateway

```
uv run uvicorn api.main:app --reload
```

Then open:

```
http://127.0.0.1:8000/docs
```

## Agent Design

### Router

The Router determines which main workflow should handle the user request.

Supported routes:

```
direct_answer
local_rag
paper_search
planner
```

### Planner

The Planner decomposes complex research requests into executable steps and generates academic search queries.

### Executor

The Executor reads the current plan step and dynamically selects the appropriate capability:

```
paper_search
paper_read
local_rag
reasoning
```

### State

LangGraph State stores intermediate information such as:

```
user_query
search_query
plan
current_step
selected_papers
step_results
answer
```

### Checkpoint

SQLite-based LangGraph checkpoints persist task state so interrupted tasks can be resumed later.

## Current Status

Implemented:

* [X] Router
* [X] Planner
* [X] Executor
* [X] Paper Search
* [X] Paper Abstract Reader
* [X] Local RAG
* [X] Query Rewrite
* [X] Embedding Retrieval
* [X] Reranking
* [X] Reasoning
* [X] SQLite Checkpoint
* [X] Human-in-the-loop
* [X] FastAPI Gateway
* [X] Automatic Thread ID

In progress:

* [ ] Full-text PDF reading
* [ ] Better paper selection strategy
* [ ] Streaming response
* [ ] Run management
* [ ] Error handling and retry
* [ ] Frontend interface

## Roadmap

Future improvements include:

* Full-text academic paper parsing
* PDF chunking and retrieval
* Better multi-paper comparison
* More academic search sources
* Streaming Agent events
* Task retry and failure recovery
* Long-term memory
* Web frontend

## License

This project is currently for learning and research purposes.
