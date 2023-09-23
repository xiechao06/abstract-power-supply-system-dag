#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import namedtuple
from time import time

from tabulate import tabulate
from tqdm import tqdm

from benchmarks.build_graph import build_graph

runs = 100

Result = namedtuple("Result", ["runs", "nodes", "edges", "total", "avg"])


def main():
    results: list[Result] = []
    for level1, level2 in ((50, 50), (100, 100)):
        graph = build_graph(level1, level2)
        start = time()
        for _ in tqdm(range(runs)):
            graph.gen_forest()
        total = round((time() - start) * 1e3)
        results.append(
            Result(
                runs, len(graph.devices), len(graph.edges), total, round(total / runs)
            )
        )
    t = tabulate(
        results,
        headers=["runs", "nodes", "edges", "total(ms)", "avg(ms)"],
    )
    print(t)


if __name__ == "__main__":
    main()
