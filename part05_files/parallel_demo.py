"""Uruchamiaj jako skrypt: python part05_files/parallel_demo.py [--benchmark]."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import multiprocessing as mp
import os
import platform
from statistics import median
from time import perf_counter

import numpy as np

from workers import count_batch, count_row, reciprocal, sum_squares


def examples():
    context = mp.get_context("spawn")
    rows = [[1, 4, 5, 8, 9], [0, 2, 3, 9, 9], [4, 4, 8, 8, 6]]
    expected = [count_row(row) for row in rows]
    with context.Pool(2) as pool:
        # apply czeka na każdy wynik: ten zapis NIE rozdziela pracy równolegle.
        applied = [pool.apply(count_row, (row, 4, 8)) for row in rows]
        mapped = pool.map(partial(count_row, minimum=4, maximum=8), rows)
        starred = pool.starmap(count_row, [(row, 4, 8) for row in rows])
        pending = [pool.apply_async(count_row, (row, 4, 8)) for row in rows]
        asynchronous = [result.get(timeout=20) for result in pending]
        map_async = pool.map_async(count_row, rows).get(timeout=20)
        star_async = pool.starmap_async(
            count_row, [(row, 4, 8) for row in rows]
        ).get(timeout=20)
    assert applied == mapped == starred == asynchronous == expected
    assert map_async == star_async == expected
    print("Pool: apply/map/starmap oraz warianty async:", expected)

    with ProcessPoolExecutor(max_workers=2, mp_context=context) as executor:
        calculated = list(executor.map(count_row, rows, chunksize=2))
        assert calculated == expected
        future = executor.submit(reciprocal, 0)
        try:
            future.result(timeout=20)
        except ZeroDivisionError:
            print("Future.result(): odebrano oczekiwany ZeroDivisionError")
        else:
            raise AssertionError("Oczekiwano wyjątku z procesu")
    print("ProcessPoolExecutor: wyniki zgodne z wersją sekwencyjną")


def measured(function, expected, repeats=3):
    samples = []
    for _ in range(repeats):
        start = perf_counter()
        result = function()
        elapsed = perf_counter() - start
        assert result == expected
        samples.append(elapsed)
    return median(samples)


def benchmark():
    context = mp.get_context("spawn")
    workers = min(2, os.cpu_count() or 1)
    array = np.random.default_rng(100).integers(0, 10, size=(20_000, 5))
    rows = array.tolist()  # przygotowanie danych poza pomiarem
    expected = [count_row(row) for row in rows]
    batches = [rows[start:start + 500] for start in range(0, len(rows), 500)]

    def pool_rows(chunksize):
        with context.Pool(workers) as pool:
            return pool.map(count_row, rows, chunksize=chunksize)

    def pool_batches():
        with context.Pool(workers) as pool:
            return [value for batch in pool.map(count_batch, batches) for value in batch]

    print(f"Python {platform.python_version()}, NumPy {np.__version__}")
    print(f"{platform.system()} {platform.machine()}, CPU logiczne={os.cpu_count()}")
    print(f"Dane={array.shape}, procesy={workers}, start=spawn, mediana 3 prób")
    print("Czas procesów obejmuje start, serializację, IPC i zamknięcie puli.")
    variants = {
        "pętla Python": lambda: [count_row(row) for row in rows],
        "NumPy": lambda: ((array >= 4) & (array <= 8)).sum(axis=1).tolist(),
        "Pool chunksize=1": lambda: pool_rows(1),
        "Pool chunksize=500": lambda: pool_rows(500),
        "Pool: paczki po 500": pool_batches,
    }
    for name, function in variants.items():
        print(f"{name:24s} {measured(function, expected):.6f} s")

    limits = [500_000] * 8
    cpu_expected = [sum_squares(limit) for limit in limits]

    def cpu_parallel():
        with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
            return list(executor.map(sum_squares, limits))

    print("Większe zadania CPU: 8 x 500 000 iteracji; bez gwarancji przyspieszenia")
    print("sekwencyjnie:", f"{measured(lambda: [sum_squares(n) for n in limits], cpu_expected):.6f} s")
    print("procesy:     ", f"{measured(cpu_parallel, cpu_expected):.6f} s")


if __name__ == "__main__":
    mp.freeze_support()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    arguments = parser.parse_args()
    examples()
    if arguments.benchmark:
        benchmark()
