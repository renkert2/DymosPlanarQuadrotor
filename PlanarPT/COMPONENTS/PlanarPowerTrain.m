classdef PlanarPowerTrain < System
    %POWERTRAINMODEL Summary of this class goes here
    %   Detailed explanation goes here
    properties (SetAccess = private)
        Battery Battery
        DCBus DCBus_CurrentEquivalence
        Inverter PMSMInverter
        Motor PMSMMotor
        Propeller Propeller
        MotorProp MotorProp
        
        Mass extrinsicParam
        Price extrinsicParam
    end
    
    methods
        function obj = PlanarPowerTrain(p)
            arguments
                p.Battery Battery = Battery('Name', "Battery");
                p.DCBus DCBus_CurrentEquivalence = DCBus_CurrentEquivalence('Name', 'Bus', 'N_inputs',1,'N_outputs',2);
                p.PMSMInverter PMSMInverter = PMSMInverter('Name', "Inverter");
                p.PMSMMotor PMSMMotor = PMSMMotor('Name', "Motor");
                p.Propeller Propeller = Propeller('Name', "Propeller");
            end
            
            pmsminverters = Replicate([p.PMSMInverter], 2);
            pmsminverters = pmsminverters{1};
            
            motorprop = MotorProp('PMSMMotor', p.PMSMMotor, 'Propeller', p.Propeller);
            motorprops = Replicate(motorprop, 2, 'RedefineParams', false, 'RedefineElement', true, 'RedefineChildren', false);
            motorprops = vertcat(motorprops{:});
            
            Components = [p.Battery; p.DCBus; pmsminverters; motorprops];
            
            ConnectP = {[p.Battery.Ports(1) p.DCBus.Ports(1)]};
            
            for i = 1:2
                ConnectP{end+1,1} = [pmsminverters(i).Ports(1),p.DCBus.Ports(1+i)];
                ConnectP{end+1,1} = [pmsminverters(i).Ports(2), motorprops(i).Ports(1)];
            end
            
            obj = obj@System("PlanarPowerTrain", Components, ConnectP);
            obj.Battery = p.Battery;
            obj.DCBus = p.DCBus;
            obj.Inverter = p.PMSMInverter;
            obj.Motor = p.PMSMMotor;
            obj.Propeller = p.Propeller;
            obj.MotorProp = motorprop;
            
            init_post(obj);
        end
        
        function init_post(obj)
            params = obj.Params;
            params = params([params.Parent] == obj);
            obj.Mass = params([params.Name] == "Mass");
            obj.Price = params([params.Name] == "Price");
        end
    end
end

