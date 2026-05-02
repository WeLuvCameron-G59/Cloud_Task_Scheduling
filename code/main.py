import random
import heapq
import copy
import time
import csv
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
    # FIX: deep copy wolves
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

    # execute best schedule
    time_now = 0
    for p in best:
        time_now = max(time_now, p.arrival)
        p.start = time_now
        p.completion = time_now + p.burst
        time_now = p.completion

    return best


# ----------------------------
# Experiment Runner (multi-trial)
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

                # measure execution time
                start = time.time()
                completed = algo(processes)
                end = time.time()

                avg_wait, avg_turn, throughput = compute_metrics(completed)

                all_results.append({
                    "tasks": n,
                    "trial": t,
                    "algorithm": name,
                    "waiting": avg_wait,
                    "turnaround": avg_turn,
                    "throughput": throughput,
                    "runtime": end - start
                })

        print(f"Completed experiments for {n} tasks")

    return all_results


# ----------------------------
# Save CSV
# ----------------------------
def save_results(results, filename="results.csv"):
    keys = results[0].keys()

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {filename}")


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    task_sizes = [10, 50, 100, 500]
    results = run_experiments(task_sizes, trials=30)
    save_results(results)
