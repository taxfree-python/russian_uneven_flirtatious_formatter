import os
import timeit


def run_pure_ruff(file):
    os.system(f"ruff check {file}")


def run_custom_ruff(file):
    os.system(f"python3 src/format.py {file} 0")


test_files = ["benchmark_data/1.py", "benchmark_data/2.py"]

with open("result.txt", "w") as result_file:
    for file in test_files:
        time_taken_pure = timeit.timeit(
            lambda: run_pure_ruff(file), number=100)
        result_file.write(f"Pure Ruff の {file} に対する平均実行時間: {
                          time_taken_pure / 100:.6f} 秒\n")

    for file in test_files:
        time_taken_custom = timeit.timeit(
            lambda: run_custom_ruff(file), number=100)
        result_file.write(f"Custom Ruff (format.py) の {file} に対する平均実行時間: {
                          time_taken_custom / 100:.6f} 秒\n")
