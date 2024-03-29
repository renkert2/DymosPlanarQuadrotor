# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 11:32:38 2022

@author: renkert2
"""
import openmdao.api as om
import openmdao.core.component as omcomp
import numpy as np
import tabulate

from GraphTools_Phil_V2.OpenMDAO import Param as P

import SUPPORT_FUNCTIONS.support_funcs as SF

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
    
    @property
    def val(self):
        raise Exception("val property not implemented in Constraint superclass")
        pass
    
    def satisfied(self):
        v = self.val
        if hasattr(v, "__iter__"):
            v_max = SF.iterapply(max, v)
            v_min = SF.iterapply(min, v)
        else:
            v_max = v
            v_min = v
            
        if self.lb and (v_min < self.lb):
            return False
        elif self.ub and (v_max > self.ub):
            return False
        else:
            return True
    
    def props(self):
        base_props = ["name", "active", "lb", "ub", "ref", "ref0"]
        
        prop_dict = {}
        for p in base_props:
            prop_dict[p] = getattr(self, p)
        
        return prop_dict
            
           
class ConstraintParam(Constraint):
    # Constraint defined by a calculated Parameter in the model    
    # UNUTILIZED!!!    

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
    
    def props(self):
        prop_dict = super().props()
        
        for bound in ["lb", "ub"]:
            val = getattr(self, f"_{bound}")
            if isinstance(val, P.Param):
                prop_dict[f"{bound}_param"] = val.strID
        
        return prop_dict
    
class TrajConstraint(Constraint):
    def __init__(self, traj_convar=None, convar_output_path=None, **kwargs):
        Constraint.__init__(self,**kwargs)
        self._traj_convar = traj_convar # Name of trajectory variable to constrain
        
        if not convar_output_path:
            convar_output_path = traj_convar
        
        self._convar_output_path = convar_output_path
        self._traj = None
    
    def add_to_traj(self, traj):
        self._traj = traj
        if self.active:
            convars = SF.iterize(self._traj_convar)
            for (phase_name, phase) in traj._phases.items():
                for v in convars:
                    if callable(v):
                        v = v(phase_name)
                    phase.add_path_constraint(name=v, lower=self.lb, upper=self.ub, ref=self.ref, ref0=self.ref0)
    
    def props(self):
        prop_dict = super().props()
        prop_dict["traj_convar"] = self._traj_convar
        prop_dict["convar_output_path"] = self._convar_output_path
        
        return prop_dict 
    
    @property
    def val(self):
        val=[]
        convar_outs = SF.iterize(self._convar_output_path)
        for outname in convar_outs:
            # Get from all phases
            _val = np.array([])
            for phase in self._traj._phases.values():
                v = phase.get_val(outname) 
                _val = np.append(_val,v)
        val.append(_val)
        return val
              
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
            
    @property
    def val(self):
        convars = SF.iterize(self._convar)
        vals = []
        for v in convars:
            vals.append(self.get_val(v))
        return vals
    
    def props(self):
        prop_dict = Constraint.props(self)
        
        base_props = ["_mdl_name", "_connections", "_params", "_convar"]
        for p in base_props:
            prop_dict[p] = getattr(self, p)
        
        return prop_dict
    
class TrajConstraintGroup(TrajConstraint, om.Group):
    def __init__(self, **kwargs):
        TrajConstraint.__init__(self, **kwargs)
        om.Group.__init__(self)
        
        self._mdl_name = None # Name of the group in the system
        self._connections = None # Contains tuples with from,to connections for each component in the group
        self._params = None # String IDs of required parameters
        self._convar = None # Variable within each component to constrain
        
        self._traj_path = "traj"
        self._traj_phases = []
        self._traj_name_prefix = "timeseries"
        self._traj_connections = None # Contains tuples with from,to connections in the trajectory. From must be in traj.
        self._comp_class = None # Class of component to be constructed for each phase
        self._comp_class_args = [] # Arguments passed to _comp_class constructor
        self._comp_class_kwargs = dict() # KW Arguments passed to _comp_class constructor
        self._comps = dict() # dictionary of name:component pairs

        self._grid_nn = []
        
    def add_to_system(self, sys, traj):
        self._mdl_name = "traj_constraint__" + self.name
        self._traj_phases = list(traj._phases.keys())
        
        for phase in self._traj_phases:
            # Get Transcription Data
            tx = traj._phases[phase].options["transcription"]
            nn = tx.grid_data.num_nodes
            self._grid_nn.append(nn)
            
            # Define Components
            c = self._comp_class(*self._comp_class_args, **self._comp_class_kwargs)
            name = f"comp_{phase}"
            self._comps[name] = c
            self.add_subsystem(name, c)
            
        # Add group to the system
        sys.add_subsystem(self._mdl_name, self, params=self._params)
        self.add_traj_connections(sys)

    def add_traj_connections(self, sys):
        for conn in self._traj_connections:
            comp_names = self._comps.keys()
            for p,cn in zip(self._traj_phases, comp_names):
                from_var = ".".join([self._traj_path, p, self._traj_name_prefix, conn[0]])
                to_var = ".".join([self._mdl_name, cn, conn[1]])
                sys.connect(from_var, to_var)  
                
    @property
    def val(self):
        raise Exception("Val not yet excepted")
        convars = SF.iterize(self._convar)
        vals = []
        for v in convars:
            vals.append(self.get_val(v))

        return vals.fget(self)
                
    def props(self):
        prop_dict = TrajConstraint.props(self)
        
        base_props = ["_mdl_name", "_connections", "_params", "_convar"]
        for p in base_props:
            prop_dict[p] = getattr(self, p)
        
        prop_dict["traj_connections"] = self._traj_connections
        
        return prop_dict
    
    def setup(self):
        comps = self._comps.values()
        
        for c,p in zip(comps, self._traj_phases):
            self.setup_comp(c,p)
        
        if self.active:
            convars = SF.iterize(self._convar)
            for v in convars:
                for c in comps:
                    c.add_constraint(v, lower=self.lb, upper=self.ub, ref0=self.ref0, ref=self.ref)
                
        om.Group.setup(self)
            
    def setup_comp(self, c, p):
        raise Exception("setup_comp must be implemented in subclasses")
            
    
    
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
        raise KeyError("Constraint not found")
        
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
    
# class BatteryCurrent(TrajConstraintComp, om.AddSubtractComp):
#     def __init__(self):
#         # TODO: This will eventually need to accomodate all the phases in a trajectory
#         om.AddSubtractComp.__init__(self)
#         TrajConstraintComp.__init__(self, name="battery_current", ub=0, ref=100)
#         self._params = tuple()
#         self._traj_connections = (("outputs:PT_a2", "i__Battery"),("parameters:MaxDischarge__Battery", "MaxDischarge__Battery"))
#         self._convar = "con"
        
#     def setup(self):
#         self.add_equation('con', input_names = ['i__Battery', 'MaxDischarge__Battery'], scaling_factors=[1,-1], vec_size = self._grid_nn[0], desc="Battery Current Constraint")
#         om.AddSubtractComp.setup(self)
#         TrajConstraintComp.setup(self)
        
class BatteryCurrent(TrajConstraintGroup):
    def __init__(self):
        # TODO: This will eventually need to accomodate all the phases in a trajectory
        TrajConstraintGroup.__init__(self, name="battery_current", ub=0, ref=100)
        self._params = tuple()
        self._traj_connections = (("outputs:PT_a2", "i__Battery"),("parameters:MaxDischarge__Battery", "MaxDischarge__Battery"))
        self._convar = "con"
        self._comp_class = om.AddSubtractComp
        
    def setup_comp(self, comp, phase_name):
        # Function specified in subclasses, used to setup each copy of _comp_class in TrajConstraintGroup.setup()
        comp.add_equation('con', input_names = ['i__Battery', 'MaxDischarge__Battery'], scaling_factors=[1,-1], vec_size = self._grid_nn[0], desc="Battery Current Constraint")
        # comp.setup()
        
class InverterCurrent(TrajConstraint):
    def __init__(self):
        TrajConstraint.__init__(self, traj_convar=["PT.a3", "PT.a5"], convar_output_path=["timeseries.outputs:PT_a3", "timeseries.outputs:PT_a5"])
        self.name = "inverter_current"
        self._lb = None
        self._ub = 80 # Based off of a reasonably large inverter, suggested by Dr. Alleyne
        self._ref = 80
        self._ref0 = None
        
class InputRate(Constraint):
    def __init__(self):
        TrajConstraint.__init__(self, traj_convar=["CTRL.u_1_delta", "CTRL.u_2_delta"], convar_output_path=["timeseries.outputs:PT_a3", "timeseries.outputs:PT_a5"])
        self.name = "inverter_current"
        self._lb = None
        self._ub = 80 # Based off of a reasonably large inverter, suggested by Dr. Alleyne
        self._ref = 80
        self._ref0 = None
    
