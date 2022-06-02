import json
import openmdao.api as om
import numpy as np
import io
import shapely.geometry as SG
import shapely.affinity as SA
import my_plt
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import colors
import matplotlib as mpl
import Param as P
import warnings
import tabulate

class Fit:
    def __init__(self, outputs = None, inputs = None):
        
        self.outputs = outputs # Params
        self.inputs = inputs
        
        self.comps = {} # Dictionary of Components with Output String ID as the key
        
        # Grid of points for OpenMDAO Structure MetaModel Comp
        self.X_vec = None
        self.X_grid = None
        self.Y_grid = None
        
    def setup(self):
        self.comps = {}
        for (i, out) in enumerate(self.outputs):
            comp = P.ParamComp(om.MetaModelStructuredComp, method='scipy_cubic', extrapolate=True)
            
            for (j,ip) in enumerate(self.inputs):
                comp.add_input(ip.strID, 1.0, training_data=np.array(self.X_vec[j]))
        
            comp.add_output(out.name, 1.0, training_data = np.array(self.Y_grid[i]))
        
            self.comps[out.strID] = comp
    
    def attach_outputs(self):
        for out in self.outputs:
            comp = self.comps[out.strID]
            out.setDependency(comp, depArgs = self.inputs)
            out.dep=True
    
    def plot(self):
        from openmdao.visualization.meta_model_viewer.meta_model_visualization import view_metamodel
        view_metamodel(self.comp, 50, 5007, True)
    
    def load(source, params):
        if isinstance(source, io.TextIOBase): # Check for File-Like Object
            surr_meta = json.load(source)
        else:
            surr_meta = source
        
        # Dictionary to convert from JSON names to object attributes
        surr_dict_reqd = {"Outputs":"outputs","Inputs":"inputs"}
        surr_dict_opt = {"X_vec":"X_vec", "X_grid":"X_grid", "Y_grid":"Y_grid"}
        surr_dict_opt_set = set(surr_dict_opt)

        # Make a new Fit
        s = Fit()
        s_ = surr_meta

        # Set Identifying Parameters
        for key in surr_dict_reqd:
            if (key not in s_) or (not s_[key]):
                raise Exception(f"{key} field required to import fit")
            
            if key == "Outputs" or key == "Inputs":
                # Get params from second argument
                val = [params[x] for x in s_[key]]
            else:
                val = s_[key]
                
            setattr(s, surr_dict_reqd[key], val)
        
        surr_meta_keys = surr_dict_opt_set.intersection(set(s_))
        for key in surr_meta_keys:
            setattr(s, surr_dict_opt[key], s_[key])

        return s
    
    def __str__(self):
        return  str(self.__class__) + '\n'+ '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))
                 
    def __getitem__(self, out):
        c = self.comps[out] 
        return c                                  
    
class Boundary:
    def __init__(self):
        # BASE
        self.N = None
        self.args = []
        self.boundary_points = []
        self.lb = []
        self.ub = []
        self.mean = []
        
        # OPTIONS     
        self.grid_resolution = 50
        self.grid_buffer = 0.2
        self.smooth_distance = 0.1
        self.constraint_padding = 0.0
        
        # Internal
        self.polygon = None
        self.box = None
        self.eff_len = None
        
        self.polygon_smooth = None
        
        self.vec_X = None
        self.vec_Y = None
        self.grid_X = None
        self.grid_Y = None
        self.grid_D = None

        self.distance_comp = None

    
    def load(source, params):
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
            
            if key == "Args":
                # Get params from second argument
                val = [params[x] for x in s_[key]]
            else:
                val = s_[key]
            setattr(s, dict_reqd[key],val)
        
        meta_keys = dict_opt_set.intersection(set(s_))
        for key in meta_keys:
            setattr(s, dict_opt[key], s_[key])

        return s
    
    def scale(self, geom):
        shifted = SA.translate(geom, xoff = -self.cent.x, yoff = -self.cent.y)
        scaled = SA.scale(shifted, xfact = 1/self.x_scale, yfact = 1/self.y_scale, origin=(0,0,0))
        return scaled
    
    def unscale(self, geom):
        scaled = SA.scale(geom, xfact = self.x_scale, yfact = self.y_scale, origin=(0,0,0))
        shifted = SA.translate(scaled, xoff = self.cent.x, yoff = self.cent.y)
        return shifted
    
    def setup_geometry(self):
        self.polygon = SG.Polygon(self.boundary_points)
        self.box = self.polygon.bounds
        self.eff_len = eff_length(self.box)

        self.cent = self.polygon.centroid
        self.x_scale = self.box[2] - self.box[0]
        self.y_scale = self.box[3] - self.box[1]

        polygon_scaled = self.scale(self.polygon)        

        poly_erode_scaled = polygon_scaled.buffer(-self.smooth_distance)
        hd = polygon_scaled.hausdorff_distance(poly_erode_scaled)
        poly_dilate_scaled = poly_erode_scaled.buffer(hd)
        self.polygon_smooth_scaled = poly_dilate_scaled
        
        self.polygon_smooth = self.unscale(self.polygon_smooth_scaled)
    
    def setup_grid(self):
        N = self.grid_resolution
        
        poly_outer_scaled = self.polygon_smooth_scaled.buffer(self.grid_buffer)
        poly_outer = self.unscale(poly_outer_scaled)
        pbox = poly_outer.bounds

        (self.vec_X, self.vec_Y, self.grid_X, self.grid_Y) = box_grid(pbox, N)
    
    def sample(self):  
        def poly_dist(polygon, X, Y):
            poly_ext = polygon.exterior
            D = np.zeros(np.shape(X))
            for i in range(len(X)):
                for j in range(len(X[i])):
                    x = X[i][j]
                    y = Y[i][j]
                    p = self.scale(SG.Point(x,y))
                    d = poly_ext.distance(p)
                    if polygon.contains(p):
                        d = -d
                    D[i][j] = d
            return D
        
        self.grid_D = poly_dist(self.polygon_smooth_scaled, self.grid_X, self.grid_Y)
    
    def setup_comp(self):
        comp = om.MetaModelStructuredComp(method='scipy_cubic', extrapolate=True)
        
        vecs = [self.vec_X, self.vec_Y] # Later add third dimension if necessary
        for (j,p) in enumerate(self.args):
            comp.add_input(p.strID, 1.0, training_data=np.array(vecs[j]))
        
        outname = "distance"
        comp.add_output(outname, 1.0, training_data = np.array(self.grid_D))
        comp.add_constraint("distance", lower=None, upper=self.constraint_padding)
        
        self.distance_comp = comp
        
    def setup(self):
        self.setup_geometry()
        self.setup_grid()
        self.sample()
        self.setup_comp()
    
    def attach_args(self):
        # Only modify bounds if boundary is more restrictive
        
        for (i,p) in enumerate(self.args):
            if self.lb:
                if (not p.lb) or (p.lb < self.lb[i]):
                    p.lb = self.lb[i]
            if self.ub:
                if (not p.ub) or (p.ub > self.ub[i]):
                    p.ub = self.ub[i]
            
        
    def add_to_system(self, sys, name="boundary"):
        if isinstance(sys, P.ParamSystem):
            kwargs = {"params":[p.strID for p in self.args]}
        else:
            kwargs = {}
            
        if not self.distance_comp:
            raise Exception("Please run boundary.setup() before adding to system")
        
        sys.add_subsystem(name, self.distance_comp, **kwargs)

    def plot3D(self, ax=None, fig = None):
        if not fig:
            fig = plt.figure()
        if not ax:
            ax = plt.axes(projection='3d')
        
        # Define Colormap
        divnorm = colors.TwoSlopeNorm(vmin=np.min(self.grid_D), vcenter=0, vmax=np.max(self.grid_D))
        
        ax.plot_surface(self.grid_X, self.grid_Y, self.grid_D, alpha=0.5, cmap = cm.coolwarm, norm=divnorm)
        
        x,y = self.polygon.exterior.xy
        ax.plot(x,y, linestyle='--', linewidth=1, color="r")
        
        x,y = self.polygon_smooth.exterior.xy
        ax.plot(x,y, linestyle='-', linewidth=2, color="r")
        

        ax.set_xlabel(self.args[0].latex())
        ax.set_ylabel(self.args[1].latex())
        ax.set_zlabel("Distance") 
        
        return (fig, ax)
    
    def plot2D(self, ax=None, fig = None):
        if not fig:
            fig = plt.figure()
        if not ax:
            ax = plt.axes()

        x,y = self.polygon.exterior.xy
        ax.plot(x,y, '--r', linewidth = 1)
        
        x,y = self.polygon_smooth.exterior.xy
        ax.plot(x,y, '-r', linewidth = 2)
        
        ax.set_xlabel(self.args[0].latex())
        ax.set_ylabel(self.args[1].latex())
        
        return (fig, ax)

def eff_length(box):
    dx = box[2] - box[0]
    dy = box[3] - box[1]
    eff_length = (np.abs(dx) + np.abs(dy))/2
    return eff_length

def box_grid(box, N):
    X_pnts = np.linspace(box[0], box[2], N)
    Y_pnts = np.linspace(box[1], box[3], N)

    (X, Y) = np.meshgrid(X_pnts, Y_pnts)
    return (X_pnts, Y_pnts, X,Y)
    
        
class ComponentData:
    def __init__(self, component=None, make=None, model=None, sku=None, desc=None, data=P.ParamValSet()):
        self.component = component
        self.make = make
        self.model = model
        self.sku = sku
        self.desc = desc
        self.data = data
    
    def __str__(self):
        return  str(self.__class__) + '\n'+ '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))
    
    def approx_eq(self, o):
        test_fields = ["component", "make", "model", "sku"]
        for f in test_fields:
            if getattr(self, f) != getattr(o, f):
                return False
        return True
    
class ComponentDataSet(set):
    def __init__(self, arg={}):
        for cd in arg:
            if not isinstance(cd, ComponentData):
                raise TypeError("All elements in component data set must be ComponentData object")
        super().__init__(arg)
        
    def __getitem__(self, arg):
        if isinstance(arg, int):
            return self.sorted()[arg]
        else:
            found = []
            for p in self:
                if p.sku == arg:
                    return p
                if p.component == arg:
                    found.append(p)
            if len(found) == 1:
                return found[0]
            elif len(found) > 1:
                return found
            else:
                raise KeyError("Parameter not found")
    
    def __add__(self, arg):
        if isinstance(arg, type(self)):
            # In place add
            return self.union(arg)
        elif isinstance(arg, ComponentData):
            self.add(arg)
            return self
        else:
            raise Exception("+ Operator only supported for ComponentDataSet and ComponentData")
    
    def approx_contains(self, o):
        for c in self:
            if c.approx_eq(o):
                return True
        return False
    
    @property
    def data(self):
        data = P.ParamValSet()
        for c in self:
            data.update(c.data)
        
        return data
            
    def union(self, arg):
        cls = type(self)
        if isinstance(arg, cls):
            u_set = super().union(arg)
            u_pset = cls(u_set)
            return u_pset
        else:
            raise TypeError("Can only add other ComponentDataSets")
            
    def sorted(self, key=lambda p: (p.component, p.make, p.model), **kwargs):
        return sorted(self, key=key, **kwargs)
            
    def __str__(self):
        self_sorted = self.sorted()
        tab_data = [(x.component, x.make, x.model, x.sku, x.desc) for x in self_sorted]
        tab = tabulate.tabulate(tab_data, headers=["Component", "Make", "Model", "SKU", "Description"])
        return str(self.__class__) + "\n" + str(tab)
    
    def latex(self):
        self_sorted = self.sorted()
        tab_data = [(x.component, x.make, x.model, x.sku, x.desc) for x in self_sorted]
        tab = tabulate.tabulate(tab_data, headers=["Component", "Make", "Model", "SKU", "Description"], tablefmt="latex_raw")
        return str(tab)
    
    def splitBy(self, splitter="component"):
        splitter_vals = [getattr(x, splitter) for x in self]
        unique_splitters = set(splitter_vals)
        
        splitted_cds = {}
        for s in unique_splitters:
            elems = [x for x in self if getattr(x, splitter) == s]
            splitted_cds[s] = ComponentDataSet(elems)
        
        return splitted_cds
        
    def load(self, source):
        if isinstance(source, (list, tuple)):
            cd_meta = source
        else:
            cd_meta = json.load(source)
        
        # Dictionary to convert from JSON names to object attributes
        comp_dict_opt = {"Component":"component", "Make":"make", "Model":"model", "SKU":"sku", "Description":"desc", "Data":"data"}
        comp_dict_opt_set = set(comp_dict_opt)

        for cd_ in cd_meta:

            # Make a new ComponentData with new ParamValSet.
            # I think __init__ doesn't re-construct the default data = P.ParamValSet each time
            
            cd = ComponentData(data=P.ParamValSet())
            self.add(cd) # Add new param to set
            
            comp_meta_keys = comp_dict_opt_set.intersection(set(cd_))
            for key in comp_meta_keys:
                cd_key = comp_dict_opt[key]
                if key == "Data":
                    # Update ComponentData's ParamValSet
                    cd.data.load(cd_[key])
                else:
                    setattr(cd, cd_key, cd_[key])

        return self
    
            
    def plot(self, vals, ax=None, fig=None, annotate=True, scatter_kwargs = {'facecolors':'none', "edgecolors":'b', "label":"Component Data"}):
        if not fig:
            fig = plt.figure()
        if not ax:
            ax = plt.axes()
        
        pnts = []
        axes_labels = []
        for cd in self:
            pnt = []
            for v in vals:
                if isinstance(v, str):
                    pv = cd.data[v]
                else:
                    pv = v.get_compatible(cd.data)
                    
                pnt.append(pv.val)
                if len(axes_labels) < len(vals):
                    axes_labels.append(pv.latex())
            pnts.append(pnt)

        ax.scatter(*zip(*pnts), **scatter_kwargs)
        
        if annotate:
            ax.legend()
            ax.set_xlabel(axes_labels[0])
            ax.set_ylabel(axes_labels[1])            
        
        return (fig, ax)

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
    
    def load(source, params):
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
                    f = Fit.load(val, params)
                    val = f
                elif key == "Boundary":
                    b = Boundary.load(val, params)
                    val = b
                elif key == "ComponentData":
                    cd = ComponentDataSet()
                    cd = cd.load(val)
                    val = cd                
                setattr(s, dict_opt[key], val)
            
            S[s.comp_name] = s
        return S
    
    @property
    def inputs(self):
        if self.fits:
            return self.fits.inputs
        else:
            warnings.warn("Fits not yet defined")
    
    @property
    def outputs(self):
        if self.fits:
            return self.fits.outputs
        else:
            warnings.warn("Fits not yet defined")
    
    def plot_boundary_3D(self, fig = None, ax=None):
        if not fig:
            fig = plt.figure(0)
        if not ax:
            ax = plt.axes(projection='3d')
            
        (fig,ax) = self.boundary.plot3D(fig=fig,ax=ax)
        fig.suptitle(f"Surrogate: {self.comp_name}")
        if self.comp_data:
            skwargs = {'facecolors':'none', "edgecolors":'gray', "label":"Component Data"}
            self.comp_data.plot(self.boundary.args, ax=ax, fig=fig, annotate=False, scatter_kwargs=skwargs)
        
        return (fig, ax)

    def plot_boundary_2D(self, fig = None, ax=None):
        (fig,ax) = self.boundary.plot2D(fig=fig,ax=ax)
        fig.suptitle(f"Surrogate: {self.comp_name}")
        if self.comp_data:
            self.comp_data.plot(self.boundary.args, ax=ax, fig=fig, annotate=False)
            
        return (fig,ax)