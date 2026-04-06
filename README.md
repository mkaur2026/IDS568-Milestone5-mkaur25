# IDS 568 Milestone 5 — LLM Inference Optimization (Batching + Caching)

## Overview

This project implements a FastAPI-based LLM inference server with two optimization strategies:

- Dynamic request batching  
- In-memory caching  

The goal is to improve:

- Throughput  
- Latency  
- Cache efficiency  
- Resource utilization  

A lightweight Hugging Face model (`sshleifer/tiny-gpt2`) is used to ensure stable execution on Mac hardware. The focus of this milestone is system architecture, batching behavior, caching behavior, benchmarking, and governance — not model quality.

---

# Repository Structure

```
ids568-milestone5-mkaur25/
│
├── src/
│   ├── server.py
│   ├── batching.py
│   ├── caching.py
│   └── config.py
│
├── benchmarks/
│   ├── __init__.py
│   ├── load_generator.py
│   ├── run_benchmarks.py
│   └── results/
│
├── analysis/
│   ├── make_charts.py
│   ├── performance_report.md
│   ├── performance_report.pdf
│   ├── governance_memo.md
│   ├── governance_memo.pdf
│   └── visualizations/
│
├── requirements.txt
└── README.md
```

---

# Features

FastAPI inference API

Dynamic batching:
- configurable batch size
- configurable timeout

Caching:
- TTL expiration
- max cache size
- hashed cache keys

Benchmarking:
- synthetic load generator
- reproducible benchmark runner

Performance Analysis:
- latency measurement
- throughput measurement
- cache hit rate
- memory usage

Visualization:
- latency charts
- throughput charts
- cache hit rate charts
- memory usage charts

---

# Setup Instructions

## Step 1 — Clone Repository

```
git clone <your-repo-url>
cd ids568-milestone5-mkaur25
```

---

## Step 2 — Create Virtual Environment

```
python3 -m venv .venv
```

Activate:

Mac / Linux:

```
source .venv/bin/activate
```

Windows:

```
.venv\Scripts\activate
```

---

## Step 3 — Install Dependencies

```
pip install -r requirements.txt
```

---

# Running the Server

Start FastAPI server:

```
uvicorn src.server:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

# Test the Server

Health Check:

```
curl http://127.0.0.1:8000/
```

Generate Request:

```
curl -X POST http://127.0.0.1:8000/generate \
-H "Content-Type: application/json" \
-d '{"prompt":"Explain machine learning in one sentence.","max_tokens":20,"temperature":0.0}'
```

---

# Caching Behavior

Caching is enabled only when:

```
temperature = 0.0
```

Caching is disabled when:

```
temperature > 0
```

Cache characteristics:

- hashed keys  
- TTL expiration  
- max entry limit  
- in-memory store  

---

# Configuration

Config file:

```
src/config.py
```

Configurable parameters:

- model_name  
- default_temperature  
- default_max_new_tokens  
- max_batch_size  
- batch_timeout_seconds  
- cache_ttl_seconds  
- cache_max_entries  
- host  
- port  

---

# Running Benchmarks

Keep server running, then execute:

```
python benchmarks/run_benchmarks.py --run_all
```

This runs:

- low load cached  
- medium load cached  
- high load cached  
- low load noncached  
- medium load noncached  

---

# Benchmark Results Location

Results saved in:

```
benchmarks/results/
```

Generated files:

- CSV request logs  
- JSON summary files  
- Combined summary file  

---

# Generate Charts

After benchmarks finish:

```
python analysis/make_charts.py
```

Charts saved in:

```
analysis/visualizations/
```

Charts generated:

- latency_by_experiment.png  
- throughput_by_experiment.png  
- cache_hit_rate.png  
- memory_usage.png  

---

# Performance Metrics Collected

Latency Metrics:
- average latency  
- min latency  
- max latency  

Throughput:
- requests per second  

Caching:
- cache hit rate  

Memory:
- memory before  
- memory after  
- memory delta  

---

# System Architecture

Request Flow:

Client  
→ FastAPI  
→ Cache Check  
→ Batch Queue  
→ Model Inference  
→ Cache Store  
→ Response  

---

# Batching Behavior

Batch triggers when:

- batch size reached  
OR  
- timeout reached  

Benefits:

- improved throughput  
- reduced compute overhead  
- better concurrency handling  

Trade-off:

- slightly increased latency  

---

# Caching Behavior

Cache improves:

- repeated request latency  
- throughput  

Trade-off:

- memory usage  
- stale response risk  

---

# Governance Considerations

Caching risks:

- storing sensitive prompts  
- stale outputs  
- data retention concerns  

Mitigation:

- TTL expiration  
- hashed keys  
- bounded cache size  
- deterministic caching only  

Governance memo located at:

```
analysis/governance_memo.md
analysis/governance_memo.pdf
```

---

# Performance Report

Performance report located at:

```
analysis/performance_report.md
analysis/performance_report.pdf
```

---

# Dependencies

Key libraries:

- FastAPI  
- Uvicorn  
- Transformers  
- Torch  
- httpx  
- psutil  
- matplotlib  
- numpy  

---

# Reproducibility

To reproduce:

Start server:

```
uvicorn src.server:app --reload
```

Run benchmarks:

```
python benchmarks/run_benchmarks.py --run_all
```

Generate charts:

```
python analysis/make_charts.py
```

---

# Notes

Small model used for Mac stability:

```
sshleifer/tiny-gpt2
```

Focus of milestone:

- batching optimization  
- caching optimization  
- benchmarking  
- governance  
- performance evaluation  

Not model accuracy.

---
