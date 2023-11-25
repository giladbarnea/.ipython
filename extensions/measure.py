"""
%load_ext measure
measurements=%measure import rich
measurements=%measure sleep(5) -s from time import sleep -n 5,10
measurements.plot()
measurements[:5].plot()
"""
import re
from collections import namedtuple
from copy import deepcopy
from dataclasses import dataclass, field
from time import perf_counter_ns
from timeit import timeit
from typing import ForwardRef, Iterable, Union

from IPython.core.magic import register_line_cell_magic

try:
    from rich.traceback import install

    install(show_locals=True)
except ModuleNotFoundError:
    pass

HDIV = "\033[90m|\033[0m"


def get_justification(*items):
    return max(map(lambda x: len(str(x)), [*items]))


def fmt_num(num, dec=2) -> str:
    if dec == 0:
        return f"{num:,}"
    return f"{num:,.{dec}f}"


def human_ns(ns, dec=2) -> str:
    sec = ns / 1_000_000_000
    if sec >= 1:
        return f"{fmt_num(sec, dec)} sec"
    ms = ns / 1_000_000
    if ms >= 1:
        return f"{fmt_num(ms, dec)} ms"
    microsec = ns / 1_000
    if microsec >= 0.1:
        return f"{fmt_num(microsec, dec)} μs"
    return f"{fmt_num(ns, dec)} ns"


Most = namedtuple("Most", ["ns", "index"])


@dataclass
class Run:
    nanosec: int
    deviation: int


@dataclass
class Stats:
    runs: list[Run] = field(default_factory=list)
    variance = 0
    stdev = 0
    slowest = None
    fastest = None
    nanosec_sum = None
    nanosec_avg = None

    def calculate(
        self, stmt: str, *, setup: str, timer, run_count: int, nanosec_sum: int, nanosec_avg: float, _globals=None
    ):
        for duration in (
            # 10_000_000_000,
            5_000_000_000,  # 10 s to 1 ms
            1_000_000_000,
            500_000_000,
            100_000_000,
            50_000_000,
            10_000_000,
            5_000_000,
            1_000_000,
        ):
            if nanosec_sum < duration:
                repetitions = duration // nanosec_sum
                break
        else:
            print(
                f"Not calculating variance because one repetition one have taken {human_ns(nanosec_sum)} (cap is 10 seconds)"
            )
            return None

        print(f"Calculating variance among {repetitions:,} repetitions...")

        self.nanosec_sum = nanosec_sum
        self.nanosec_avg = nanosec_avg
        deviation_sum = 0

        for i in range(repetitions):
            nanosec = timeit(stmt, setup=setup, timer=timer, number=run_count, globals=_globals)

            if (self.fastest and nanosec < self.fastest.ns) or not self.fastest:
                self.fastest = Most(nanosec, i)
            if (self.slowest and nanosec > self.slowest.ns) or not self.slowest:
                self.slowest = Most(nanosec, i)

            deviation = (nanosec - nanosec_avg) ** 2
            deviation_sum += deviation
            self.runs.append(Run(nanosec, deviation))

        self.variance = int(deviation_sum / (run_count - 1))
        self.stdev = int(self.variance**0.5)

    def __repr__(self) -> str:
        stdev_percent = fmt_num((self.stdev * 100) / self.nanosec_avg)
        slowest_percent = fmt_num((self.slowest.ns * 100) / self.nanosec_avg)
        fastest_percent = fmt_num((self.fastest.ns * 100) / self.nanosec_avg)
        avg_human = human_ns(self.nanosec_avg)
        sum_human = human_ns(self.nanosec_sum)
        stdev_human = human_ns(self.stdev)
        slowest_human = human_ns(self.slowest.ns)
        fastest_human = human_ns(self.fastest.ns)
        col_1_rjust = get_justification(avg_human, sum_human, stdev_human, slowest_human, fastest_human)
        col_2_rjust = get_justification(stdev_percent, slowest_percent, fastest_percent)
        col_3_rjust = get_justification(self.slowest.index, self.fastest.index)
        return "\n".join(
            [
                f"Avg      {HDIV} {avg_human.rjust(col_1_rjust)} {HDIV}",
                f"Total    {HDIV} {sum_human.rjust(col_1_rjust)} {HDIV}",
                f"Std. Dev {HDIV} {stdev_human.rjust(col_1_rjust)} {HDIV} {stdev_percent.rjust(col_2_rjust)}%",
                f"Slowest  {HDIV} {slowest_human.rjust(col_1_rjust)} {HDIV} {slowest_percent.rjust(col_2_rjust)}% {HDIV} Run # {str(self.slowest.index).rjust(col_3_rjust)}",
                f"Fastest  {HDIV} {fastest_human.rjust(col_1_rjust)} {HDIV} {fastest_percent.rjust(col_2_rjust)}% {HDIV} Run # {str(self.fastest.index).rjust(col_3_rjust)}",
            ]
        )

    def __bool__(self):
        return bool(self.variance)


class Measurement:
    """Runs the statment `run_count` times."""

    def __init__(
        self, stmt: str, setup="pass", timer=perf_counter_ns, run_count: int = 1_000_000, _globals=None, variance=False
    ):
        self.stmt = stmt
        self.run_count = run_count
        print(f"\nTiming {run_count:,} runs...", end="")
        self.nanosec_sum = timeit(stmt, setup=setup, timer=timer, number=run_count, globals=_globals)
        self.nanosec_avg = self.nanosec_sum / self.run_count
        self.stats = None

        if variance:
            self.stats = Stats()
            if run_count == 1:
                return

            self.stats.calculate(
                stmt,
                setup=setup,
                timer=timer,
                run_count=run_count,
                nanosec_sum=self.nanosec_sum,
                nanosec_avg=self.nanosec_avg,
                _globals=_globals,
            )

    def __repr__(self):
        if self.stats:
            return f"\n\t" + "\n\t".join(str(self.stats).split("\n"))
        else:
            human_sum = human_ns(self.nanosec_sum)
            human_avg = human_ns(self.nanosec_avg)
            return f"Avg: {human_avg} {HDIV} Total: {human_sum}"


class Experiment:
    """Runs len(runs_counts) measurements"""

    def __init__(self, stmt: str, runs_counts: Iterable[int], setup="pass", _globals=None, variance=False):
        self.measurements: dict[str, Measurement] = {}
        self.runs_counts: list[int] = []
        self.nanosec_avgs: list[int] = []
        self.stats_arr: list[Stats] = []
        self.variance = variance
        for run_count in runs_counts:
            key = f"{run_count:,}"
            measurement = Measurement(stmt, setup=setup, run_count=run_count, _globals=_globals, variance=variance)
            self.runs_counts.append(measurement.run_count)
            self.nanosec_avgs.append(measurement.nanosec_avg)
            if variance:
                self.stats_arr.append(measurement.stats)
            self.measurements[key] = measurement

    def __repr__(self) -> str:
        lines = []
        ljust = get_justification(*self.measurements.keys()) + 5
        for key, measurement in self.measurements.items():
            measurement_str = str(measurement)
            if measurement_str.startswith("\n"):
                runs = f"{key} runs".ljust(ljust)
            else:
                runs = f"{key} runs {HDIV}"
            lines.append(f"{runs} {measurement_str}")
        return "\n".join(lines)

    def __getitem__(self, slice_or_index: Union[int, slice]) -> ForwardRef("Experiment"):
        if isinstance(slice_or_index, (str, int)):
            if isinstance(slice_or_index, str):
                key = slice_or_index
            else:
                key = list(self.measurements.keys())[slice_or_index]
            measurement = self.measurements[key]
            return measurement

        else:
            copy = deepcopy(self)
            copy.measurements.clear()
            # slice
            for key in list(self.measurements.keys())[slice_or_index]:
                copy.measurements[key] = self.measurements[key]
            copy.runs_counts = self.runs_counts[slice_or_index]
            copy.nanosec_avgs = self.nanosec_avgs[slice_or_index]
            copy.stats_arr = self.stats_arr[slice_or_index]
            return copy

    def plot(self):
        try:
            ipython.enable_matplotlib()
        except ModuleNotFoundError as e:
            print(
                "[WARNING][measure.py] ModuleNotFoundError when ipython.enable_matplotlib(). Experiment.plot() will not work."
            )
            return False
        from matplotlib import pyplot as plt

        plt.xlabel("Repeats")
        plt.ylabel("Nanoseconds")
        runs_pretty = list(map(lambda n: f"{n:,}", self.runs_counts))
        return plt.plot(runs_pretty, self.nanosec_avgs)


from pdbpp import break_on_exc


def load_ipython_extension(ipython):
    print("Loaded extension measure")

    @register_line_cell_magic("measure")
    @break_on_exc
    def linemagic(line: str, cell: str = None):
        if not line and not cell:
            return
        if cell:
            print("Not implemented yet! cell: ", cell)
            return
        stmt = []
        variance = False
        setup = "pass"
        runs_counts = (*range(1, 11), 100, 1000, 10_000, 100_000)
        i = -1
        while i + 1 < len(line):
            i += 1
            char = line[i]
            if char != "-":
                stmt.append(char)
                continue

            if line[i : i + 10] == "--variance":
                variance = True
                i = i + 9
                continue

            if line[i + 2] != " ":
                arg_value_start_idx = i + 2
            else:
                arg_value_start_idx = i + 3

            # ** Number of runs
            if line[i + 1] == "n":
                if match := re.search(r"[ -]", line[arg_value_start_idx:]):
                    arg_value_stop_idx = match.span()[0] + arg_value_start_idx
                    runs_counts = [int(number) for number in line[arg_value_start_idx:arg_value_stop_idx].split(",")]
                    i = arg_value_stop_idx - 1
                    continue
                runs_counts = [int(number) for number in line[arg_value_start_idx:].split(",")]
                break

            # ** Setup
            if line[i + 1] == "s":
                arg_value_stop_idx = line[arg_value_start_idx:].rfind("-")  # -1 if not found
                if arg_value_stop_idx != -1:
                    arg_value_stop_idx += arg_value_start_idx
                    setup = line[arg_value_start_idx:arg_value_stop_idx]
                    i = arg_value_stop_idx - 1
                    continue
                setup = line[arg_value_start_idx:].strip()
                break

        measures = Experiment(stmt="".join(stmt), runs_counts=runs_counts, setup=setup, variance=variance)
        print("\n" + str(measures))
        return measures
