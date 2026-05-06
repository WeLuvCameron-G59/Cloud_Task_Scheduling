import random
import heapq
import copy
import time
import csv
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque

# ----------------------------
# Process Model
# ----------------------------
class Process:
    def __init__(self, pid, arrival, burst, priority=1):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority

        self.remaining = burst
        self.start = -1
        self.completion = 0
        self.waiting = 0
        self.turnaround = 0


# ----------------------------
# Workload Generator
# ----------------------------
def generate_processes(n, seed=42):
    random.seed(seed)

    processes = []
    for i in range(n):
        arrival = i
        burst = random.randint(1, 10)
        priority = random.randint(1, 5)
        processes.append(Process(f"P{i+1}", arrival, burst, priority))

    return processes


# ----------------------------
# Metrics
# ----------------------------
def compute_metrics(processes):
    n = len(processes)

    for p in processes:
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst

    avg_wait = sum(p.waiting for p in processes) / n
    avg_turn = sum(p.turnaround for p in processes) / n
    makespan = max(p.completion for p in processes)
    throughput = n / makespan

    return avg_wait, avg_turn, throughput


# ----------------------------
# FIFO
# ----------------------------
def fifo(processes):
    time_now = 0

    for p in processes:
        if time_now < p.arrival:
            time_now = p.arrival

        p.start = time_now
        p.completion = time_now + p.burst
        time_now = p.completion

    return processes


# ----------------------------
# Round Robin
# ----------------------------
def round_robin(processes, quantum=2):
    time_now = 0
    queue = deque()

    processes.sort(key=lambda x: x.arrival)
    i = 0
    completed = []

    while i < len(processes) or queue:

        while i < len(processes) and processes[i].arrival <= time_now:
            queue.append(processes[i])
            i += 1

        if not queue:
            time_now = processes[i].arrival
            continue

        p = queue.popleft()

        if p.start == -1:
            p.start = time_now

        exec_time = min(quantum, p.remaining)
        p.remaining -= exec_time
        time_now += exec_time

        while i < len(processes) and processes[i].arrival <= time_now:
            queue.append(processes[i])
            i += 1

        if p.remaining > 0:
            queue.append(p)
        else:
            p.completion = time_now
            completed.append(p)

    return completed


# ----------------------------
# Priority Scheduling
# ----------------------------
def priority_scheduling(processes):
    time_now = 0
    completed = []
    ready = []

    processes.sort(key=lambda x: x.arrival)
    i = 0

    while i < len(processes) or ready:

        while i < len(processes) and processes[i].arrival <= time_now:
            heapq.heappush(
                ready,
                (processes[i].priority, processes[i].arrival, processes[i].pid, processes[i])
            )
            i += 1

        if not ready:
            time_now = processes[i].arrival
            continue

        _, _, _, p = heapq.heappop(ready)

        p.start = time_now
        p.completion = time_now + p.burst
        time_now = p.completion

        completed.append(p)

    return completed


# ----------------------------
# Grey Wolf Optimization
# ----------------------------
def gwo_schedule(processes, iterations=10):
    wolves = [copy.deepcopy(processes) for _ in range(5)]

    def fitness(schedule):
        time_now = 0
        total_wait = 0

        for p in schedule:
            time_now = max(time_now, p.arrival)
            total_wait += time_now - p.arrival
            time_now += p.burst

        return total_wait

    for _ in range(iterations):
        wolves.sort(key=fitness)
        best = wolves[0]

        for i in range(1, len(wolves)):
            wolves[i] = copy.deepcopy(best)

    best = wolves[0]

    time_now = 0
    for p in best:
        time_now = max(time_now, p.arrival)
        p.start = time_now
        p.completion = time_now + p.burst
        time_now = p.completion

    return best


# ----------------------------
# Run Experiments
# ----------------------------
def run_experiments(task_sizes, trials=30):
    all_results = []

    algorithms = [
        ("FIFO", fifo),
        ("RoundRobin", lambda x: round_robin(x, 2)),
        ("Priority", priority_scheduling),
        ("GWO", gwo_schedule)
    ]

    for n in task_sizes:
        for t in range(trials):
            for name, algo in algorithms:

                processes = generate_processes(n, seed=42 + t)
                processes = copy.deepcopy(processes)

                # Accurate empirical timing
                start = time.perf_counter()
                completed = algo(processes)
                end = time.perf_counter()

                avg_wait, avg_turn, throughput = compute_metrics(completed)

                all_results.append({
                    "tasks": n,
                    "trial": t,
                    "algorithm": name,
                    "waiting": round(avg_wait, 2),
                    "turnaround": round(avg_turn, 2),
                    "throughput": round(throughput, 3),
                    "runtime": round(end - start, 6)

                })

        print(f"Completed {n} tasks")

    return all_results


# ----------------------------
# Save Raw CSV
# ----------------------------
def save_results(results, filename="results.csv"):
    keys = results[0].keys()

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved raw data → {filename}")


# ----------------------------
# Create Clean Summary CSV
# ----------------------------
def create_summary(filename="results.csv"):
    df = pd.read_csv(filename)

    # Round raw values for readability
    df["waiting"] = df["waiting"].round(2)
    df["turnaround"] = df["turnaround"].round(2)
    df["throughput"] = df["throughput"].round(3)
    df["runtime"] = df["runtime"].round(6)

    summary = df.groupby(["tasks", "algorithm"]).agg({
        "waiting": ["mean", "std"],
        "turnaround": ["mean", "std"],
        "throughput": ["mean"],
        "runtime": ["mean"]
    }).reset_index()

    summary.columns = [
        "tasks", "algorithm",
        "wait_mean", "wait_std",
        "turn_mean", "turn_std",
        "throughput_mean",
        "runtime_mean"
    ]

    # FINAL ROUNDING OF SUMMARY VALUES
    summary["wait_mean"] = summary["wait_mean"].round(2)
    summary["wait_std"] = summary["wait_std"].round(2)
    summary["turn_mean"] = summary["turn_mean"].round(2)
    summary["turn_std"] = summary["turn_std"].round(2)
    summary["throughput_mean"] = summary["throughput_mean"].round(3)
    summary["runtime_mean"] = summary["runtime_mean"].round(6)

    summary.to_csv("summary_results.csv", index=False)
    print("Saved clean summary → summary_results.csv")



# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    task_sizes = [10, 50, 100, 500, 1000, 2000]
    results = run_experiments(task_sizes, trials=5)

    save_results(results)
    create_summary()

    # Load results for plotting
    df = pd.read_csv("results.csv")

    grouped = df.groupby(["tasks", "algorithm"])["runtime"].mean().reset_index()
    algorithms = grouped["algorithm"].unique()

    for algo in algorithms:
        plt.figure()

        data = grouped[grouped["algorithm"] == algo]

        plt.plot(data["tasks"], data["runtime"], marker='o', label=algo)

        plt.title(f"{algo} Runtime Scaling")
        plt.xlabel("Number of Tasks")
        plt.ylabel("Average Execution Time (seconds)")

        plt.legend()   
        plt.grid()

        plt.show()

        plt.figure()

# ----------------------------
# Combined graph
# ----------------------------
    plt.figure()

    for algo in algorithms:
        data = grouped[grouped["algorithm"] == algo]
        plt.plot(data["tasks"], data["runtime"], marker='o', label=algo)

    # Set labels AFTER plotting all lines
    plt.title("Runtime Scaling Comparison")
    plt.xlabel("Number of Tasks")
    plt.ylabel("Average Execution Time (seconds)")

    plt.legend(title="Scheduling Algorithm")
    plt.grid()

    plt.show()