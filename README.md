# Cloud_Task_Scheduling
Team members:
Cameron Bailey, Bryant Peden
---------------------------------------------------------------------------------------------------------------------------------
Efficient resource management is a critical function of operating systems. This project analyzes and compares the performance of two page replacement algorithms and one CPU scheduling algorithm.

The goal is to evaluate how different algorithms handle:
Memory management, CPU management, runtime, execution time,

We focus on measuring efficiency using:
Page faults (for memory algorithms) and 
Waiting time and turnaround time (for scheduling)
---------------------------------------------------------------------------------------------------------------------------------
Algorithms used in project:

FIFO (First In First Out) - The first process that arrives is the first one to be executed.

Grey Wolf Optimization - 

Priority Scheduling - a CPU scheduling algorithm where each process is assigned a priority value, and the 
scheduler always runs the process with the highest priority first. 

Round Robin Scheduling - a time-sharing CPU scheduling algorithm designed to give every process a fair chance to run. 
It cycles through all processes repeatedly—like taking turns.

This project uses synthetic datasets generated within the code:

task_sizes = [10, 50, 100, 500, 1000, 5000, 10000]
    results = run_experiments(task_sizes, trials=5)

To run this project, clone the repository with the following code:

git clone Cloud_Task_Scheduling / 
cd code / 
python main.py
