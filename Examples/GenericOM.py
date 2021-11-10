import openmdao.api as om
import numpy as np
import importlib as impL
import pandas as pd
import sys
        


class MatlabModel(om.ExplicitComponent):
    
    def initialize(self):
        self.options.declare('Model', types=str, default = 'None')
    
    
    
    def setup(self):
        mdl = self.options['Model']
        
        self.ImportModel(mdl)
        
        for i in range(self.ModelSize['Nu']):
            self.add_input('u{}'.format(i+1),val=0)
        
        for i in range(self.ModelSize['Nd']):
            self.add_input('d{}'.format(i+1),val=0)
        
        for i in range(self.ModelSize['Nout']):
            self.add_output('y{}'.format(i+1),val=0)
            
        
    
    def setup_partials(self):
        self.declare_partials('*', '*')    
    
    
    
    def compute(self,inputs,outputs):
        x = []
        u = []
        d = []
        for i in range(self.ModelSize['Nu']):
            u.append(inputs['u{}'.format(i+1)])
        for i in range(self.ModelSize['Nd']):
            d.append(inputs['d{}'.format(i+1)])
        
        out = self.calc['calcX'](x,u,d)
        
        for i in range(self.ModelSize['Nout']):
            outputs['y{}'.format(i+1)] = out[i]
    
    
    
    def compute_partials(self, inputs, J):
        x = []
        u = []
        d = []
        Nu = self.ModelSize['Nu']
        Nd = self.ModelSize['Nd']
        for i in range(Nu):
            u.append(inputs['u{}'.format(i+1)])
        for i in range(Nd):
            d.append(inputs['d{}'.format(i+1)])
        
        if Nu>0:
            outU = self.calc['calcJu'](x,u,d)
        outD = self.calc['calcJd'](x,u,d)
        
        cnt = 0
        for i in range(Nu):
            for j in range(self.ModelSize['Nout']):
                J['y{}'.format(j+1),'u{}'.format(i+1)] = outU[cnt]
                cnt = cnt + 1
                
        cnt = 0
        for i in range(Nd):
            for j in range(self.ModelSize['Nout']):
                J['y{}'.format(j+1),'d{}'.format(i+1)] = outD[cnt]
                cnt = cnt + 1       
                
                     
    
    def ImportModel(self,mdl):
        
        # sys.path.insert(0, mdl)
        
        inp = pd.read_csv(mdl+'\Inp.csv')
        dists = pd.read_csv(mdl+'\Dist.csv')
        out = pd.read_csv(mdl+'\Out.csv')    
        Nu = len(inp)
        Nd = len(dists)
        Nout = len(out)
        
        fX = impL.import_module(mdl+'.X')
        if Nu != 0:
            fJu = impL.import_module(mdl+'.Ju')
        fJd = impL.import_module(mdl+'.Jd')
        
        
        
        for i in range(Nout):
            calcX = getattr(fX, 'CalcX')
        
            if Nu != 0:
                for j in range(Nu):
                    calcJu = getattr(fJu, 'CalcJu')
            else:
                 calcJu = []   
                    
            if Nd != 0:
                for j in range(Nd):
                    calcJd = getattr(fJd, 'CalcJd')
                    
        self.ModelSize = {'Nu':Nu,'Nd':Nd,'Nout':Nout}         
        self.calc = {'calcX':calcX,'calcJu':calcJu,'calcJd':calcJd}  
        self.VarNames = {'Inputs':inp,'Dists':dists,'Outputs':out}  
                
            
    


p = om.Problem()
p.model.add_subsystem('Test', subsys=MatlabModel(Model='Shaft'),promotes=['*'])




# p.model.add_subsystem('Pin',subsys=om.ExecComp('Pin=y1+y3'),promotes=['*'])



# p.model.add_design_var('u1',lower=.01,upper=.99,ref0=0,ref=1)
# p.model.add_design_var('u2',lower=.01,upper=.99,ref0=0,ref=1)
# p.model.add_design_var('u3',lower=.01,upper=.99,ref0=0,ref=1)
# p.model.add_design_var('u4',lower=.01,upper=.99,ref0=0,ref=1)
# p.model.add_design_var('u5',lower=.01,upper=.99,ref0=0,ref=1)

# p.model.add_objective('Pin',ref0=3800,ref=10000)
# p.model.add_constraint('y13',equals=1000)
# p.model.add_constraint('y14',equals=250)
# p.model.add_constraint('y15',equals=2000)


# p.model.nonlinear_solver = om.NewtonSolver(maxiter=50,rtol=1e-10,
#     iprint=0,solve_subsystems=False)
# p.model.linear_solver = om.DirectSolver(iprint=0)
# # p.model.nonlinear_solver = om.NonlinearBlockGS(maxiter=50,rtol=1e-10,iprint=0)
# # p.model.linear_solver = om.LinearBlockGS(iprint=0)
# p.driver = om.ScipyOptimizeDriver()
# p.driver.options['debug_print'] = ['objs'] 
# p.driver.options['maxiter'] = 200 


p.setup(force_alloc_complex=True)


# for i in range(5):
#     p['u{}'.format(i+1)] = .2+.1*i
# for i in range(3):
#     p['d{}'.format(i+1)] = 100+100*i

# p['d1'] = 30
# p['d2'] = 10
# p['d3'] = 5
# om.n2(p)
# # p.run_model()
# # p.check_partials(method='cs',compact_print = True)

# # for i in range(18):
# #     print(p['y{}'.format(i+1)])



# p.run_driver()    

# print(p['y1'])
# print(p['y3'])
# print(p['u1'])
# print(p['u2'])
# print(p['u3'])
# print(p['u4'])
# print(p['u5'])

# print(p['y13'])
# print(p['y14'])
# print(p['y15'])