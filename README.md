# Python-Based CPU Scheduling Simulator

## Project overview
This project simulates classical CPU scheduling algorithms and visualizes process execution using Gantt charts. It also compares waiting time, turnaround time, and throughput.

## Algorithms
- First Come First Serve (FCFS), non-preemptive
- Shortest Job First (SJF), non-preemptive
- Round Robin (RR), with a configurable time quantum (default 2)
- Priority Scheduling, non-preemptive; a smaller priority number means higher priority
- Dynamic Workload Adaptation: processes with arrival time <= 3 are placed in an SJF batch; processes with arrival time > 3 are placed in an RR batch. The SJF batch is scheduled first, followed by the RR batch.

## Technologies
- Python
- Pandas
- Matplotlib

## Requirements
Python 3.9 or newer is recommended.

## Installation
```bash
python -m pip install -r requirements.txt
```

## Run
```bash
python cpu_scheduling.py
```

Enter the number of processes, then enter each process's arrival time, burst time, and priority. Choose one algorithm or compare all five.

## Metrics
- Completion time
- Turnaround time = completion time - arrival time
- Waiting time = turnaround time - burst time
- Average waiting time
- Average turnaround time
- Throughput (processes per time unit)

## Notes about the dynamic rule
The accompanying project paper describes the dynamic method as SJF for the early-arriving batch and Round Robin for later arrivals, with a time quantum of 2. This implementation interprets the threshold as arrival time <= 3 for the SJF batch and arrival time > 3 for the RR batch, then runs the batches sequentially. That is a clear, runnable interpretation of the paper's pseudocode; it may differ from the original Google Colab implementation if its exact code used a different integration strategy.

## Files
- `cpu_scheduling.py` — simulator source code
- `requirements.txt` — Python dependencies
- `CPU_Scheduling_Report.pdf` — optional project report, if you add it yourself
