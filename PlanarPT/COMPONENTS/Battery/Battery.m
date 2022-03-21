classdef Battery < Component
    % Battery Cell Specifications from: Nemes et. al. "Parameters identification using experimental measurements for equivalent circuit Lithium-Ion cell models"
    % Battery Pack specifications (N_s and N_p) from: Ferry, "Quadcopter Plant Model and Control System Development With MATLAB/Simulink Implementation"
    % Pack specs from Turnigy Graphene Panther 4000mAh 3S 75C Battery Pack w/XT90
    
    % All parameters specified per cell except for N_series and N_parallel
    
    properties (SetAccess = private)
        N_p Param
        N_s Param
        Q Param
        C Param
        V_OCV_nominal Param

        % Dependent Params
        R_s Param
        R_p Param
        V_OCV_pack Param
        Capacity Param
        DischargeCurrent Param
        Mass extrinsicParam
        Price extrinsicParam
    end

    properties(SetAccess = private)
        Surrogate BatterySurrogate
    end
    properties (Dependent)
        Fit paramFit
    end
    
    methods (Access = protected)
        function DefineParams(obj)
            % Independent Params
            obj.N_p = Param('N_p', 1, 'Unit', "unit", 'Tunable', true); % Number of cells in parallel
            obj.N_s = Param('N_s', 3, 'Unit', "unit", 'Tunable', true); % Number of cells in series
            obj.Q = Param('Q', 4000, 'Unit', "mAh", 'Tunable', true); % mAh
            obj.C = Param('C', 75, 'Unit', "A/Ah", 'Description', "Constant Discharge Rating", 'Tunable', true); % C-Rating: I = C(1/hr) * Q(Ah) = A
            obj.V_OCV_nominal = Param('V_OCV_nom', 3.7, 'Unit', 'V', 'Tunable', true); %Nominal Open Circuit Voltage = V_OCV_nominal*V_OCV_curve(q)
            
            % Dependent Params - Dependency set in init()
            obj.R_s = Param('R_s', (10e-3) / 3, 'Unit', "Ohm", 'Tunable', true); % Series Resistance - Ohms - From Turnigy Website
            obj.R_p = Param('R_p', NaN, 'Unit', "Ohm", 'Description', 'Pack Resistance', 'Tunable', true); % Dependent Param, pack resistance
            obj.V_OCV_pack = Param('V_OCV_pack', NaN, 'Unit', 'V', 'Tunable', true); %Nominal Open Circuit Voltage = V_OCV_nominal*V_OCV_curve(q)
            obj.Capacity = Param('Capacity', NaN, 'Unit', "As", 'Description', 'Pack Capacity', 'Tunable', true); % Dependent Param A*s
            obj.DischargeCurrent = Param('MaxDischarge', NaN, 'Unit', "A", 'Description', 'Maximum constant discharge current', 'Tunable', true);
            obj.Mass = extrinsicParam("Mass", NaN, 'Unit', "kg", 'Tunable', true);
            obj.Price = extrinsicParam("Price", NaN, 'Unit', "USD", 'Tunable', true);
            
            rpfun = @(N_s,N_p,R_s) N_s./N_p.*R_s;
            setDependency(obj.R_p, rpfun, [obj.N_s, obj.N_p, obj.R_s]);
            obj.R_p.Dependent = true;
            
            vpackfun = @(N_s, v_ocv_nom) N_s*v_ocv_nom;
            setDependency(obj.V_OCV_pack, vpackfun, [obj.N_s, obj.V_OCV_nominal]);
            obj.V_OCV_pack.Dependent = true;
            
            capfun = @(N_p,Q) N_p.*Battery.mAhToCoulombs(Q);
            setDependency(obj.Capacity, capfun, [obj.N_p, obj.Q]);
            obj.Capacity.Dependent = true;
            
            dischargefun = @(C,Q) C*Q/1000;
            setDependency(obj.DischargeCurrent, dischargefun, [obj.C, obj.Q]);
            obj.DischargeCurrent.Dependent = true;
        end
        
        function init(obj)       
            bs = BatterySurrogate();
            bs.Fit.Inputs = [obj.N_s, obj.Q];
            bs.Fit.Outputs = [obj.R_s, obj.Mass, obj.Price];
            bs.Fit.setOutputDependency();
            obj.Surrogate = bs;
            for i = 1:numel(bs.Fit.Outputs)
                bs.Fit.Outputs(i).Dependent = true;
            end
        end
        
        function DefineComponent(obj)
            % Capacitance Types
            C(1) = Type_Capacitance(1); % Capacitance Type for Q*V_OCV
            C(2) = Type_Capacitance("x");
            
            % PowerFlow Types
            P(1) = Type_PowerFlow('xh');
            P(2) = Type_PowerFlow("xt^2");
            
            % Vertices
            voltage_coeff = Param("v_coeff", NaN, 'Dependent', true, 'Tunable', false);
            voltage_coeff.setDependency(@(N_s,vnom) N_s * vnom, [obj.N_s, obj.V_OCV_nominal]);
            
            energy_coeff = Param("e_coeff", NaN, 'Dependent', true, 'Tunable', false);
            energy_coeff.setDependency(@(v_coeff, cap) v_coeff*cap, [voltage_coeff, obj.Capacity]);
            
            Vertex(1) = GraphVertex_Internal('Description', "Battery SOC", 'Capacitance', C(1), 'Coefficient', energy_coeff, 'Initial', 1, 'VertexType','Abstract');
            Vertex(2) = GraphVertex_External('Description', "Load Current", 'VertexType', 'Current', 'DynamicType', 'StateFlow');
            Vertex(3) = GraphVertex_External('Description', "Heat Sink", 'VertexType', 'Temperature');
            
            % Inputs
            
            % Edges
            Edge(1) = GraphEdge_Internal('PowerFlow',P(1),'Coefficient',voltage_coeff,'TailVertex',Vertex(1),'HeadVertex',Vertex(2));
            Edge(2) = GraphEdge_Internal('PowerFlow',P(2),'Coefficient',obj.R_p,'TailVertex',Vertex(2),'HeadVertex',Vertex(3));
            
            g = Graph(Vertex, Edge);
            obj.Graph = g;
            
            % Ports
            p(1) = ComponentPort('Description','Load Current','Element', Vertex(2));
            obj.Ports = p;
        end
    end

    methods
        function f = get.Fit(obj)
            f = obj.Surrogate.Fit;
        end
    end
    
    methods (Static)
        function mah = CoulombsTomAh(c)
            mah = c/3.6;
        end
        
        function c = mAhToCoulombs(mAh)
            c = 3.6*mAh;
        end
    end
end

