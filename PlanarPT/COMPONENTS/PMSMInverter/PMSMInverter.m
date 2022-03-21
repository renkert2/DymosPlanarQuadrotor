classdef PMSMInverter < Component
    properties
        InverterType InverterTypes = InverterTypes.VoltageDependent
    end
    properties (SetAccess = private)
        I_max Param
        L Param
        C Param
        R Param
        R_2 Param
        
        Mass extrinsicParam
        Price extrinsicParam
    end
    
    methods (Access = protected)
        function DefineParams(obj)
            obj.I_max = Param("I_max",20,'Unit',"A",'Description',"Rated Current",'Tunable',true); %Rated Current - Amps
            obj.L = Param("L", 0, 'Unit', "H", 'Description', "Inductance", 'Tunable', true);
            obj.C = Param("C", 0, 'Unit', "F", 'Description', "Capacitance", 'Tunable', true);
            obj.R = Param("R", 0.01, 'Unit', 'Ohm','Description', "Resistance", 'Tunable', true);
            obj.R_2 = Param("R_2", 0, 'Unit', 'Ohm','Description', "Resistance", 'Tunable', true);
            
            obj.Mass = extrinsicParam('Mass', 0.03, 'Unit', "kg", 'Tunable', true);
            obj.Price = extrinsicParam('Price', NaN, 'Unit', "USD", 'Tunable', true);
        end
        function DefineComponent(obj)
            % Capacitance Types
            C(1) = Type_Capacitance("x");
            
            % PowerFlow Types
            P(1) = Type_PowerFlow("xt*xh");
            P(2) = Type_PowerFlow("u1*xt*xh");
            P(3) = Type_PowerFlow("xt^2");

            % Internal Vertices
            desc = ["DC Inductance", "q Capacitance"];
            type = [VertexTypes.Current, VertexTypes.Voltage];
            cap = C(1);
            coeff = [obj.L, obj.C];
            init = 0;
            for i = 1:2
                V(i) = GraphVertex_Internal('Description',desc(i),'Capacitance',cap,'Coefficient',coeff(i),'Initial',init, 'VertexType', type(i),'DynamicType', 'StateFlow');
            end
            
            % External Vertices
            desc = ["Input Voltage (DC)", "Output Current (q)", "Heat Sink"];
            type = [VertexTypes.Voltage, VertexTypes.Current, VertexTypes.Temperature];
            dyntype = ["StateFlow", "StateFlow", "EnergyFlow"];
            for i = 1:3
                V(i+2) = GraphVertex_External('Description',desc(i), 'VertexType', type(i), 'DynamicType', dyntype(i));
            end
            
            % Inputs
            I(1) = GraphInput("d");
            
            % Edges
            E(1) = GraphEdge_Internal('PowerFlow',P(2),'Coefficient',1,'TailVertex',V(3),'HeadVertex',V(1), 'Input', I(1));
            E(2) = GraphEdge_Internal('PowerFlow',P(1),'Coefficient',sqrt(2/3),'TailVertex',V(1),'HeadVertex',V(2));
            E(3) = GraphEdge_Internal('PowerFlow',P(1),'Coefficient',1,'TailVertex',V(2),'HeadVertex',V(4));
            
            if obj.InverterType == InverterTypes.ConstantLoss
                P(4) = Type_PowerFlow("xt");
                E(4) = GraphEdge_Internal('PowerFlow',[P(3) P(4)],'Coefficient',[obj.R obj.R_2],'TailVertex',V(1),'HeadVertex',V(5));
            elseif obj.InverterType == InverterTypes.VoltageDependent
                P(4) = Type_PowerFlow("u1*xt");
                E(4) = GraphEdge_Internal('PowerFlow',[P(3) P(4)],'Coefficient',[obj.R obj.R_2],'TailVertex',V(1),'HeadVertex',V(5), 'Input', I(1));
            elseif obj.InverterType == InverterTypes.CurrentDependent
                P(4) = Type_PowerFlow("(1/u1)*xt^2");
                E(4) = GraphEdge_Internal('PowerFlow',[P(3) P(4)],'Coefficient',[obj.R obj.R_2],'TailVertex',V(1),'HeadVertex',V(5), 'Input', I(1)); 
            else
                error('Invalid InverterType')
            end
            
            g = Graph(V, E);
            obj.Graph = g;
            
            p(1) = ComponentPort('Description',"Voltage Input (DC)",'Element',obj.Graph.Edges(1));
            p(2) = ComponentPort('Description',"Current Output (q)",'Element',obj.Graph.Edges(3));
            p(3) = ComponentPort('Description',"Heat Sink",'Element',obj.Graph.Vertices(5));
            obj.Ports = p;
        end
    end
end

