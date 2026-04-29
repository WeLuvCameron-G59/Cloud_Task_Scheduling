import random
import heapq
import copy
from collections import deque

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

def generate_processes(n, seed=42):
    random.seed(seed)

    processes = []
    for i in range(n):
        arrival = i  # deterministic arrival
        burst = random.randint(1, 10)
        priority = random.randint(1, 5)
        processes.append(Process(f"P{i+1}", arrival, burst, priority))

    return processes

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

def round_robin(processes, quantum=2):
    time = 0
    queue = deque()

    processes.sort(key=lambda x: x.arrival)
    i = 0
    completed = []

    while i < len(processes) or queue:

        while i < len(processes) and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time = processes[i].arrival
            continue

        p = queue.popleft()

        if p.start == -1:
            p.start = time

        exec_time = min(quantum, p.remaining)
        p.remaining -= exec_time
        time += exec_time

        while i < len(processes) and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if p.remaining > 0:
            queue.append(p)
        else:
            p.completion = time
            completed.append(p)

    return completed

def fifo(processes):
    time = 0

    for p in processes:
        if time < p.arrival:
            time = p.arrival

        p.start = time
        p.completion = time + p.burst
        time = p.completion

    return processes

def priority_scheduling(processes):
    time = 0
    completed = []
    ready = []

    processes.sort(key=lambda x: x.arrival)
    i = 0

    while i < len(processes) or ready:

        while i < len(processes) and processes[i].arrival <= time:
            heapq.heappush(
                ready,
                (processes[i].priority, processes[i].arrival, processes[i].pid, processes[i])
            )
            i += 1

        if not ready:
            time = processes[i].arrival
            continue

        _, _, _, p = heapq.heappop(ready)

        if time < p.arrival:
            time = p.arrival

        p.start = time
        p.completion = time + p.burst
        time = p.completion

        completed.append(p)

    return completed

def gwo_schedule(processes, iterations=10):
    wolves = [processes[:] for _ in range(5)]  # population of schedules

    def fitness(schedule):
        time = 0
        total_wait = 0

        for p in schedule:
            time = max(time, p.arrival)
            total_wait += time - p.arrival
            time += p.burst

        return total_wait

    best = min(wolves, key=fitness)

    for _ in range(iterations):
        wolves.sort(key=fitness)
        best = wolves[0]

        # "movement" toward best solution (simplified)
        for i in range(1, len(wolves)):
            wolves[i] = best[:]

    # execute best schedule
    time = 0
    for p in best:
        time = max(time, p.arrival)
        p.start = time
        p.completion = time + p.burst
        time = p.completion

    return best

def run_all(n):
    results = {}

    algorithms = [
        ("FIFO", fifo),
        ("Round Robin", lambda x: round_robin(x, 2)),
        ("Priority", priority_scheduling),
        ("GWO", gwo_schedule)
    ]

    for name, algo in algorithms:

        processes = generate_processes(n)
        processes = copy.deepcopy(processes)  

        completed = algo(processes)

        metrics = compute_metrics(completed)
        results[name] = metrics

    print(f"\n--- Results for {n} tasks ---")
    for k, v in results.items():
        print(f"{k}: AvgWait={v[0]:.2f}, AvgTurn={v[1]:.2f}, Throughput={v[2]:.2f}")
        
for size in [10, 50, 100, 500, 1000]:
    run_all(size)
