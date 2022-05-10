# -*- coding: utf-8 -*-
"""
Created on Tue May 10 09:26:07 2022

@author: renkert2
"""
class _Counter_SUPER:
    def __init__(self):
        self._fevals = 0
    
    @property
    def fevals(self):
        return self._fevals
    
    @fevals.setter
    def fevals(self, val):
        raise Exception("Property is protected")
        
    def prop_str(self):
        out = f"Function Evaluations: {self.fevals}"
        return out

class Counter(_Counter_SUPER):
    def increment(self, **kwargs):
        for k,v in kwargs.items():
            self.__dict__["_"+k] += v
    
    def reset(self):
        self._fevals = 0
    
    def state(self):
        return CounterState(self)
    
    def __str__(self):
        out = "---Counter---\n"
        out += self.prop_str() + "\n"
        return out

class CounterState(_Counter_SUPER):
    def __init__(self, parent):
        self.__dict__ = parent.__dict__.copy()
        
    def __str__(self):
        out = "---Counter State---\n"
        out += self.prop_str() + "\n"
        return out


if __name__ == "__main__":
    # Quick Test
    counter = Counter()
    
    counter.increment(fevals=10)
    counter.increment(fevals=5)
    state_1 = counter.state()
    print(counter)
    
    counter.reset()
    state_2 = counter.state()
    print(counter)
    
    print(state_1)
    print(state_2)