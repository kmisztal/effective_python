"""Porównaj zwykłą listę przekazaną do wątku i procesu spawn."""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp

from workers import append_and_return


def main():
    thread_items = ["start"]
    with ThreadPoolExecutor(max_workers=1) as executor:
        thread_result = executor.submit(
            append_and_return, thread_items, "thread"
        ).result(timeout=20)
    assert thread_items == ["start", "thread"]
    assert thread_result is thread_items
    print("Wątek: lista główna =", thread_items)

    process_items = ["start"]
    with ProcessPoolExecutor(
        max_workers=1, mp_context=mp.get_context("spawn")
    ) as executor:
        process_result = executor.submit(
            append_and_return, process_items, "process"
        ).result(timeout=20)
    assert process_items == ["start"]
    assert process_result == ["start", "process"]
    assert process_result is not process_items
    print("Proces: lista główna =", process_items)
    print("Proces: odebrany wynik =", process_result)


if __name__ == "__main__":
    mp.freeze_support()
    main()
