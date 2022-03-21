classdef PMSMMotor < Component
    %PMSM Motor
    %   Default parameters need updated
    
    properties (SetAccess = private)
        L Param
        kV Param
        Rm Param
        B_v Param
        
        D Param
        J Param
                
        K_t Param
        Mass extrinsicParam
        Price extrinsicParam
    end
    
    properties(SetAccess = private)
        Surrogate MotorSurrogate
    end
    properties (Dependent)
        Fit paramFit
    end
        
    methods
        function f = get.Fit(obj)
            f = obj.Surrogate.Fit;
        end
    end
    
    methods (Access = protected)
        function DefineParams(obj)
            obj.L = Param('L', 1.17e-4, 'Unit', "H", 'Tunable', true); % Inductance - H
            obj.kV = Param('kV', 900,'Unit', "RPM/V", 'Tunable', true); % Torque/Speed Coefficient - Nm/A = Vs/rad
            obj.Rm = Param('Rm',0.117, 'Unit', "Ohm", 'Tunable', true); % Phase Resistance - Ohms      
            obj.B_v = Param('Bv', 0, 'Unit', 'N*m*s/rad', 'Tunable', true);
            
            obj.D = Param('D', 0.05, 'Unit', "m", 'Tunable', true);
            obj.J = Param('J', 6.5e-6,'Unit', "kg*m^2", 'Tunable', true); % Mechanical rotational inertia - Modified to better reflect Ferry's simulation results
            
            obj.K_t = Param('K_t', NaN, 'Unit', "Nm/A", 'Tunable', true);
            obj.Mass = extrinsicParam('Mass',0.04, 'Unit', "kg", 'Tunable', true);
            obj.Price = extrinsicParam('Price', NaN, 'Unit', "USD", 'Tunable', true);
            
            obj.J.setDependency(@PMSMMotor.calcInertia, [obj.Mass, obj.D]);
            obj.J.Dependent = true;
            
            obj.K_t.setDependency(@PMSMMotor.kVToKt, [obj.kV]);
            obj.K_t.Dependent = true;
        end
        function init(obj)
            ms = MotorSurrogate();
            ms.Fit.Inputs = [obj.kV, obj.Rm];
            ms.Fit.Outputs = [obj.Mass, obj.D, obj.Price];
            ms.Fit.setOutputDependency;
            obj.Surrogate = ms;
            for i = 1:numel(ms.Fit.Outputs)
                ms.Fit.Outputs(i).Dependent = true;
            end
        end
        function DefineComponent(obj)
            % Capacitance Types
            C(1) = Type_Capacitance('x');
            
            % PowerFlow Types
            PF(1) = Type_PowerFlow('xt*xh');
            PF(2) = Type_PowerFlow('xt^2');
            
            % Vertices
            V(1) = GraphVertex_Internal('Description', "Inductance (i_q)", 'Capacitance', C(1), 'Coefficient', obj.L, 'Initial', 0, 'VertexType', 'Current', 'DynamicType', 'StateFlow');
            V(2) = GraphVertex_Internal('Description', "Inertia (omega_m)", 'Capacitance', C(1), 'Coefficient', obj.J, 'Initial', 0, 'VertexType', 'AngularVelocity', 'DynamicType', 'StateFlow');
            
            V(3) = GraphVertex_External('Description', "Input Voltage (v_q)", 'VertexType', 'Voltage', 'DynamicType', 'StateFlow');
            V(4) = GraphVertex_External('Description', "Mechanical Load (T_l)", 'VertexType', 'Torque', 'DynamicType', 'StateFlow');
            V(5) = GraphVertex_External('Description', "Heat Sink", 'VertexType', 'Temperature');
            
            % Inputs
            
            % Edges
            E(1) = GraphEdge_Internal(...
                'PowerFlow',PF(1),...
                'Coefficient',1,...
                'TailVertex',V(3),...
                'HeadVertex',V(1));
            
            E2_Coeff = Param("E2_Coeff", NaN, 'Dependent', true, 'Tunable', false);
            E2_Coeff.setDependency(@(K_t) sqrt(3/2)*K_t, obj.K_t)
            
            E(2) = GraphEdge_Internal(...
                'PowerFlow',PF(1),...
                'Coefficient',E2_Coeff,...
                'TailVertex',V(1),...
                'HeadVertex',V(2));
            
            E(3) = GraphEdge_Internal(...
                'PowerFlow',PF(1),...
                'Coefficient',1,...
                'TailVertex',V(2),...
                'HeadVertex',V(4));
            
            E(4) = GraphEdge_Internal(...
                'PowerFlow',PF(2),...
                'Coefficient',obj.Rm,...
                'TailVertex',V(1),...
                'HeadVertex',V(5));
            
            E(5) = GraphEdge_Internal(...
                'PowerFlow',PF(2),...
                'Coefficient',obj.B_v,...
                'TailVertex',V(2),...
                'HeadVertex',V(5));
                       
            g = Graph(V, E);
            obj.Graph = g;
            
            % Ports            
            p(1) = ComponentPort('Description',"Voltage Input",'Element',E(1));
            p(2) = ComponentPort('Description',"Torque Output",'Element',E(3));
            p(3) = ComponentPort('Description',"Heat Sink",'Element',V(5));
            obj.Ports = p;
        end
    end
    
    methods (Static)
        function K_t = calcTorqueConstant(P,lambda_m)
            % P - Total number of poles - not pole pairs
            % lambda_m - Magnetic Flux Linkage
            K_t = (P/2)*lambda_m;
        end
        
        function K_t = kVToKt(kV)
            % Convert kV in rpm/V to torque constant Kt in N*m/A = V/(rad/s)
            kV_radps = kV*(2*pi)/60;
            K_t = 1./kV_radps;
        end
        
        function kV = KtTokV(Kt)
            kV_radps = 1./Kt;
            kV =kV_radps/((2*pi)/60);
        end
        
        function J = calcInertia(M,D)
            % Estimate mass of rotor as M/2;
            % R = D/2;
            % J = MR^2 (Hoop moment of inertia)
            
            J = (M/2).*(D/2).^2;
        end
    end
end

