import asyncio
import time
import statistics
import argparse
from typing import List, Dict, Any

import httpx


PROMPTS = [
    "Explain machine learning in one sentence.",
    "Explain deep learning in one sentence.",
    "What is a neural network?",
    "What is overfitting?",
    "What is regularization?",
    "Explain machine learning in one sentence.",
    "What is a neural network?",
    "What is overfitting?",
]


async def send_request(
    client: httpx.AsyncClient,
    url: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
) -> Dict[str, Any]:
    start = time.time()

    response = await client.post(
        url,
        json={
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )

    latency_ms = (time.time() - start) * 1000

    data = response.json()

    return {
        "prompt": prompt,
        "status_code": response.status_code,
        "latency_ms": round(latency_ms, 2),
        "cached": data.get("cached", False),
        "generated_text": data.get("generated_text", ""),
    }


async def run_load_test(
    url: str,
    total_requests: int,
    concurrency: int,
    max_tokens: int,
    temperature: float,
) -> (List[Dict[str, Any]], Dict[str, Any]):

    results = []

    limits = httpx.Limits(
        max_connections=concurrency,
        max_keepalive_connections=concurrency,
    )

    async with httpx.AsyncClient(timeout=60.0, limits=limits) as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_request(i: int):
            async with semaphore:
                prompt = PROMPTS[i % len(PROMPTS)]
                result = await send_request(
                    client=client,
                    url=url,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                results.append(result)

        tasks = [bounded_request(i) for i in range(total_requests)]

        start_total = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_total

    latencies = [r["latency_ms"] for r in results]
    cache_hits = sum(1 for r in results if r["cached"])
    throughput_rps = total_requests / total_time if total_time > 0 else 0

    summary = {
        "total_requests": total_requests,
        "concurrency": concurrency,
        "temperature": temperature,
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0,
        "min_latency_ms": round(min(latencies), 2) if latencies else 0,
        "max_latency_ms": round(max(latencies), 2) if latencies else 0,
        "throughput_rps": round(throughput_rps, 2),
        "cache_hit_rate": round(cache_hits / total_requests, 4) if total_requests > 0 else 0,
    }

    return results, summary


def main():
    parser = argparse.ArgumentParser(description="Synthetic load generator for Milestone 5")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:8000/generate")
    parser.add_argument("--total_requests", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--max_tokens", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    results, summary = asyncio.run(
        run_load_test(
            url=args.url,
            total_requests=args.total_requests,
            concurrency=args.concurrency,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
    )

    print("SUMMARY")
    print(summary)
    print("\nSAMPLE RESULTS")
    for row in results[:5]:
        print(row)


if __name__ == "__main__":
    main()
