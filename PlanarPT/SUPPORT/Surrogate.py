import json
import openmdao.api as om
import numpy as np
import io

class Fit:
    def __init__(self, outputs = None, inputs = None):
        self.outputs = outputs
        self.inputs = inputs
        
        self._outputs_name = None
        self._inputs_name = None
        
        self.comps = {} # Dictionary of Components with Output String ID as the key
        
        # Grid of points for OpenMDAO Structure MetaModel Comp
        self.X_vec = None
        self.X_grid = None
        self.Y_grid = None
        
    def setup(self):
        self.comps = {}
        for (i, out) in enumerate(self._outputs_name):
            strid = self.outputs[i]
            comp = om.MetaModelStructuredComp(method='scipy_cubic', extrapolate=True)
            
            for (j,ip) in enumerate(self.inputs):
                comp.add_input(ip, 1.0, training_data=np.array(self.X_vec[j]))
        
            comp.add_output(out, 1.0, training_data = np.array(self.Y_grid[i]))
        
            self.comps[strid] = comp
    
    def plot(self):
        from openmdao.visualization.meta_model_viewer.meta_model_visualization import view_metamodel
        view_metamodel(self.comp, 50, 5007, True)
    
    def load(source):
        if isinstance(source, io.TextIOBase): # Check for File-Like Object
            surr_meta = json.load(source)
        else:
            surr_meta = source
        
        # Dictionary to convert from JSON names to object attributes
        surr_dict_reqd = {"Outputs":"outputs","Inputs":"inputs", "OutputsName":"_outputs_name", "InputsName":"_inputs_name"}
        surr_dict_opt = {"X_vec":"X_vec", "X_grid":"X_grid", "Y_grid":"Y_grid"}
        surr_dict_opt_set = set(surr_dict_opt)

        # Make a new Fit
        s = Fit()
        s_ = surr_meta

        # Set Identifying Parameters
        for key in surr_dict_reqd:
            if (key not in s_) or (not s_[key]):
                raise Exception(f"{key} field required to import fit")
            setattr(s, surr_dict_reqd[key], s_[key])
        
        surr_meta_keys = surr_dict_opt_set.intersection(set(s_))
        for key in surr_meta_keys:
            setattr(s, surr_dict_opt[key], s_[key])

        return s
    
    def __str__(self):
        return  str(self.__class__) + '\n'+ '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))
                 
    def __getitem__(self, out):
        try:
            c = self.comps[out] 
        except:
            # Try searching by output name
            out_i = self._outputs_name.index(out)
            str_id = self.outputs[out_i]
            c = self.comps[str_id]
        
        return c                                  
    
class Boundary:
    def __init__(self):
        self.N = None
        self.args = []
        self.boundary_points = []
        self.lb = []
        self.ub = []
        self.mean = []
        
        self.distance_func = None
        self.distance_comp = None

    
    def load(source):
        if isinstance(source, io.TextIOBase): # Check for File-Like Object
            meta = json.load(source)
        else:
            meta = source
        
        # Dictionary to convert from JSON names to object attributes
        dict_reqd = {"BoundaryPoints":"boundary_points", "Args":"args", "N":"N"}
        dict_opt = {"X_lb":"lb", "X_ub":"ub", "X_mean":"mean"}
        dict_opt_set = set(dict_opt)

        # Make a new Boundary
        s = Boundary()
        s_ = meta

        # Set Identifying Parameters
        for key in dict_reqd:
            if (key not in s_) or (not s_[key]):
                raise Exception(f"{key} field required to import fit")
            setattr(s, dict_reqd[key], s_[key])
        
        meta_keys = dict_opt_set.intersection(set(s_))
        for key in meta_keys:
            setattr(s, dict_opt[key], s_[key])

        return s
        
    def setup(self):
        #TODO: Make Boundary Component and Function
        pass
    
class DistToBoundaryComp(om.ExplicitComponent):
    def setup(self):
        pass
    def compute(self, inputs, outputs):
        pass
    def compute_partials(self, inputs, partials):
        pass
    def dist_to_bnd(poly_data, point):
        pass
        
class ComponentData:
    def __init__(self):
        pass
    
    def load(source):
        pass
    
    def setup(self):
        pass
        
class Surrogate:
    def __init__(self, comp_name=""):
        self.comp_name = comp_name
        
        self.fits = None
        self.boundary = None
        self.comp_data = None
    
    def setup(self):
        
        # Set up all components that can be setup
        props = vars(self)
        for (k,v) in props.items():
            if hasattr(v, 'setup'):
                v.setup()
    
    def load(source):
        if isinstance(source, io.TextIOBase): # Check for File-Like Object
            surr_meta = json.load(source)
        else:
            surr_meta = source
        
        # Dictionary to convert from JSON names to object attributes
        dict_reqd = {"ComponentName":"comp_name"}
        dict_opt = {"Fits":"fits","Boundary":"boundary", "ComponentData":"comp_data"}
        dict_opt_set = set(dict_opt)

        S = {} # Output dict of surrogates
        for s_ in surr_meta:

            # Make a new Surrogate
            s = Surrogate()

            # Set Identifying Parameters
            for key in dict_reqd:
                if (key not in s_) or (not s_[key]):
                    raise Exception(f"{key} field required to import surrogate")
                setattr(s, dict_reqd[key], s_[key])
            
            # Surrogate Components
            surr_meta_keys = dict_opt_set.intersection(set(s_))
            for key in surr_meta_keys:
                val = s_[key]
                if key == "Fits":
                    f = Fit.load(val)
                    val = f
                elif key == "Boundary":
                    b = Boundary.load(val)
                    val = b
                elif key == "ComponentData":
                    cd = ComponentData.load(val)
                    val = cd
                
                    # TODO: Finish ComponentData Case
                
                setattr(s, dict_opt[key], val)
            
            S[s.comp_name] = s
        return S

            