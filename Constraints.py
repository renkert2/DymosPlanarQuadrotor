# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 11:32:38 2022

@author: renkert2
"""
import openmdao.api as om
import openmdao.core.component as omcomp
import SUPPORT_FUNCTIONS.support_funcs as SF
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
        
        val = SF.scalarize(val)
        return val
    
    @property
    def ub(self):
        if isinstance(self._ub, P.Param):
            if self._param_prob:
                self._param_prob.run_model()
            val = self._ub.val
        else:
            val = self._ub
            
        val = SF.scalarize(val)
        return val
    
class TrajConstraint(Constraint):
    def __init__(self, traj_convar=None, **kwargs):
        Constraint.__init__(self,**kwargs)
        self._traj_convar = traj_convar # Name of trajectory variable to constrain
    
    def add_to_traj(self, traj):
        if self.active:
            convars = SF.iterize(self._traj_convar)
            for phase in traj._phases.values():
                for v in convars:
                    phase.add_path_constraint(name=v, lower=self.lb, upper=self.ub, ref=self.ref, ref0=self.ref0)
              
class ConstraintComp(Constraint, omcomp.Component):
    def __init__(self, **kwargs):
        Constraint.__init__(self, **kwargs)
        self._mdl_name = None # Name of the component in the system
        self._connections = None # Contains tuples with from,to connections
        self._params = None # String IDs of required parameters
        self._convar = None # Variable within component to constrain
        
    def setup(self):     
        if self.active:
            convars = SF.iterize(self._convar)
            for v in convars:
                self.add_constraint(v, lower=self.lb, upper=self.ub, ref0=self.ref0, ref=self.ref)
    
    def add_to_system(self, sys):
        self._mdl_name = "constraint__" + self.name
        sys.add_subsystem(self._mdl_name, self, params=self._params)
        
        self.add_connections(sys)
    
    def add_connections(self, sys):
        for c in self._connections:
            from_var = c[0]
            to_var = self._mdl_name + "." + c[1]
            sys.connect(from_var, to_var)        
    
class TrajConstraintComp(TrajConstraint, ConstraintComp):
    def __init__(self, **kwargs):
        TrajConstraint.__init__(self)
        ConstraintComp.__init__(self, **kwargs)
        self._traj_path = "traj"
        self._traj_phases = []
        self._traj_name_prefix = "timeseries"
        self._traj_connections = None # Contains tuples with from,to connections in the trajectory. From must be in traj.

        self._grid_nn = []
        
    def add_to_system(self, sys, traj):
        self._mdl_name = "traj_constraint__" + self.name
        sys.add_subsystem(self._mdl_name, self, params=self._params)

        self._traj_phases = list(traj._phases.keys())
        
        self._traj_timeseries_size = []
        for phase in self._traj_phases:
            tx = traj._phases[phase].options["transcription"]
            nn = tx.grid_data.num_nodes
            self._grid_nn.append(nn)
        
        if self._connections: # Check if there are any normal, non-trajectory connections
            ConstraintComp.add_connections(self, sys)
        
        self.add_traj_connections(sys)

    def add_traj_connections(self, sys):
        for c in self._traj_connections:
            for p in self._traj_phases:
                from_var = ".".join([self._traj_path, p, self._traj_name_prefix, c[0]])
                to_var = ".".join([self._mdl_name, c[1]])
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
        
# class BatteryCurrent(ConstraintParam, TrajConstraint):
#     def __init__(self):
#         TrajConstraint.__init__(self, traj_convar="PT.a2")
#         self.name = "battery_current"
#         self._ref=100
#     def set_bounds(self, pg):
#         ConstraintParam.set_bounds(self, lb=None, ub=pg._params["MaxDischarge__Battery"], param_group=pg)
    
class BatteryCurrent(TrajConstraintComp, om.AddSubtractComp):
    def __init__(self):
        # TODO: This will eventually need to accomodate all the phases in a trajectory
        om.AddSubtractComp.__init__(self)
        TrajConstraintComp.__init__(self, name="battery_current", ub=0, ref=100)
        self._params = tuple()
        self._traj_connections = (("outputs:PT_a2", "i__Battery"),("parameters:MaxDischarge__Battery", "MaxDischarge__Battery"))
        self._convar = "con"
        
    def setup(self):
        self.add_equation('con', input_names = ['i__Battery', 'MaxDischarge__Battery'], scaling_factors=[1,-1], vec_size = self._grid_nn[0], desc="Battery Current Constraint")
        om.AddSubtractComp.setup(self)
        TrajConstraintComp.setup(self)
        
class InverterCurrent(TrajConstraint):
    def __init__(self):
        TrajConstraint.__init__(self, traj_convar=["PT.a3", "PT.a5"])
        self.name = "inverter_current"
        self._lb = None
        self._ub = 20
        self._ref = 20
        self._ref0 = None
    
