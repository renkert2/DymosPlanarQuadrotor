classdef Propeller < Component
    %PROPELLER Summary of this class goes here
    %   Detailed explanation goes here
    
    properties (SetAccess = private)
        % Independent Params
        D Param
        P Param
        k_P Param
        k_T Param
        k_P_mod Param
        k_T_mod Param
        Mass extrinsicParam
        Price extrinsicParam
        J Param
        rho Param
        
        % Dependent Params
        k_Q Param
        K_Q Param
        K_T Param
    end

    properties (SetAccess = private)
       Surrogate PropellerSurrogate
    end
    properties (Dependent)
        Fit paramFit
    end
    
    methods (Access = protected)
        function DefineParams(obj)
            obj.D = Param('D', 0.1780, 'Unit', "m", 'Tunable', true); % Propeller Diameter - m
            obj.P = Param('P', 0.0673, 'Unit', "m", 'Tunable', true); % Propeller Pitch - m
            
            % k_Q and k_T Parameters from:
            % Illinois Volume 2 Data
            % Static Test for C_t and C_p
            % Note: C_q (drag coeff) = C_p (power coeff) / (2 * pi)
            % - https://m-selig.ae.illinois.edu/props/volume-2/data/da4002_5x2.65_static_1126rd.txt
            
            % Nominal Parameters from "magf_7x4" in propStruct
            obj.k_P = Param('k_P',  0.0411, 'Tunable', true); % Power coefficient - k_P = 2*pi*k_Q, speed in rev/s
            obj.k_T = Param('k_T', 0.0819, 'Tunable', true); % Thrust coefficient - N/(s^2*kg*m^2), speed in rev/s.
            
            obj.k_P_mod = Param('k_P_mod', 1, 'Tunable', true); % Used to adjust k_P based on experimental data
            obj.k_T_mod = Param('k_T_mod', 1, 'Tunable', true); % Used to adjust k_T from experimental data
            
            obj.Mass = extrinsicParam('Mass', 0.008, 'Unit', "kg", 'Tunable', true);
            obj.Price = extrinsicParam('Price', NaN, 'Unit', "USD", 'Tunable', true);
            obj.J = Param('J', 2.1075e-05,'Unit', "kg*m^2", 'Tunable', true); % Rotational Inertia - kg*m^2 from "Stabilization and Control of Unmanned Quadcopter (Jiinec)
            
            obj.rho = Param('rho', 1.205, 'Unit', "kg/m^3", 'Description', "Air Density", 'Tunable', true); % Air Density - kg/m^3
            obj.k_Q = Param('k_Q', NaN, 'Unit', "N/(s*kg*m)", 'Description', "Drag Torque Coefficient", 'Dependent', true, 'Tunable', true); % Drag Torque Coefficient - N/(s*kg*m)=1/s^4, speed in rev/s.
            obj.K_Q = Param('K_Q', NaN, 'Unit', "N*m/(rad/s)^2", 'Description', "Lumped Drag Coefficient", 'Dependent', true, 'Tunable', true); %square_drag_coeff %coefficient in front of speed^2 term, N*m/(rad/s)^2.
            obj.K_T = Param('K_T', NaN, 'Unit', "N/(rad/s)^2", 'Description', "Lumped Thrust Coefficient", 'Dependent', true, 'Tunable', true); %square_thrust_coeff %coefficient in front of speed^2 term, N/(rad/s)^2.
                    
            obj.J.setDependency(@Propeller.calcInertia, [obj.Mass, obj.D]);
            obj.J.Dependent = true;
            obj.k_Q.setDependency(@Propeller.calcTorqueCoefficient, [obj.k_P, obj.k_P_mod]);
            obj.k_Q.Dependent = true;
            obj.K_Q.setDependency(@Propeller.calcLumpedTorqueCoefficient, [obj.k_Q, obj.rho, obj.D]);
            obj.K_Q.Dependent = true;
            obj.K_T.setDependency(@Propeller.calcLumpedThrustCoefficient, [obj.k_T, obj.k_T_mod, obj.rho, obj.D]);
            obj.K_T.Dependent = true;
        end
        
        function init(obj)
            ps = PropellerSurrogate();
            ps.Fit.Inputs = [obj.D, obj.P];
            ps.Fit.Outputs = [obj.k_P, obj.k_T, obj.Mass, obj.Price];
            ps.Fit.setOutputDependency;
            obj.Surrogate = ps;
            for i = 1:numel(ps.Fit.Outputs)
                ps.Fit.Outputs(i).Dependent = true;
            end
        end
        
        function DefineComponent(obj)
            % Capacitance Types
            C(1) = Type_Capacitance('x');
            
            % PowerFlow Types
            P(1) = Type_PowerFlow('xt*xh');
            P(2) = Type_PowerFlow('xt^3');
            
            % Vertices
            V(1) = GraphVertex_Internal('Description', "Inertia (omega)",...
                'Capacitance', C(1),...
                'Coefficient', obj.J,...
                'VertexType', 'AngularVelocity',...
                'DynamicType', 'StateFlow');
            
            V(2) = GraphVertex_External('Description', "Input Torque (T_m)",'VertexType','Torque', 'DynamicType', 'StateFlow');
            V(3) = GraphVertex_External('Description', "Drag Sink",'VertexType','Abstract');
            
            % Inputs
            
            % Edges
            E(1) = GraphEdge_Internal(...
                'PowerFlow',P(1),...
                'Coefficient',1,...
                'TailVertex',V(2),...
                'HeadVertex',V(1));
            
            E(2) = GraphEdge_Internal(...
                'PowerFlow',P(2),...
                'Coefficient',obj.K_Q,...
                'TailVertex',V(1),...
                'HeadVertex',V(3));
            
            g = Graph(V, E);
            obj.Graph = g;
            
            % Ouputs
            syms omega
            Thrust_Fun = symfun(omega^2, omega);
            O(1) = GraphOutput('Description', "Thrust", 'Function', Thrust_Fun, 'Breakpoints', {V(1)}, 'Coefficient', obj.K_T);
            
            obj.Graph.Outputs = O;
                          
            % Ports
            p(1) = ComponentPort('Description',"Torque Input",'Element',E(1));
            obj.Ports = p;
        end
        
    end
    
    methods

        
        function k_Q = lumpedToTorqueCoeff(obj, lumped_torque_coeff)
            k_Q = lumped_torque_coeff/(pop(obj.rho)*pop(obj.D).^5); % rev/s
        end
        
        function k_T = lumpedToThrustCoeff(obj, lumped_thrust_coeff)
            k_T = lumped_thrust_coeff/(pop(obj.rho)*pop(obj.D).^4); % rev/s
        end
        
        function torque = calcTorque(obj, speed)
            torque = pop(obj.K_Q)*(speed.^2);
        end
        
        function speed = RotorSpeed(obj, thrust)
            speed = sqrt(thrust/obj.K_T.Value); % Bandaid!  Need ParamFunctions class or something
        end
        
        function f = get.Fit(obj)
            f = obj.Surrogate.Fit;
        end
    end
    
    methods (Static)
        function k_rad_per_s = convCoeffToRadPerSec(k_rev_per_s)
            % Converts lumped coefficients of speed^2 term from rev/s to rad/s
            % w' = speed in rad/s
            % w = speed in rev/s
            % Thrust = k_rev_per_s * w^2 = k_rad_per_s * (w')^2
            
            k_rad_per_s = k_rev_per_s / (2*pi)^2;
        end
        
        function k_rev_per_s = convCoeffToRevPerS(k_rad_per_s)
            % Converts lumped coefficients of speed^2 term from rev/s to rad/s
            % w' = speed in rad/s
            % w = speed in rev/s
            % Thrust = k_rev_per_s * w^2 = k_rad_per_s * (w')^2
            
            k_rev_per_s = k_rad_per_s * (2*pi)^2;
        end
        
        function J = calcInertia(M,D)
            J = 1/12*M.*D.^2;
        end
        
        function k_Q = calcTorqueCoefficient(k_P, k_P_mod)
            k_Q = (k_P*k_P_mod) / (2*pi);
        end
        
        function K_Q = calcLumpedTorqueCoefficient(k_Q, rho, D)
            sdc = k_Q*rho*D^5; % rev/s
            K_Q = Propeller.convCoeffToRadPerSec(sdc); % rad/s
        end
        
        function K_T = calcLumpedThrustCoefficient(k_T, k_T_mod, rho, D)
            stc = (k_T*k_T_mod)*rho*D^4; % rev/s
            K_T = Propeller.convCoeffToRadPerSec(stc); % rad/s
        end
    end
end

