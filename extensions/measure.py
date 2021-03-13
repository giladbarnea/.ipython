"""
%load_ext measure
ms=%measure import rich
ms.plot()
ms[:5].plot()
"""
from timeit import timeit
from typing import Union, ForwardRef

from IPython.core.magic import register_line_magic


class Measure:
    def __init__(self, stmt: str, number: int):
        self.stmt = stmt
        self.number = number
        self.sec_tot = timeit(stmt, number=number)
        self.sec_avg = self.sec_tot / number
        self.millisec_tot = self.sec_tot * 1_000
        self.millisec_avg = self.sec_avg * 1_000
        self.microsec_tot = self.sec_tot * 1_000_000
        self.microsec_avg = self.sec_avg * 1_000_000
        self.nanosec_tot = self.sec_tot * 1_000_000_000
        self.nanosec_avg = self.sec_avg * 1_000_000_000
    
    def __repr__(self):
        if self.sec_avg >= 1:
            measure_avg, measure_tot, unit = self.sec_avg, self.sec_tot, "seconds"
        elif self.millisec_avg >= 1:
            measure_avg, measure_tot, unit = self.millisec_avg, self.millisec_tot, "milliseconds"
        elif self.microsec_avg >= 0.1:  # 0.1 microsecond is better than 100 nanosecond
            measure_avg, measure_tot, unit = self.microsec_avg, self.microsec_tot, "μs (microseconds)"
        else:
            measure_avg, measure_tot, unit = self.nanosec_avg, self.nanosec_tot, "nanoseconds"
        
        measure_avg_pretty = f"{round(measure_avg, 3):,}"
        measaure_tot_pretty = f'{round(measure_tot, 2):,}'
        return f'{measure_avg_pretty} {unit} on average (total: {measaure_tot_pretty} over {self.number}) times'


class Measures:
    def __init__(self, line, times_arr):
        self.measures = {}
        self.numbers = []
        self.nanosec_avgs = []
        for times in times_arr:
            key = (6 - len(str(times))) * ' ' + f'{times:,}'
            measure = Measure(line, times)
            self.numbers.append(measure.number)
            self.nanosec_avgs.append(measure.nanosec_avg)
            self.measures[key] = measure
    
    def __getitem__(self, slice_or_index: Union[int, slice]) -> ForwardRef('Measures'):
        from copy import deepcopy
        copy = deepcopy(self)
        copy.measures.clear()
        if isinstance(slice_or_index, int):
            key = list(self.measures.keys())[slice_or_index]
            copy.measures[key] = self.measures[key]
        else:
            # slice
            for key in list(self.measures.keys())[slice_or_index]:
                copy.measures[key] = self.measures[key]
        # copy.measures = self.measures[slice_or_index]
        copy.numbers = self.numbers[slice_or_index]
        copy.nanosec_avgs = self.nanosec_avgs[slice_or_index]
        return copy
    
    def plot(self):
        from matplotlib import pyplot as plt
        plt.xlabel('Repeats')
        plt.ylabel('Nanoseconds')
        numbers_pretty = list(map(lambda n: f'{n:,}', self.numbers))
        return plt.plot(numbers_pretty, self.nanosec_avgs)


def load_ipython_extension(ipython):
    ipython.enable_matplotlib()
    
    @register_line_magic("measure")
    def linemagic(line):
        if not line:
            return
        measures = Measures(line, (*range(1, 11), 100, 1000, 10_000, 100_000))
        return measures
