classdef PlanarPT_InitialDesign < PlanarPowerTrain
    methods
        %% HolyBro S500
        % https://shop.holybro.com/s500-v2-kitmotor2216-880kv-propeller1045_p1153.html
        function obj = PlanarPT_InitialDesign(opts)
            arguments
                opts.VariableVOCV = false;
            end
            %% Battery
            % - Recommended: 4S, 5000 mAh.  Used 4s,4000mAh
            batt = Battery('Name', 'Battery',...
                'Q', compParam('Q',4000,'Unit', 'mAh', 'AutoRename', true, 'Tunable', true),...
                'N_p', compParam('N_p',1,'Unit', 'unit', 'AutoRename', true, 'Tunable', true),...
                'N_s', compParam('N_s',4, 'Unit', 'unit', 'AutoRename', true, 'Tunable', true),... % 4000mAh, No Dynamics
                'R_s', compParam('R_s', .004, 'Unit', "Ohm", 'AutoRename', true, 'Tunable', true),... % Measured with Battery Charger, likely not very accurate.  R_s = N_p/N_s R_p
                'Mass', extrinsicProp('Mass', 0.47735, 'Unit',"kg", 'AutoRename', true, 'Tunable', true),...
                'Price', extrinsicProp('Price', 59.99, 'Unit', "USD", 'AutoRename', true, 'Tunable', false),...
                'V_OCV_nominal', compParam('V_OCV_nom', 3.7, 'Unit', 'V', 'AutoRename', true, 'Tunable', false),...
                'variableV_OCV', opts.VariableVOCV);
            batt.OperatingSOCRange = [0.2 1];
            
            %% DC Bus
            bus = DCBus_CurrentEquivalence('Name', 'DCBus',...
                'R', compParam('R', 0.003, 'Unit', "Ohm", 'AutoRename', true, 'Tunable', false),...
                'N_inputs',1,...
                'N_outputs',2);
            
            %% ESC (Inverter)
            esc = PMSMInverter('Name', 'PMSMInverter',...
                'I_max', compParam('I_max', 20, 'Unit', "A", 'AutoRename', true, 'Tunable', false),...
                'R_1', compParam('R_1', 0.1, 'Unit', "Ohm", 'AutoRename', true, 'Tunable', false),...
                'Mass', extrinsicProp('Mass', 0.026, 'Unit', "kg", 'AutoRename', true, 'Tunable', false),...
                'Price', extrinsicProp('Price', 11.5, 'Unit', "USD", 'AutoRename', true, 'Tunable', false)); % Measured
            
            %% Motor
            motor = PMSMMotor('Name','Motor',...
                'Mass', extrinsicProp('Mass',0.0656, 'AutoRename', true, 'Tunable', true, 'Unit', "kg"),... % Measured mass
                'L', compParam('L', 0, 'AutoRename', true, 'Tunable', false, 'Unit', "H"),...
                'J', compParam('J', NaN, 'AutoRename', true, 'Tunable', true, 'Unit', "kg*m^2"),...
                'D', compParam('D', 0.03, 'AutoRename', true, 'Tunable', true, 'Unit', "m"),... % Need to measure this
                'kV', compParam('kV', 880, 'AutoRename', true, 'Tunable', true, 'Unit', "RPM/V"),...
                'Rm', compParam('Rm',0.108, 'AutoRename', true, 'Tunable', true, 'Unit', "Ohm"),... % Estimate https://www.rcmoment.com/p-rm6909.html
                'Price', extrinsicProp('Price', 19.90, 'Unit', "USD", 'AutoRename', true, 'Tunable', false));
            motor.J.Dependent = true; % Use the estimate function from PMSMMotor since we don't know the actual value
            
            %% Propeller
            D = 10*(u.in/u.m);
            P = 4.5*(u.in/u.m);
            
            prop = Propeller('Name', 'Propeller',...
                'k_P', compParam('k_P',  NaN, 'AutoRename', true, 'Tunable', true) ,... % Power coefficient - k_P = 2*pi*k_Q, speed in rev/s
                'k_T', compParam('k_T', NaN, 'AutoRename', true, 'Tunable', true),... % Thrust coefficient - N/(s^2*kg*m^2), speed in rev/s.
                'k_P_mod', compParam('k_P_mod',  NaN, 'AutoRename', true, 'Tunable', true) ,... % Power coefficient modifier
                'k_T_mod', compParam('k_T_mod', NaN, 'AutoRename', true, 'Tunable', true),... % Thrust coefficient modifier
                'D', compParam('D', D, 'AutoRename', true, 'Tunable', true, 'Unit', "m"),...
                'P', compParam('P', P, 'AutoRename', true, 'Tunable', true, 'Unit', "m"),...
                'Mass', extrinsicProp('Mass', 0.012275, 'AutoRename',true,'Tunable',true, 'Unit', "kg"),...
                'J', compParam('J', NaN, 'AutoRename', true, 'Tunable',true, 'Unit', "kg*m^2"),...
                'Price', extrinsicProp('Price', 2.475, 'Unit', "USD", 'AutoRename', true, 'Tunable', false));
            
            prop.J.Dependent = true; % Use the estimate function from PMSMMotor since we don't know the actual value
            prop = setQRS500AeroCoeffs(prop); % Sets k_P and k_T from experimental data
            prop.k_P_mod.Value = 1.25; % Initial Design Modifier
            prop.k_T_mod.Value = 0.85;
            
            %% Initialize Object
            obj = obj@PlanarPowerTrain('Battery', batt, 'DCBus', bus, 'PMSMInverter', esc, 'Propeller', prop, 'PMSMMotor', motor);
    
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
            prop_CD = obj.Propeller.Surrogate.CD.FilteredCD;
            prop_table = table(prop_CD);
            prop_I = (prop_table.D == 0.2286) & (prop_table.P == 0.1143);
            prop = prop_CD(prop_I);
            
            %%
            comps = [batt, motor, prop];
            loadValues(obj.Params, comps);
            obj.Params.update();
        end
    end
end