# Python-Based CPU Scheduling Simulator

## Project Overview
This project implements a Python-based simulator to study and compare classical CPU scheduling algorithms. It visualizes process execution using Gantt charts and compares scheduling performance.

## Algorithms Implemented
- First Come First Serve (FCFS)
- Shortest Job First (SJF)
- Round Robin (RR)
- Priority Scheduling
- Dynamic Workload Adaptation

## Technologies Used
- Python
- Pandas
- Matplotlib
- Google Colab

## Dynamic Workload Adaptation
The proposed approach uses Shortest Job First (SJF) for processes arriving at or before time 3 and Round Robin (RR) for processes arriving after time 3, using a time quantum of 2.

## Performance Metrics
- Waiting Time
- Turnaround Time
- Completion Time
- Average Waiting Time
- Average Turnaround Time

## Features
- Process input using arrival time, burst time, and priority
- Gantt chart visualization
- Performance comparison between scheduling algorithms
- Dynamic scheduling demonstration

## How to Run
1. Install Python and the required libraries.
2. Download the Python source code from this repository.
3. Install dependencies using `pip install -r requirements.txt`.
4. Run the program using `python cpu_scheduling.py`.

## Project Report
The project report contains the design, algorithms, implementation methodology, results, and future improvements.
