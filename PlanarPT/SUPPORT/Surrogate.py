import json
import openmdao.api as om
import numpy as np

class Surrogate:
    def __init__(self, output = None, inputs = None):
        self.output = output
        self.inputs = inputs
        
        self._output_name = None
        self._inputs_name = None
        
        self.comp = None
        
        # Grid of points for OpenMDAO Structure MetaModel Comp
        self.X_vec = None
        self.X_grid = None
        self.Y_grid = None
        
    def setup(self):
        comp = om.MetaModelStructuredComp(method='scipy_cubic', extrapolate=True)
        for (i,ip) in enumerate(self.inputs):
            comp.add_input(ip, 1.0, training_data=np.array(self.X_vec[i]))
        
        comp.add_output(self._output_name, 1.0, training_data = np.array(self.Y_grid))
        
        self.comp = comp
        
        return comp
    
    def plot(self):
        from openmdao.visualization.meta_model_viewer.meta_model_visualization import view_metamodel
        view_metamodel(self.comp, 50, 5007, True)
    
    def load(source):
        surr_meta = json.load(source)
        
        # Dictionary to convert from JSON names to object attributes
        surr_dict_reqd = {"Output":"output","Inputs":"inputs", "OutputName":"_output_name", "InputsName":"_inputs_name"}
        surr_dict_opt = {"X_vec":"X_vec", "X_grid":"X_grid", "Y_grid":"Y_grid"}
        surr_dict_opt_set = set(surr_dict_opt)

        S = {} # Output dict of surrogates
        for s_key in surr_meta:
            s_ = surr_meta[s_key]

            # Make a new Surrogate
            s = Surrogate()

            # Set Identifying Parameters
            for key in surr_dict_reqd:
                if (key not in s_) or (not s_[key]):
                    raise Exception(f"{key} field required to import surrogate")
                setattr(s, surr_dict_reqd[key], s_[key])
            
            surr_meta_keys = surr_dict_opt_set.intersection(set(s_))
            for key in surr_meta_keys:
                setattr(s, surr_dict_opt[key], s_[key])
            
            S[s_key] = s
        return S
    
    def __str__(self):
        return  str(self.__class__) + '\n'+ '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))
                                                      