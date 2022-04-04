# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 11:32:38 2022

@author: renkert2
"""
import openmdao.api as om
import openmdao.core.component as omcomp
import tabulate
import Param as P

class Constraint:
    # Constraint Base
    def __init__(self, name=None, lb=None, ub=None, ref=None, ref0=None):
        self.name = name
        self.active = True
        self._lb = lb
        self._ub = ub
        self._ref = ref
        self._ref0 = ref0
        
    @property
    def lb(self):
        return self._lb
    
    @property
    def ub(self):
        return self._ub
    
    @property
    def ref(self):
        return self._ref
    
    @property
    def ref0(self):
        return self._ref0
           
class ConstraintParam(Constraint):
    # Constraint defined by a calculated Parameter in the model        

    def set_bounds(self, lb=None, ub=None, param_group=None):
        for parg in [lb, ub]:
            if parg and not (isinstance(parg, float) or isinstance(parg, P.Param)):
                raise Exception("Upper and lower bounds must be defined by Parameters or floats")
        
        self._lb = lb
        self._ub = ub
        self._param_group = param_group
        
        self._param_prob = None
        if self._param_group:
            self._param_prob = om.Problem(model=self._param_group)
            self._param_prob.setup()
    
    @property
    def lb(self):
        if isinstance(self._lb, P.Param):
            if self._param_prob:
                self._param_prob.run_model()
            val = self._lb.val
        else:
            val = self._lb
        
        val = ConstraintParam.scalarize(val)
        return val
    
    @property
    def ub(self):
        if isinstance(self._ub, P.Param):
            if self._param_prob:
                self._param_prob.run_model()
            val = self._ub.val
        else:
            val = self._ub
            
        val = ConstraintParam.scalarize(val)
        return val
    
    def scalarize(val):
        if hasattr(val, "__len__"): # Check if array valued
            if len(val) == 1:
                val = val[0] # Get first element in list
            else:
                raise Exception("Scalar values required for upper and lower bounds")
        return val
    
class TrajConstraint(Constraint):
    def __init__(self, traj_convar=None, **kwargs):
        Constraint.__init__(self,**kwargs)
        self._traj_convar = traj_convar # Name of trajectory variable to constrain
    
    def add_to_traj(self, traj):
        if self.active:
            for phase in traj._phases.values():
                phase.add_path_constraint(name=self._traj_convar, lower=self.lb, upper=self.ub, ref=self.ref, ref0=self.ref0)
              
class ConstraintComp(Constraint, omcomp.Component):
    def __init__(self, **kwargs):
        Constraint.__init__(self, **kwargs)
        self._mdl_name = None # Name of the component in the system
        self._connections = None # Contains tuples with from,to connections
        self._params = None # String IDs of required parameters
        self._convar = None # Variable within component to constrain
        
    def setup(self):     
        if self.active:
            self.add_constraint(self._convar, lower=self.lb, upper=self.ub, ref0=self.ref0, ref=self.ref)
    
    def add_to_system(self, sys):
        self._mdl_name = "constraint__" + self.name
        sys.add_subsystem(self._mdl_name, self, params=self._params)
        
        for c in self._connections:
            from_var = c[0]
            to_var = self._mdl_name + "." + c[1]
            sys.connect(from_var, to_var)        
        
class ConstraintSet(set):
    def __init__(self, arg=set()):
        for p in arg:
            if not isinstance(p, Constraint):
                raise TypeError("All elements in constraint set must be constraints")
        super().__init__(arg)
        
    def add(self, elem):
        if isinstance(elem, ConstraintSet):
            for c in elem:
                super().add(c)
        elif isinstance(elem, Constraint):
            super().add(elem)
        else:
            raise Exception("Can only add ConstraintSets or constraints")
    
    def __getitem__(self, arg):
        for c in self:
            if c.name == arg:
                return c
        raise KeyError("Parameter not found")
        
    def __str__(self):
        self_sorted = sorted(self, key=lambda c:c.name)
        tab_data = [(x.name, x.active) for x in self_sorted]
        tab = tabulate.tabulate(tab_data, headers=["Name", "Active"])
        return str(self.__class__) + "\n" + str(tab)
        
### Individual Constraints ###       
class ThrustRatio(ConstraintComp, om.ExplicitComponent):
    def __init__(self):
        om.ExplicitComponent.__init__(self)
        ConstraintComp.__init__(self, name="thrust_ratio", lb=1.2, ref0=1, ref=3)
        self._params = ("HoverThrust__System",)
        self._connections = (("static.y1", "TMax"),)
        self._convar = "TR"
        
    def setup(self):
        self.add_input('HoverThrust__System', val=1, desc='mass')
        self.add_input('TMax', val=1, desc='Maximum thrust')
        
        self.add_output('TR', desc="Thrust Ratio")
    
        self.declare_partials('*', '*', method='exact')
        
        ConstraintComp.setup(self)
    
    def compute(self, inputs, outputs):
        ht = inputs['HoverThrust__System']
        TMax = inputs["TMax"]
        outputs["TR"] = TMax / ht
    def compute_partials(self, inputs, partials):
        ht = inputs['HoverThrust__System']
        TMax = inputs["TMax"]
        partials["TR", "HoverThrust__System"] = -TMax/(ht**2)
        partials["TR", "TMax"] = 1/(ht)
        
class BatteryCurrent(ConstraintParam, TrajConstraint):
    def __init__(self):
        TrajConstraint.__init__(self, traj_convar="PT.a2")
        self.name = "battery_current"
        self._ref=100
    def set_bounds(self, pg):
        ConstraintParam.set_bounds(self, lb=None, ub=pg._params["MaxDischarge__Battery"], param_group=pg)
