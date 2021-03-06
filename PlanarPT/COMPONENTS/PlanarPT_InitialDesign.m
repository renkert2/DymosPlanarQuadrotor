classdef PlanarPT_InitialDesign < PlanarPowerTrain
    methods
        %% HolyBro S500
        % https://shop.holybro.com/s500-v2-kitmotor2216-880kv-propeller1045_p1153.html
        function obj = PlanarPT_InitialDesign()
            %% Battery
            % - Recommended: Used 4s,4000mAh
            batt = Battery('Name', "Battery",'Q',4000,'N_p',1,'N_s',4,'R_s',.004,'Mass', 0.47735,'Price', 59.99,'V_OCV_nominal', 3.7);
            batt.C.Tunable = false;
            batt.V_OCV_nominal.Tunable = false;
            
            %% DC Bus
            bus = DCBus_CurrentEquivalence('Name', 'DCBus', 'R', 0.003, 'N_inputs', 1, 'N_outputs', 2);
            bus.R.Tunable = false;
            
            %% ESC (Inverter)
            esc = PMSMInverter('Name', 'PMSMInverter', 'I_max', 20, 'R', 0.1,'Mass', 0.026,'Price', 11.5); % Measured
            esc.L.Tunable = false;
            esc.C.Tunable = false;
            esc.R_2.Tunable = false;
            
            %% Motor
            motor = PMSMMotor('Name','Motor', 'Mass',0.0656,'L', 0,'J', NaN,'D', 0.03, 'kV', 880,'Rm',0.108,'Price', 19.90);
            motor.B_v.Tunable = false;
            motor.L.Tunable = false;
            
            %% Propeller
            D = 10*0.0254; % m
            P = 4.5*0.0254; % m
            
            prop = Propeller('Name', 'Propeller', 'k_P',  NaN,'k_T', NaN,'k_P_mod',  NaN, 'k_T_mod', NaN,'D', D,'P', P,'Mass', 0.012275,'J', NaN,'Price', 2.475);
            prop.k_P_mod.Value = 1.25; % Initial Design Modifier
            prop.k_T_mod.Value = 0.85;
            prop.rho.Tunable = false;
            
            prop = setQRS500AeroCoeffs(prop); % Sets k_P and k_T from experimental data
            
            %% Initialize Object
            obj = obj@PlanarPowerTrain('Battery', batt, 'DCBus', bus, 'PMSMInverter', esc, 'Propeller', prop, 'PMSMMotor', motor);
            
            % System Params
            obj.Mass.Tunable = true;
            obj.Price.Tunable = true;
            
            %% Select Components To Serve as Initial Design Point
            batt_CD = obj.Battery.Surrogate.CD;
            batt_table = table(batt_CD);
            batt_I = (batt_table.N_s == 4) & (batt_table.Q == 4000);
            batt = batt_CD(batt_I);
            %%
            motor_CD = obj.Motor.Surrogate.CD;
            motor_table = table(motor_CD);
            motor_I = (motor_table.kV == 965) & (motor_table.Rm == 0.102);
            motor = motor_CD(motor_I);
            %%
            prop_CD = obj.Propeller.Surrogate.CD;
            prop_table = table(prop_CD);
            prop_I = (prop_table.D == 0.2286) & (prop_table.P == 0.1143);
            prop = prop_CD(prop_I);
            
            %%
            comps = [batt, motor, prop];
            load(obj.Params, vertcat(comps.Data));
            obj.Params.update();
        end
    end
end