classdef MotorProp < System
    properties (SetAccess = private)
        J_r Param
    end
    
    methods
        function obj = MotorProp(opts)
            arguments
                opts.Name = "MotorProp"
                opts.pmsmmotor = PMSMMotor('Name', "Motor");
                opts.propeller = Propeller('Name', "Propeller");
            end
            
            comps = [opts.pmsmmotor, opts.propeller];
            obj = obj@System();
            obj.Components = comps;
            obj.Name = opts.Name;
            obj.DefineParams();
            obj.DefineElement(); % Don't want to modify parameters or children automatically, all defined explicitly below
        end
    end
    
    methods (Access = protected)
        function DefineParams(obj)
            Motor = obj.Components(1);
            Prop = obj.Components(2);
            
            obj.J_r = Param("J_r", NaN, 'Unit', "kg*m^2", 'Description', "Rotor Inertia", 'Dependent', true, 'Tunable', true);
            obj.J_r.Parent = obj;
            obj.J_r.setDependency(@(J_m, J_p) J_m + J_p, [Motor.J, Prop.J]);
            obj.J_r.update();
        
            % Params
            % I'll wait to combine the extrinsic params until the QuadRotor
            params = unique(vertcat(Motor.Params, Prop.Params, obj.J_r));
            obj.Params = params;
        end
        function DefineElement(obj)
            Motor = obj.Components(1);
            Prop = obj.Components(2);
            
            V_temp = copy(Motor.Graph.Vertices);
            V_temp_desc = [V_temp.Description];
            
            % Order Graph Vertices may change depending on which states are
            % algebraic.  We want to force this order so that assign the
            % correct head/tail vertices to the edges.  
            V_desc = ["Inductance (i_q)", "Inertia (omega_m)", "Input Voltage (v_q)", "Mechanical Load (T_l)", "Heat Sink"];
            for i = 1:numel(V_desc)
                V(i) = V_temp(V_temp_desc == V_desc(i));
            end
                
            E = copy(Motor.Graph.Edges);
            E(1).TailVertex = V(3); E(1).HeadVertex = V(1); % Edge TailVertices and HeadVertices must be reassigned
            E(2).TailVertex = V(1); E(2).HeadVertex = V(2);
            E(3).TailVertex = V(2); E(3).HeadVertex = V(4);
            E(4).TailVertex = V(1); E(4).HeadVertex = V(5);
            E(5).TailVertex = V(2); E(5).HeadVertex = V(5);
            
            % Modify Vertices
            V(2).Coefficient = obj.J_r;
            V(2).Parent = obj;
            V(4).Description = "Drag Sink";
            V(4).VertexType = 'Abstract';
            V(4).Parent = obj;

            % Modify Edges
            PF = Type_PowerFlow('xt^3'); % Additional powerflow type for propeller
            E(3).PowerFlow = PF;
            E(3).Coefficient = Prop.K_Q;
            E(3).Parent = obj;

            
            g = Graph(V, E);
            obj.Graph = g;
            obj.Graph.Parent = obj;
            
            % Ouptuts
            syms omega
            omsqrd = symfun(omega^2, omega);
            
            coeff = Prop.K_T;
            O(1) = GraphOutput('Description', "Thrust", 'Coefficient', coeff, 'Function', omsqrd, 'Breakpoints', {V(2)});
            O(1).Parent = obj;
            
            coeff = Prop.K_Q;
            O(2) = GraphOutput('Description', "Torque", 'Coefficient', coeff, 'Function', omsqrd, 'Breakpoints', {V(2)});
            O(2).Parent = obj;
            
            obj.Graph.Outputs = O;
            
            % Ports            
            p(1) = ComponentPort('Description',"Voltage Input",'Element',E(1));
            p(2) = ComponentPort('Description',"Heat Sink",'Element',V(5));
            obj.Ports = p;
        end
    end
end

