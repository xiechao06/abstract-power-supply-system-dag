#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import time
from typing import NamedTuple

import tqdm
from loguru import logger
from tabulate import tabulate

from apssm.devices.load import Load
from benchmarks.build_graph import build_graph

logger.disable("apssm")


class RunResult(NamedTuple):
    runs: int
    nodes: int
    edges: int
    destinations: int
    total_in_ms: int
    avg_in_ms: int


runs = 100


def main():
    run_results: list[RunResult] = []
    for level1, level2 in ((50, 50), (100, 100)):
        graph = build_graph(level1, level2)
        destinations: list[Load] = []
        # collect 100 destinations
        for d in graph.devices.values():
            if isinstance(d, Load):
                destinations.append(d)
                if len(destinations) == 100:
                    break
        start = time()
        for _ in tqdm.trange(runs):
            graph.find_passages((d.name, 0) for d in destinations)
        total = round((time() - start) * 1e3)

        run_results.append(
            RunResult(
                runs,
                len(graph.devices),
                len(graph.edges),
                len(destinations),
                total,
                round(total / runs),
            )
        )

    t = tabulate(
        run_results,
        headers=["runs", "nodes", "edges", "dest", "total(ms)", "avg(ms)"],
    )
    print(t)


if __name__ == "__main__":
    main()
