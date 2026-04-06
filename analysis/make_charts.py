import json
import os
import matplotlib.pyplot as plt

RESULTS_FILE = "benchmarks/results/all_summaries.json"
OUTPUT_DIR = "analysis/visualizations"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(RESULTS_FILE, "r") as f:
    summaries = json.load(f)

names = [x["experiment_name"] for x in summaries]
latencies = [x["avg_latency_ms"] for x in summaries]
throughputs = [x["throughput_rps"] for x in summaries]
hit_rates = [x["cache_hit_rate"] for x in summaries]
memory = [x["memory_after_mb"] for x in summaries]

plt.figure()
plt.bar(names, latencies)
plt.title("Average Latency by Experiment")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/latency.png")

plt.figure()
plt.bar(names, throughputs)
plt.title("Throughput by Experiment")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/throughput.png")

plt.figure()
plt.plot(names, hit_rates)
plt.title("Cache Hit Rate")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/cache.png")

plt.figure()
plt.bar(names, memory)
plt.title("Memory Usage")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/memory.png")

print("Charts created")
