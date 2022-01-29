# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:25:31 2022

@author: renkert2
"""
import time
import functools


def simple_timer(func, output = True):
    @functools.wraps(func)
    def timer_func(*args, **kwargs):
        tic = time.perf_counter()
        out = func(*args, **kwargs)
        toc = time.perf_counter()
        run_time = toc-tic
        if output:
            print(f"Funcion ran in {run_time:0.4f} seconds")
        return (run_time, out)
    return timer_func