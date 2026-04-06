# Performance Report

## 1. Introduction

This project implements a FastAPI-based LLM inference server with two optimization strategies: dynamic batching and in-memory caching. The purpose of the system is to improve throughput, reduce redundant computation, and maintain stable behavior under concurrent load. The benchmark suite was used to measure how these optimizations affect latency, throughput, cache hit rate, and memory usage.

For local execution and stability on a Mac environment, the implementation uses `sshleifer/tiny-gpt2` instead of a larger production model. The goal of this milestone is not text quality, but inference system behavior, reproducible benchmarking, and engineering trade-off analysis.

## 2. System Design and Compute Pathway

The system follows a simple inference-serving pipeline. A request reaches the FastAPI `/generate` endpoint and is validated through a request schema. The server then checks whether the request is eligible for caching. In this implementation, only deterministic requests with `temperature = 0.0` are cached.

If a valid cached response exists, the system immediately returns the cached output. If not, the request is submitted to the dynamic batcher. The batcher collects concurrent requests and processes them when either the configured batch size is reached or the configured timeout expires. After inference completes, the system returns the generated text and optionally stores the response in cache.

This pathway reflects the performance logic emphasized in class: cache hits skip model work entirely, while batching reduces repeated overhead by grouping requests together. In production systems, batching improves utilization while caching reduces unnecessary inference for repeated prompts. The module materials also emphasize that LLM serving should be structured around async request handling, batching, caching, and benchmarking. :contentReference[oaicite:1]{index=1} :contentReference[oaicite:2]{index=2}

## 3. Methodology

The benchmark suite was implemented using two scripts:
- `benchmarks/load_generator.py`
- `benchmarks/run_benchmarks.py`

The load generator sends synthetic concurrent requests to the FastAPI server. The benchmark runner executes multiple scenarios and saves both raw request logs and summary metrics into `benchmarks/results/`.

The following benchmark scenarios were run:
1. low load, cached
2. medium load, cached
3. high load, cached
4. low load, noncached
5. medium load, noncached

Repeated prompts were intentionally included in the synthetic workload so that cache hit behavior could be observed. Cached experiments used `temperature = 0.0`, which allowed deterministic cache reuse. Noncached experiments used `temperature = 0.7`, which forced cache bypass. This matches the class guidance that caching is most appropriate for deterministic generation settings. :contentReference[oaicite:3]{index=3}

The benchmark suite collected:
- average latency
- minimum latency
- maximum latency
- throughput in requests per second
- cache hit rate
- memory before and after each experiment

Raw results were stored in CSV and JSON files for reproducibility, and chart images were saved under `analysis/visualizations/`. This aligns with the milestone requirement to provide reproducible benchmark scripts, raw results, and performance visualizations. :contentReference[oaicite:4]{index=4}

## 4. Results

The benchmark results showed clear differences between cached and noncached request patterns.

### Latency

Cached workloads generally produced lower latency because repeated deterministic requests could be served directly from the in-memory cache instead of being sent to model inference. Manual API testing also confirmed this behavior: the first deterministic request returned `cached: false`, while the repeated request returned `cached: true` with much lower latency.

### Throughput

Throughput improved in cached scenarios because some repeated requests avoided model generation entirely. Even in noncached scenarios, the batching layer allowed the system to handle concurrent requests in a more structured way.

### Cache Hit Rate

Cache hit rate increased only in deterministic workloads with repeated prompts. This is the expected result because cache usage was intentionally disabled for non-deterministic requests. The result supports the class recommendation that response caching is best suited to deterministic or low-variability tasks. :contentReference[oaicite:5]{index=5}

### Memory Usage

Memory usage stayed relatively stable because the model was very small and the cache was bounded by both TTL and a maximum entry limit. In a larger real-world deployment, memory trade-offs would become more significant because both model weights and cache contents would be much larger.

## 5. Why the Optimizations Help

Batching and caching improve performance for different reasons.

### Why batching helps

LLM serving benefits from batching because requests do not always need to be processed one at a time. Instead of repeatedly invoking the model for every single request independently, the system groups concurrent requests together and processes them as a batch. This reduces repeated overhead and improves overall efficiency. The class notes explain that batching matters because token generation is memory-bandwidth bound and multiple requests can share the weight-loading work more efficiently than isolated requests. :contentReference[oaicite:6]{index=6}

### Why caching helps

Caching improves performance because repeated deterministic requests can skip model inference altogether. If the same prompt and parameters appear again, the system can immediately return the stored result. This reduces latency and increases effective throughput. The module materials explain that warm-cache lookups are far cheaper than running the model again, which is why even moderate cache hit rates can reduce serving cost and delay. :contentReference[oaicite:7]{index=7}

## 6. Trade-Off Analysis

### Batch size vs. latency

If batch size is too small, GPU or inference utilization is weaker and throughput gains are limited. If batch size is too large, requests may wait too long in the queue before processing. This creates the core trade-off between throughput and user-facing latency. The class slides explicitly discuss this tuning problem and recommend balancing batch size and timeout rather than maximizing either one independently. :contentReference[oaicite:8]{index=8}

### Timeout vs. throughput

A shorter timeout improves responsiveness because requests do not wait long before being processed, but it may lead to smaller batches and lower throughput. A longer timeout can improve batching efficiency, but it also increases queue waiting time for users.

### Cache size vs. hit rate

A larger cache can hold more reusable responses and may improve hit rate. However, larger caches consume more memory and increase data retention concerns. A smaller cache is safer and lighter but less effective for repeated workloads.

### Determinism vs. cacheability

Caching works best when repeated requests are expected to produce the same answer. Once sampling is introduced with temperature greater than zero, caching becomes less appropriate because repeated requests may validly produce different outputs. That is why this project only cached deterministic requests.

## 7. Scaling Strategies

Several realistic improvements could extend this design:

1. Replace the in-memory cache with Redis for multi-instance serving.
2. Tune batch size and timeout based on measured queue depth and workload patterns.
3. Add p95 and p99 latency metrics for better tail-latency analysis.
4. Add request logging and queue wait instrumentation.
5. Use a larger model or quantized model to better demonstrate real throughput and memory trade-offs.
6. Extend the batcher toward continuous batching or adaptive batching, as discussed in class materials. :contentReference[oaicite:9]{index=9}

## 8. Conclusion

This milestone produced a complete inference-serving pipeline with:
- async FastAPI request handling
- deterministic caching
- dynamic batching
- reproducible benchmark scripts
- saved benchmark artifacts
- performance visualizations

The final system demonstrated the expected engineering behavior. Repeated deterministic requests were served quickly from cache, non-deterministic requests bypassed cache, and concurrent traffic could be handled through the batching layer. Overall, the project shows that inference optimization depends heavily on system design choices such as batching policy, caching policy, and reproducible measurement rather than just model size or output quality.
