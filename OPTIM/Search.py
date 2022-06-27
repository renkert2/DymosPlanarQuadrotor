# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:46:59 2022

@author: renkert2
"""
import numpy as np
import numbers
import itertools
import logging
import os
import openmdao.api as om
import pickle
import tabulate

import my_plt
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap

import SUPPORT_FUNCTIONS.init
import Surrogate
import Param as P
import Recorders as R

class _SearchOutput:
    def __init__(self, output_dir = "search_output"):
        self.output_dir = output_dir
        
        self.problem_recorder_path = self.make_path("search_cases.sql")
        self.iterations_path = self.make_path("search_iterations.pickle")
        self.result_path = self.make_path("search_result.pickle")

    def make_path(self, file):
        return os.path.join(self.output_dir, file)
        
class SearchRecorder(_SearchOutput):
    def __init__(self, *args, append_mode = False, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            os.mkdir(self.output_dir)
        except FileExistsError:
            logging.info(f"SearchRecorder directory {self.output_dir} already exists")
        
        problem_recorder = om.SqliteRecorder(self.problem_recorder_path, record_viewer_data=False)
        self.problem_recorder = problem_recorder
    
        if not append_mode:
            with open(self.iterations_path, 'wb') as f: # Create new file or overwrite existing
                pass
        
            with open(self.result_path, 'wb') as f: # Create new file or overwrite existing
                pass

    
    def add_prob(self, prob):
        prob.add_recorder(self.problem_recorder)
        prob.recording_options['record_desvars'] = True
        prob.recording_options['record_responses'] = True
        prob.recording_options['record_objectives'] = True
        prob.recording_options['record_constraints'] = True
        prob.recording_options['record_inputs'] = True
        prob.recording_options['includes'] = ["*"]
        
        return prob
    
    def record_iteration(self,iter_data):
        with open(self.iterations_path, 'ab') as f:
            pickle.dump(iter_data,f)
        
    def record_result(self, searcher_data):
        with open(self.result_path, 'wb') as f:
            pickle.dump(searcher_data, f)
            
        
    
class SearchReader(_SearchOutput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._case_reader = None
        self._problem_cases = None
        self._iterations = None
        self._result = None
        
    @property
    def result(self):
        if not self._result:
            with open(self.result_path, 'rb') as f:
                r = pickle.load(f)
            self._result = r
        return self._result
    
    @property
    def iterations(self):
        if not self._iterations:
            file = open(self.iterations_path, 'rb')
            self._iterations = []
            while True:
                try:
                    iteration = pickle.load(file)
                    self._iterations.append(iteration)
                except EOFError:
                    break
            file.close()
        return self._iterations
    
    @property
    def case_reader(self):
        if not self._case_reader:
            r = R.Reader(self.problem_recorder_path)
            self._case_reader = r
        return self._case_reader
    
    @property
    def problem_cases(self):
        pc = self.case_reader.get_cases("problem")
        return pc

    def make_path(self, file):
        return os.path.join(self.output_dir, file)
        
            
class SearchIteration:
    def __init__(self, iteration=None):
        self.iteration = iteration # Iteration Number
        
        self.config = None # Current Configuration
        self.obj_val = None # Resulting Objective Function
        self.func_evals = None # Function Evaluations Required
        self.msg = None # Output Message
        self.case_name = None # Name of problem recorder cases associated with this iteration
        
        self.opt_iter = None # Optimal iteration up to this point
    
    def __str__(self):
        out = []
        out.append(f"Iteration: {self.iteration}")
        out.append(f"Objective Function Value: {self.obj_val}")
        out.append(f"Message: {self.msg}")
        out.append(f"Configuration:\n{str(self.config)}")
        return "\n".join(out) + "\n"
    
class SearchIteration_GA(SearchIteration):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.solution = None
        self.solution_idx = None

class SearchResult:
    def __init__(self):
        self.iterations = None
        self.opt_iter = None
        self.termination_msg = None
        self.counter_state = None
        
        self.objective = None
        self.base_case_data = None
        self.config_searcher = None
        
    @property
    def sorted_iterations(self):
        return sorted(self.iterations, key=lambda x: (x.obj_val is None, x.obj_val))
    
    def __str__(self):
        out = "--- Search Result ---\n"
        out += f"Termination: {self.termination_msg}\n"
        out += f"Iterations: {len(self.iterations) -1}\n"
        out += "Counter: \n"
        cntr_str = "\t" + str(self.counter_state)
        out += '\t'.join(cntr_str.splitlines(True))
        out += "Optimal Iteration: \n"
        iter_str = "\t" + str(self.opt_iter) + "\t"
        out += '\t'.join(iter_str.splitlines(True))
        out += "\n"
        return out
    
    def plot(self, iter_slice=None):
        (fig, axes) = plt.subplots(2,1)
        iters = self.iterations
        if not iter_slice:
            iter_slice = slice(None,len(iters))
        i = range(len(iters))[iter_slice]
        self.config_searcher.plotDistances(fig=fig, ax=axes[1], iter_slice=iter_slice)

        ax = axes[0]
        
        obj_fun_vals = [x.obj_val for x in iters]
        ax.plot(i, obj_fun_vals, "-k", linewidth=1.5, label="Config. Obj. Value")
        
        opt_iter = self.opt_iter
        ax.plot(opt_iter.iteration, opt_iter.obj_val, '.r', markersize=10, label="Opt. Obj. Value")
        
        ax.set_ylabel("Obj. Value")
        ax.legend()
        
        return (fig, axes)
    
    def showTopComps(self, max_comps = 10):
        iters_sorted = self.sorted_iterations
        
        sorted_configs = [i.config for i in iters_sorted[:max_comps]]
        splitter_vals = [x.component for x in sorted_configs[0]]
        unique_splitters = set(splitter_vals)
        
        splitted_cds = {}
        for s in unique_splitters:
            elems = [x[s] for x in sorted_configs]
            splitted_cds[s] = elems
            tab_data = [(x.component, x.make, x.model, x.sku, x.desc) for x in elems]
            tab = tabulate.tabulate(tab_data, headers=["Component", "Make", "Model", "SKU", "Description"])
            print(tab)
            
        return splitted_cds
    
    def plotDesignSpace(self):
        out = self.config_searcher.plotDesignSpace(self.opt_iter.config, config_name="Opt. Config")        
        return out
    
    def plotCompHeatmat(self, stat_func=np.mean, stat_func_label="Mean Obj. Value"):
        cmap = LinearSegmentedColormap.from_list('gr', ['g', 'w', 'r'], N=256)
        def comp_stat_func(comp):
            obj_vals = []   
            for i,search_iter in enumerate(self.iterations):
                if search_iter.config.approx_contains(comp):
                    #logging.info(f"{comp.desc} found in iteration {i}")
                    val = search_iter.obj_val
                    if val:
                        obj_vals.append(val)
            if obj_vals:
                sf_val = stat_func(obj_vals)
                logging.info(f"{comp.desc}: StatFuncVal = {sf_val}")
                return sf_val
            else:
                return None
        
        figs = []
        for cn,cs in self.config_searcher.component_searchers.items():
            (fig, ax) = cs.plotCompDistances(ax=None, fig=None, dist_func=comp_stat_func, falloff_order = None, scatter_label=stat_func_label, scatter_edgecolors="0.8", scatter_cmap=cmap)
            figs.append(fig)
            
        return figs
    
class SearchResult_GA:
    def __init__(self):
        self.iterations = None
        self.opt_iter = None
        self.termination_msg = None
        self.counter_state = None
        
        self.objective = None
        self.base_case_data = None
        self.component_data = None
        self.gene_space = None
    
class Searcher:
    def __init__(self, config_searcher=None, prob=None, params=None, base_case=None, search_recorder=None, counter=None):
        self.config_searcher = config_searcher # SearchSurrogates, Dictionary 
        self.prob = prob # OpenMDAO Problem used to evaluate feasibility and objectives
        # TODO: We may want to separate this out into multiple problems to reduce total overhead.  We could have separate problems for 1) evaluating configuration feasibility and configuration distance metric and 2) evaluating final dynamic objective
        
        self.params = params   
        self.base_case = base_case # Case used to start evaluation of configuration
        
        self.search_recorder = search_recorder
        self.counter = counter
        
        self._dry_run = False
        self._dry_run_iterator = None
        self._dry_run_feval_iterator = None
        
        self._recover = False
        self._recover_case_reader = None
        self._recover_iters = None
        
    # def recover(self, case_reader, iters):
    #     #TODO: This isnt working right
    #     self._recover = True
    #     self._recover_case_reader = case_reader
    #     self._recover_iters = iters
        
    #     self.search(max_iter = iters[-1].iteration)
    
    def restore_result(self, search_recorder):
        # Output Search Result
        search_result = SearchResult()
        if self.base_case:
            search_result.base_case_data = R.CaseData(self.base_case)
        search_result.config_searcher = self.config_searcher
        search_result.config_searcher.component_searchers = None
        
        iters = search_recorder.iterations
        
        opt_obj_val = np.inf
        if self.counter:
            self.counter.reset()
            
        for i in iters:
            if self.counter:
                self.counter.increment(fevals=i.func_evals)
            if i.obj_val < opt_obj_val:
                opt_iter = i
                opt_obj_val = i.obj_val
            
        
        search_result.iterations = iters
        search_result.opt_iter = opt_iter
        search_result.termination_msg = "Recovered from Search Recorder"
        search_result.objective = self.prob.model.get_objectives()
        if self.counter:
            search_result.counter_state = self.counter.state()
        
        if self.search_recorder:
            self.search_recorder.record_result(search_result)
        
        print(search_result)
        return search_result
        
        
        
    def evaluate(self, config, base_case = None, case_name = None, iter_data=None):
        mod_params = []
        dep_cache = []
        driver_disp_cache = self.prob.driver.options["disp"]
        func_evals = 0
        
        if not iter_data:
            iter_data = SearchIteration()
        iter_data.config = config
        
        def cleanup():
            for (i,p) in enumerate(mod_params):
                p.dep = dep_cache[i]
            self.prob.driver.options["disp"] = driver_disp_cache
        
        # Substitute config param vals into Model
        logging.info(f"Evaluating Configuration: \n {str(config)}")
        
        self.prob.driver.options["disp"] = False
        if base_case:
            self.prob.load_case(base_case)
        
        pvals = config.data
        
        for p in self.params:
            pv = p.get_compatible(pvals)
            if pv:
                mod_params.append(p)
                dep_cache.append(p.dep)
                p.load_val(pv)
                p.dep=False
        
        # Run Feasibility Model
        self.prob.run_model()
        func_evals += 1
        
        feasible=True
        cons = self.prob.model.search_cons
        for c in cons:
            if not c.satisfied():
                msg = f"Configuration Infeasible: constraint {c.name} violated"
                logging.info(msg)
                feasible=False
                break

        if feasible:
            # Run Optimal Control Problem
            if self._dry_run:
                failed = False
                func_evals += next(self._dry_run_feval_iterator)
            
            elif self._recover:
                recovery_iter = None
                for ri in self._recover_iters:
                    if ri.iteration == iter_data.iteration:
                        recovery_iter = ri
                        break
                if recovery_iter:
                    # TODO: Check that the configurations and objectives match
                    
                    logging.info(f"Found recovery iteration {recovery_iter.iteration}")
                    
                    if recovery_iter.obj_val:
                        failed = False
                        case = self._recover_case_reader.get_case(recovery_iter.case_name)
                        self.prob.load_case(case)
                    else:
                        failed = True
                    func_evals = recovery_iter.func_evals
                    
            else:
                failed = self.prob.run_driver()
                func_evals += self.prob.driver.result['nfev']

                        
            if not failed:
                # Get Objective
                #TODO: Could also get this value from the driver results?
                if not self._dry_run:
                    obj_val = self.prob.get_objective()
                else:
                    obj_val = next(self._dry_run_iterator)
                msg = f"Successfully Evaluated Configuration: objective = {obj_val}, function_evaluations = {func_evals}"
                logging.info(msg)
                
            else:
                msg = "Optimization Failed to Converge"
                logging.warning(msg)
                obj_val = None
        else:
            obj_val = None
                
        if self.counter:
            self.counter.increment(fevals=func_evals)
            
        if case_name:
            self.prob.record(case_name) # Record problem variables 
            iter_data.case_name = case_name
        
        iter_data.obj_val = obj_val
        iter_data.func_evals = func_evals
        iter_data.msg = msg
        
        cleanup()
        return iter_data
    
    def search(self, max_iter=None, max_stall_iter=None, func_threshold=None):
        config_sets = self.config_searcher.sorted_sets
        iterations = [] # List of SearchIteration objects
        opt_iter = None # Current best SearchIteration object
        terminate = False
        stall_cntr = 0
        
        if self.base_case:
            self.prob.final_setup()
            self.prob.load_case(self.base_case)
            self.prob.record("base_case") # Record problem variables 
            
        for i,config in enumerate(config_sets):
            iter_data = SearchIteration(iteration=i)
            iter_data = self.evaluate(config, base_case = self.base_case, case_name = f"iteration_{i}", iter_data=iter_data)
            
            # Update optimal configuration
            if i == 0:
                opt_iter = iter_data
            elif iter_data.obj_val and (iter_data.obj_val < opt_iter.obj_val):
                opt_iter = iter_data
                stall_cntr = 0
            else:
                stall_cntr += 1
                
            # Update and record iter_data
            iter_data.opt_iter = opt_iter
            iterations.append(iter_data)
            if self.search_recorder:
                self.search_recorder.record_iteration(iter_data)
                
            # Termination
            if i >= max_iter:
                terminate = True
                term_msg = "Maximum Iterations Exceeded"
            elif func_threshold and opt_iter.obj_val < func_threshold:
                terminate = True
                term_msg = "Function Threshold Reached"
            elif max_stall_iter and stall_cntr >= max_stall_iter:
                terminate = True
                term_msg = f"Stalled at {stall_cntr} iterations"
                
            if terminate:
                break

        # Output Search Result
        search_result = SearchResult()
        if self.base_case:
            search_result.base_case_data = R.CaseData(self.base_case)
        search_result.config_searcher = self.config_searcher
        search_result.iterations = iterations
        search_result.opt_iter = opt_iter
        search_result.termination_msg = term_msg
        search_result.objective = self.prob.model.get_objectives()
        if self.counter:
            search_result.counter_state = self.counter.state()
        
        if self.search_recorder:
            self.search_recorder.record_result(search_result)
        
        print(search_result)
        return search_result
    
    def search_GA(self, max_generations=None, max_stall_iter=None, func_threshold=None):
        import pygad
        
        comp_searchers = self.config_searcher.component_searchers
        comp_data = []
        gene_space = []
        for k,cs in comp_searchers.items():
            cd = cs.sorted_comps
            comp_data.append(cd)
            gene_space.append(range(len(cd)))
            
                
        if self.base_case:
            self.prob.final_setup()
            self.prob.load_case(self.base_case)
            self.prob.record("base_case") # Record problem variables 
        
        iterations = []
        self._iter_counter = -1
        
        def fitness_function(solution, solution_idx):
            # solution: 1D Vector representing a single solution
            # solution_idx: Solution index within the population (?)
            # This function will be MAXIMIZED

            self._iter_counter += 1
            
            # Create config from the component searchers
            config = Surrogate.ComponentDataSet()
            for (i,comp_index) in enumerate(solution):
                cd = comp_data[i]
                comp = cd[comp_index]
                config.add(comp)
            
            
            # EValuate the configuration
            iter_data = SearchIteration_GA(iteration=self._iter_counter)
            iter_data.solution = solution
            iter_data.solution_idx = solution_idx
            
            iter_data = self.evaluate(config, base_case = self.base_case, case_name = f"iteration_{self._iter_counter}", iter_data=iter_data)
            
            iterations.append(iter_data)
            if self.search_recorder:
                self.search_recorder.record_iteration(iter_data)
            
            if iter_data.obj_val:
                return -float(iter_data.obj_val)
            else:
                #return np.nan
                return -100
            
        def callback_gen(ga_instance):
            print("Generation : ", ga_instance.generations_completed)
            print("Fitness of the best solution :", ga_instance.best_solution()[1])
            
        stop_criteria = []
        if func_threshold:
            stop_criteria.append(f"reach_{func_threshold}")
        
        if max_stall_iter:
            stop_criteria.append(f"saturate_{max_stall_iter}")

        ga_instance = pygad.GA(
                                   num_generations=max_generations,
                                   num_parents_mating=2,
                                   sol_per_pop=3,
                                   
                                   num_genes=len(comp_data),
                                   gene_space=gene_space,
                                   gene_type=int,
                                   
                               
                                   fitness_func=fitness_function,
                                   callback_generation=callback_gen,
                                   
                                   stop_criteria=stop_criteria,

                                   save_solutions=True
                               )
        
        ga_instance.run()
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        
        logging.info(f"Solution: {solution}, Solution Fitness: {solution_fitness}")
        
        opt_iter = None
        for i in iterations:
            sol_match = i.solution == solution
            if sol_match.all():
                opt_iter = i
                break

        search_result = SearchResult_GA()
        search_result.iterations = iterations
        if self.base_case:
            search_result.base_case_data = R.CaseData(self.base_case)
        search_result.component_data = comp_data
        search_result.gene_space = gene_space
        search_result.opt_iter = opt_iter
        search_result.objective = self.prob.model.get_objectives()
        if self.counter:
            search_result.counter_state = self.counter.state()
            
        ga_instance.fitness_func = None
        ga_instance.callback_generation = None
        ga_instance.on_generation = None
        search_result.ga_instance = ga_instance
        
        if self.search_recorder:
            self.search_recorder.record_result(search_result)
        
            
        return search_result
            
        

class ConfigurationSearcher:
    def __init__(self, component_searchers, configuration_template=None):
        self.component_searchers = component_searchers # Dictionary of component searchers, key's are the "name" of the searcher
        
        # Configuration Template: specifies a complete component set, e.x.
        # configuration_template = ["Battery", "PMSMMotor", "Propeller"]
        # Entries correspond to keys of component_searchers
        if not configuration_template:
            configuration_template = list(component_searchers.keys())
        self.configuration_template = configuration_template
        
        self._sorted_sets_distances = None
        
    @property
    def sorted_sets(self):
        return [Surrogate.ComponentDataSet([cd[0] for cd in sd[0]]) for sd in self._sorted_sets_distances]
        
    @property
    def component_distances(self):
        return [[cd[1] for cd in sd[0]] for sd in self._sorted_sets_distances]
    
    @property
    def configuration_distances(self):
        return [sd[1] for sd in self._sorted_sets_distances]
    
    def run(self):
        for searcher in self.component_searchers.values():
            searcher.run()
        self.sortSets()
        
    def enumerator(self):
        # Enumerates all possible sets from component_searchers' sorted comps corresponding to the configuration template
        cd_all = [self.component_searchers[name]._sorted_comps_distances for name in self.configuration_template]
        
        #TODO: We could think about this in a smarter way to that the enumerator considers component distances
        # as it builds the set to take some of the burden off the sort. 
        combinations = [c for c in itertools.product(*cd_all)]
        
        return combinations
    
    def configuration_distance(self, configs):
        # config_dist: list of (comp, distance) tuples
        comp_distances = [x[1] for x in configs]
        return np.linalg.norm(comp_distances)
        
    def sortSets(self):
        # Generates ComponentSets in ascending order of configuration distance
        sorted_sets = []
        combinations = self.enumerator()
        for s in combinations:
            d_s = self.configuration_distance(s)
            sorted_sets.append((s, d_s))
        
        sorted_sets.sort(key=lambda x : x[1])
        self._sorted_sets_distances = sorted_sets
        
        return sorted_sets
    
    def plotDistances(self, fig=None, ax=None, annotate=True, iter_slice=None):
        if not fig:
            fig = plt.figure()
        if not ax:
            ax = plt.axes()
        
        if not iter_slice:
            iter_slice = slice(None, None)
            
        indices = range(len(self.configuration_distances))[iter_slice]
        cd = self.configuration_distances[iter_slice]
        
        ax.plot(indices, cd, '-k', linewidth=2, label="$d_s$")
        
        comp_distances = self.component_distances[iter_slice]
        for (i,name) in enumerate(self.configuration_template):
            d = [x[i] for x in comp_distances] # Get distance corresponding to individual component
            ax.plot(indices, d, linewidth=1, alpha=0.4, label=f"$d_c$: {name}")
        
        ax.legend()
        ax.set_xlabel("Configuration")
        ax.set_ylabel("Distances")
        
        return (fig, ax)
    
    def plotDesignSpace(self, config_data, config_name=None):
        comp_searchers = self.component_searchers
        
        if not isinstance(config_data, P.ParamValSet):
            config_data = config_data.data # Get corresponding parameter values
        
        figs = []
        for k,cs in comp_searchers.items():
            (fig, ax) = cs.plotCompDistances()
            handles, labels = ax.get_legend_handles_labels()
            print(labels)
            
            vals = [p.get_compatible(config_data).val for p in cs.boundary.args]
            
            mkropts = {"marker":"o", "markersize":10, "markerfacecolor":"forestgreen", "markeredgecolor":"0.8", "linestyle":"None"}
            if config_name:
                mkropts["label"] = config_name
        
            c_mkr, = ax.plot(*vals, **mkropts)
            
            if config_name:
                handles.append(c_mkr)
                ax.legend(handles=handles)

            figs.append(fig)
            
        return figs
    
    #TODO: Add component_searchers back to ConfigurationSearcher state, Fix component_searcher so it can be pickled. Want to be able to save/load the boundaries. 
    # def __getstate__(self):
    #     state = self.__dict__.copy()
    #     del state["component_searchers"]
    #     return state
    
    # def __setstate__(self, state):
    #     self.__dict__.update(state)

class ComponentSearcher:
    # ComponentData Wrapper Class for Discrete Search
    def __init__(self, surrogate):
        self.boundary = surrogate.boundary
        self.comp_name = surrogate.comp_name
        self.comp_data = surrogate.comp_data
        
        self.target = None
        self.sorted_comps = None
        self._sorted_comps_distances = None

    def set_target(self, pv_target):
        self.target = P.ParamValSet([pv for pv in pv_target if pv.component == self.comp_name])
        
    def run(self):
        self.filterNearest()

    def component_distance(self, candidate_comp, method="Norm", enforce_bounds=True):
        def param_error(t,c):
            # Parameter Error Calculation
            
            if method == "Norm":
                return ((c/t) - 1)
        
        def distance(param_errors):
            # Component Distance Metric
            return np.linalg.norm(param_errors)
        
        def check_valid(pv_t, pv_c):
            valid = True
            
            # Ensure candidate parameter is in bounds
            if enforce_bounds:
                if pv_t.lb and pv_c.val < pv_t.lb:
                    valid = False
                if pv_t.ub and pv_c.val > pv_t.ub:
                    valid = False
                
            return valid
        
        candidate = candidate_comp.data # Get ParamValSet from ComponentData
        errors = []
        for pv_t in self.target:
            pv_c = pv_t.get_compatible(candidate)
            if pv_c:
                valid = check_valid(pv_t, pv_c)
                if not valid:
                    # Exit function and return NaN distance
                    return None
                errors.append(param_error(pv_t.val, pv_c.val))
            
        return distance(errors)
        
    def filterNearest(self, **kwargs):        
        cd_dist = []
        for c in self.comp_data:
            d = self.component_distance(c, **kwargs)
            if d != None:
                cd_dist.append((c,d))
        
        cd_dist.sort(key = lambda x:x[1])
        self._sorted_comps_distances = cd_dist
        self.sorted_comps = [x[0] for x in cd_dist]
        return cd_dist
    
    def plotCompDistances(self, ax=None, fig=None, dist_func=None, falloff_order = 1/10, scatter_label="Components", scatter_edgecolors="0.8", scatter_cmap="Blues_r"):
        if not dist_func:
            dist_func = self.component_distance
        
        (fig,ax) = self.boundary.plot2D(fig=fig,ax=ax)
        fig.suptitle(f"Component: {self.comp_name}")
        
        handles = []
        
        distances = []
        for c in self.comp_data:
            d = dist_func(c)
            if falloff_order and d:
                d = d**falloff_order
            distances.append(d)
        
        self.comp_data.plot(self.boundary.args, ax=ax, fig=fig, annotate=False, scatter_kwargs={"c":distances, "label":scatter_label, "edgecolors":scatter_edgecolors, "cmap":scatter_cmap})          
        
        for child in ax.get_children():
            if isinstance(child, matplotlib.collections.PathCollection):
                handles.append(child)
        
        # Add plot of Target:
        mkropts = {"marker":"o", "markersize":10, "markerfacecolor":"none", "markeredgewidth":2, "linestyle":"None"}
        trgt_pnt = []
        for p in self.boundary.args:
            pv = p.get_compatible(self.target)
            trgt_pnt.append(pv.val)
        l_i, = ax.plot(*trgt_pnt, markeredgecolor="orange",  label="Target", **mkropts)
        handles.append(l_i)
        
        
        ax.legend(handles=handles)
        
        return (fig, ax)
        
            
        
    
    
    
    
        
        
        