"""
Python-Based Simulator for Dynamic Workload Adaptation and Performance Analysis
in Classical CPU Scheduling Algorithms.

Algorithms:
- First Come First Serve (FCFS), non-preemptive
- Shortest Job First (SJF), non-preemptive
- Round Robin (RR), configurable time quantum (default: 2)
- Priority Scheduling, non-preemptive; smaller priority number means higher priority
- Dynamic Workload Adaptation: arrival time <= 3 uses SJF; arrival time > 3 uses RR

Dependencies:
    pip install -r requirements.txt

Run:
    python cpu_scheduling.py
"""

from dataclasses import dataclass, field
from collections import deque
from copy import deepcopy
import math

import pandas as pd
import matplotlib.pyplot as plt


@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0
    remaining: int = field(init=False)

    def __post_init__(self):
        self.remaining = self.burst


def read_processes():
    """Read and validate process details from the terminal."""
    while True:
        try:
            n = int(input("Enter number of processes: ").strip())
            if n < 1:
                print("Enter at least one process.")
                continue
            break
        except ValueError:
            print("Please enter a whole number.")

    processes = []
    print("\nFor each process, enter arrival time, burst time, and priority.")
    print("Priority convention: a smaller number means a higher priority.")
    for i in range(n):
        pid = f"P{i + 1}"
        while True:
            try:
                arrival = int(input(f"{pid} arrival time (>= 0): ").strip())
                burst = int(input(f"{pid} burst time (> 0): ").strip())
                priority = int(input(f"{pid} priority (integer): ").strip())
                if arrival < 0 or burst <= 0:
                    print("Arrival must be >= 0 and burst must be > 0.")
                    continue
                processes.append(Process(pid, arrival, burst, priority))
                break
            except ValueError:
                print("Please enter whole numbers.")
    return processes


def fresh(processes):
    return [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]


def finalize_metrics(processes, completion):
    """Calculate waiting, turnaround, and response time from completion times."""
    rows = []
    for p in processes:
        ct = completion[p.pid]
        tat = ct - p.arrival
        wt = tat - p.burst
        rows.append({
            "Process": p.pid,
            "Arrival Time": p.arrival,
            "Burst Time": p.burst,
            "Priority": p.priority,
            "Completion Time": ct,
            "Turnaround Time": tat,
            "Waiting Time": wt,
        })
    return rows


def fcfs(processes):
    ps = sorted(fresh(processes), key=lambda p: (p.arrival, p.pid))
    time, completion, gantt = 0, {}, []
    for p in ps:
        if time < p.arrival:
            gantt.append(("Idle", time, p.arrival))
            time = p.arrival
        start = time
        time += p.burst
        gantt.append((p.pid, start, time))
        completion[p.pid] = time
    return finalize_metrics(ps, completion), gantt


def sjf(processes):
    ps = fresh(processes)
    time, completed, completion, gantt = 0, set(), {}, []
    while len(completed) < len(ps):
        ready = [p for p in ps if p.pid not in completed and p.arrival <= time]
        if not ready:
            next_arrival = min(p.arrival for p in ps if p.pid not in completed)
            if time < next_arrival:
                gantt.append(("Idle", time, next_arrival))
                time = next_arrival
            continue
        p = min(ready, key=lambda x: (x.burst, x.arrival, x.pid))
        start = time
        time += p.burst
        gantt.append((p.pid, start, time))
        completion[p.pid] = time
        completed.add(p.pid)
    return finalize_metrics(ps, completion), gantt


def priority_scheduling(processes):
    ps = fresh(processes)
    time, completed, completion, gantt = 0, set(), {}, []
    while len(completed) < len(ps):
        ready = [p for p in ps if p.pid not in completed and p.arrival <= time]
        if not ready:
            next_arrival = min(p.arrival for p in ps if p.pid not in completed)
            if time < next_arrival:
                gantt.append(("Idle", time, next_arrival))
                time = next_arrival
            continue
        p = min(ready, key=lambda x: (x.priority, x.arrival, x.pid))
        start = time
        time += p.burst
        gantt.append((p.pid, start, time))
        completion[p.pid] = time
        completed.add(p.pid)
    return finalize_metrics(ps, completion), gantt


def round_robin(processes, quantum=2):
    if quantum < 1:
        raise ValueError("Time quantum must be at least 1.")
    ps = sorted(fresh(processes), key=lambda p: (p.arrival, p.pid))
    by_pid = {p.pid: p for p in ps}
    remaining = {p.pid: p.burst for p in ps}
    completion, gantt = {}, []
    ready = deque()
    i, time = 0, 0

    while i < len(ps) or ready:
        if not ready:
            if i < len(ps) and time < ps[i].arrival:
                gantt.append(("Idle", time, ps[i].arrival))
                time = ps[i].arrival
            while i < len(ps) and ps[i].arrival <= time:
                ready.append(ps[i].pid)
                i += 1
        if not ready:
            continue

        pid = ready.popleft()
        p = by_pid[pid]
        run_for = min(quantum, remaining[pid])
        start = time
        time += run_for
        remaining[pid] -= run_for
        gantt.append((pid, start, time))

        while i < len(ps) and ps[i].arrival <= time:
            ready.append(ps[i].pid)
            i += 1

        if remaining[pid] > 0:
            ready.append(pid)
        else:
            completion[pid] = time

    return finalize_metrics(ps, completion), gantt


def dynamic_workload_adaptation(processes, quantum=2, threshold=3):
    """
    Implements the paper's batch-based rule:
    arrival time <= threshold: non-preemptive SJF
    arrival time > threshold: Round Robin.
    The SJF batch is scheduled first, followed by the RR batch.
    """
    early = [p for p in processes if p.arrival <= threshold]
    later = [p for p in processes if p.arrival > threshold]
    combined_rows = []
    combined_gantt = []
    time_offset = 0

    if early:
        rows, gantt = sjf(early)
        # Rebase the batch timeline so it follows the current timeline.
        first_start = min(start for _, start, _ in gantt)
        shift = time_offset - first_start
        combined_gantt.extend((pid, start + shift, end + shift) for pid, start, end in gantt)
        for row in rows:
            row = dict(row)
            row["Completion Time"] += shift
            combined_rows.append(row)
        time_offset = max(end for _, _, end in combined_gantt)

    if later:
        # All later-batch processes are ready when the RR phase begins.
        # Use phase-relative arrival times for scheduling, but preserve each
        # process's original arrival time when calculating final metrics.
        later_phase = [Process(p.pid, 0, p.burst, p.priority) for p in later]
        rows, gantt = round_robin(later_phase, quantum)
        shift = time_offset
        combined_gantt.extend((pid, start + shift, end + shift) for pid, start, end in gantt)
        original_by_pid = {p.pid: p for p in later}
        for row in rows:
            row = dict(row)
            row["Arrival Time"] = original_by_pid[row["Process"]].arrival
            row["Completion Time"] += shift
            combined_rows.append(row)

    # Recalculate metrics for the combined timeline. This also ensures
    # waiting time = turnaround time - original burst time.
    originals = {p.pid: p for p in processes}
    for row in combined_rows:
        p = originals[row["Process"]]
        row["Turnaround Time"] = row["Completion Time"] - p.arrival
        row["Waiting Time"] = row["Turnaround Time"] - p.burst

    combined_rows.sort(key=lambda r: (r["Arrival Time"], r["Process"]))
    return combined_rows, combined_gantt


def plot_gantt(gantt, title):
    """Plot a Gantt chart from (process, start, end) intervals."""
    fig, ax = plt.subplots(figsize=(10, 2.8))
    y = 10
    for pid, start, end in gantt:
        duration = end - start
        ax.barh(y, duration, left=start, height=5, edgecolor="black")
        label = pid if duration >= 1 else ""
        ax.text(start + duration / 2, y, label, ha="center", va="center", fontsize=9)
    ax.set_yticks([])
    ax.set_xlabel("Time units")
    ax.set_title(title)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.set_xlim(left=0)
    fig.tight_layout()
    plt.show()


def summarize(rows, gantt):
    df = pd.DataFrame(rows)
    avg_wait = df["Waiting Time"].mean()
    avg_tat = df["Turnaround Time"].mean()
    makespan = max((end for _, _, end in gantt), default=0)
    total_burst = df["Burst Time"].sum()
    throughput = len(df) / makespan if makespan > 0 else 0
    summary = {
        "Average Waiting Time": avg_wait,
        "Average Turnaround Time": avg_tat,
        "Throughput (processes/time unit)": throughput,
    }
    return df, summary


def main():
    print("=" * 66)
    print("CPU SCHEDULING SIMULATOR")
    print("=" * 66)
    processes = read_processes()

    while True:
        print("\nChoose a scheduling method:")
        print("1. First Come First Serve (FCFS)")
        print("2. Shortest Job First (SJF, non-preemptive)")
        print("3. Round Robin (RR)")
        print("4. Priority Scheduling (non-preemptive)")
        print("5. Dynamic Workload Adaptation (SJF then RR)")
        print("6. Compare all five methods")
        choice = input("Enter choice (1-6): ").strip()

        quantum = 2
        if choice in {"3", "5", "6"}:
            try:
                quantum = int(input("Enter Round Robin time quantum [default 2]: ").strip() or "2")
                if quantum < 1:
                    raise ValueError
            except ValueError:
                print("Invalid quantum. Using 2.")
                quantum = 2

        methods = {
            "1": ("FCFS", lambda: fcfs(processes)),
            "2": ("SJF", lambda: sjf(processes)),
            "3": ("Round Robin", lambda: round_robin(processes, quantum)),
            "4": ("Priority Scheduling", lambda: priority_scheduling(processes)),
            "5": ("Dynamic Workload Adaptation", lambda: dynamic_workload_adaptation(processes, quantum)),
        }

        if choice == "6":
            results = []
            for name, fn in [
                ("FCFS", lambda: fcfs(processes)),
                ("SJF", lambda: sjf(processes)),
                ("Round Robin", lambda: round_robin(processes, quantum)),
                ("Priority Scheduling", lambda: priority_scheduling(processes)),
                ("Dynamic Workload Adaptation", lambda: dynamic_workload_adaptation(processes, quantum)),
            ]:
                rows, gantt = fn()
                df, summary = summarize(rows, gantt)
                results.append({
                    "Algorithm": name,
                    "Average Waiting Time": summary["Average Waiting Time"],
                    "Average Turnaround Time": summary["Average Turnaround Time"],
                    "Throughput": summary["Throughput (processes/time unit)"],
                })
                plot_gantt(gantt, f"{name} Gantt Chart")
            comparison = pd.DataFrame(results)
            print("\nPerformance comparison:")
            print(comparison.round(2).to_string(index=False))
            ax = comparison.set_index("Algorithm")[["Average Waiting Time", "Average Turnaround Time"]].plot(
                kind="bar", figsize=(10, 5), rot=20
            )
            ax.set_ylabel("Time units")
            ax.set_title("Performance Comparison of Scheduling Algorithms")
            ax.grid(axis="y", linestyle="--", alpha=0.35)
            plt.tight_layout()
            plt.show()
            break

        if choice in methods:
            name, fn = methods[choice]
            rows, gantt = fn()
            df, summary = summarize(rows, gantt)
            print(f"\n{name} - per-process results:")
            print(df.round(2).to_string(index=False))
            print("\nPerformance summary:")
            for key, value in summary.items():
                print(f"{key}: {value:.2f}")
            plot_gantt(gantt, f"{name} Gantt Chart")
            break

        print("Please choose a number from 1 to 6.")


if __name__ == "__main__":
    main()
