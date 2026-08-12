import gc
import json
import os
import random
import time
from collections import deque
from datetime import datetime

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class CustomLinkedFIFO:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, data):
        new_node = Node(data)
        if not self.tail:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def popleft(self):
        if not self.head:
            raise IndexError("pop from empty queue")
        data = self.head.data
        self.head = self.head.next
        if not self.head:
            self.tail = None
        return data

def log_telemetry(N, list_s, linked_s, deque_s):
    """
    Appends execution metrics to .benchmark_telemetry.json in the project root.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "N": N,
        "gc_disabled": True,
        "list_pop_0_s": round(list_s, 4),
        "linked_list_s": round(linked_s, 4),
        "deque_s": round(deque_s, 4)
    }
    log_file = ".benchmark_telemetry.json"
    data = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    data.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)

def run_benchmark(N=100000, trials=3):
    random.seed(42)
    print(f"--- Running Dilgorithm Queue Profiling (N={N:,}, GC Disabled) ---")

    # 1. Standard Python List
    gc.disable()
    list_times = []
    for _ in range(trials):
        lst = list(range(N))
        t0 = time.perf_counter()
        while lst:
            lst.pop(0)
        t1 = time.perf_counter()
        list_times.append(t1 - t0)
    gc.enable()
    list_median = sorted(list_times)[trials // 2]

    # 2. Custom Pointer-Based Linked FIFO
    gc.disable()
    linked_times = []
    for _ in range(trials):
        fifo = CustomLinkedFIFO()
        for i in range(N):
            fifo.append(i)
        t0 = time.perf_counter()
        while fifo.head:
            fifo.popleft()
        t1 = time.perf_counter()
        linked_times.append(t1 - t0)
    gc.enable()
    linked_median = sorted(linked_times)[trials // 2]

    # 3. collections.deque
    gc.disable()
    deque_times = []
    for _ in range(trials):
        deq = deque(range(N))
        t0 = time.perf_counter()
        while deq:
            deq.popleft()
        t1 = time.perf_counter()
        deque_times.append(t1 - t0)
    gc.enable()
    deque_median = sorted(deque_times)[trials // 2]

    # Persist metrics to .benchmark_telemetry.json
    log_telemetry(N, list_median, linked_median, deque_median)

    print(f"Standard list.pop(0):     {list_median:.3f} s (1.0x baseline)")
    print(f"CustomLinkedFIFO.popleft: {linked_median:.3f} s ({list_median/linked_median:.1f}x speedup)")
    print(f"collections.deque.popleft:{deque_median:.3f} s ({list_median/deque_median:.1f}x speedup)")

if __name__ == "__main__":
    run_benchmark()