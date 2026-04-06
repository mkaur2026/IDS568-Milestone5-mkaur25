import os
import csv
import json
import time
import argparse
import asyncio
from typing import List, Dict, Any

import psutil

from load_generator import run_load_test


RESULTS_DIR = "benchmarks/results"


def ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def save_csv(path: str, rows: List[Dict[str, Any]]):
    if not rows:
        return

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def save_json(path: str, data: Any):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


async def run_one_experiment(
    name: str,
    total_requests: int,
    concurrency: int,
    temperature: float,
) -> Dict[str, Any]:

    process = psutil.Process()
    mem_before_mb = process.memory_info().rss / (1024 * 1024)

    rows, summary = await run_load_test(
        url="http://127.0.0.1:8000/generate",
        total_requests=total_requests,
        concurrency=concurrency,
        max_tokens=20,
        temperature=temperature,
    )

    mem_after_mb = process.memory_info().rss / (1024 * 1024)

    summary["experiment_name"] = name
    summary["memory_before_mb"] = round(mem_before_mb, 2)
    summary["memory_after_mb"] = round(mem_after_mb, 2)
    summary["memory_delta_mb"] = round(mem_after_mb - mem_before_mb, 2)

    save_csv(os.path.join(RESULTS_DIR, f"{name}.csv"), rows)
    save_json(os.path.join(RESULTS_DIR, f"{name}_summary.json"), summary)

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Milestone 5 benchmark suite")
    parser.add_argument("--run_all", action="store_true", help="Run the full benchmark suite")
    args = parser.parse_args()

    ensure_results_dir()

    if not args.run_all:
        print("Use --run_all to run the full benchmark suite.")
        return

    experiments = [
        ("low_load_cached", 20, 5, 0.0),
        ("medium_load_cached", 50, 10, 0.0),
        ("high_load_cached", 100, 20, 0.0),
        ("low_load_noncached", 20, 5, 0.7),
        ("medium_load_noncached", 50, 10, 0.7),
    ]

    summaries = []

    for name, total_requests, concurrency, temperature in experiments:
        print(f"Running {name} ...")
        summary = asyncio.run(
            run_one_experiment(
                name=name,
                total_requests=total_requests,
                concurrency=concurrency,
                temperature=temperature,
            )
        )
        summaries.append(summary)
        time.sleep(2)

    save_json(os.path.join(RESULTS_DIR, "all_summaries.json"), summaries)

    print("\nFinished all benchmark runs.")
    print("Saved files in benchmarks/results/")


if __name__ == "__main__":
    main()
