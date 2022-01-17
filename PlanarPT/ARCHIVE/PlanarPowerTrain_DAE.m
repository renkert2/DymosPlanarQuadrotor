%% Make Full DAE Model

%Nx,Na,Nu,Nd,Ny,Ntheta
sv = DAEDesignSymVars(3,8,2,0,4,18);
x = sv.x;
a = sv.a;
u = sv.u;
y = sv.y;
theta = sv.theta;

% DYNAMIC STATES
% x1: Battery SOC
% x2: Rotor 1 Speed
% x3: Rotor 2 Speed
x.Descriptions = ["Battery SOC", "Rotor 1 Speed", "Rotor 2 Speed"];

% ALGEBRAIC STATES
% a1: Bus Voltage
% a2: Bus Current
% a3: Inverter Current
% a4: Inverter Voltage
% a5: Inverter 2 Current
% a6: Inverter 2 Voltage
% a7: Motor 1 Inductance
% a8: Motor 2 Inductance
a.Descriptions = ... 
    ["Bus Voltage";
    "Bus Current";
    "Inverter Current";
    "Inverter Voltage";
    "Inverter 2 Current";
    "Inverter 2 Voltage";
    "Motor 1 Inductance";
    "Motor 2 Inductance";
    ];

% OUTPUTS
y.Descriptions = ...
    ["Rotor 1 Thrust";
    "Rotor 1 Torque";
    "Rotor 2 Thrust";
    "Rotor 2 Torque"];

% PARAMETERS
% theta1: D__Motor
% theta(2): D__Propeller
% theta(3): J__Motor
% theta(4): J__Propeller
% theta(5): N_p__Battery
% theta(6): N_s__Battery
% theta7: P__Propeller
% theta(8): Q__Battery
% theta(9): R_s__Battery
% theta(10): Rm__Motor
% theta(11): kV__Motor
% theta12: k_P__Propeller
% theta(13): k_P_mod__Propeller
% theta(14): k_T__Propeller
% theta(15): k_T_mod__Propeller
% theta16: Mass__Battery
% theta17: Mass__Motor
% theta18: Mass__Propeller
theta.Descriptions = ...
    ["D__Motor";
    "D__Propeller";
    "J__Motor";
    "J__Propeller";
    "N_p__Battery";
    "N_s__Battery";
    "P__Propeller";
    "Q__Battery";
    "R_s__Battery";
    "Rm__Motor";
    "kV__Motor";
    "k_P__Propeller";
    "k_P_mod__Propeller";
    "k_T__Propeller";
    "k_T_mod__Propeller";
    "Mass__Battery";
    "Mass__Motor";
    "Mass__Propeller"];

x = x.Syms;
a = a.Syms;
u = u.Syms;
theta = theta.Syms;

Rh = [a(2) - u(1)*a(3) - u(2)*a(5);
    -(0.0010*(1000*theta(5)*a(1) + 3*theta(5)*a(2) - 3700*theta(5)*theta(6) + 1000*theta(6)*theta(9)*a(2)))/theta(5);
    u(1)*a(1) - 0.8165*a(4) - 0.1000*a(3);
    0.8165*a(3) - a(7);
    u(2)*a(1) - 0.8165*a(6) - 0.1000*a(5);
    0.8165*a(5) - a(8);
    -(0.3183*(36.7423*x(2) - 3.1416*theta(11)*a(4) + 3.1416*theta(10)*theta(11)*a(7)))/theta(11);
    -(0.3183*(36.7423*x(3) - 3.1416*theta(11)*a(6) + 3.1416*theta(10)*theta(11)*a(8)))/theta(11)];

f = [-(0.2778*a(2))/(theta(5)*theta(8));
    (4.5832e-18*(- 1.0599e+15*theta(11)*theta(7)*theta(13)*theta(2)^5*x(2)^2 + 2.5518e+18*a(7)))/(theta(11)*(theta(3) + theta(4)));
    (4.5832e-18*(- 1.0599e+15*theta(11)*theta(7)*theta(13)*theta(2)^5*x(3)^2 + 2.5518e+18*a(8)))/(theta(11)*(theta(3) + theta(4)))];

g = [0.0305*theta(2)^4*theta(14)*theta(15)*x(2)^2;
    0.0049*theta(2)^5*theta(7)*theta(13)*x(2)^2;
    0.0305*theta(2)^4*theta(14)*theta(15)*x(3)^2;
    0.0049*theta(2)^5*theta(7)*theta(13)*x(3)^2];

full_model = DAEDesignModel(sv);
full_model.Rh = Rh;
full_model.f = f;
full_model.g = g;

%% Make Simple DAE Model for Steady State
sv = DAEDesignSymVars(1,5,1,0,1,18);
x = sv.x;
a = sv.a;
u = sv.u;
y = sv.y;
theta = sv.theta;

% DYNAMIC STATES
% x1: Rotor Speed
x.Descriptions = ["Rotor Speed"];

% ALGEBRAIC STATES
% a1: Bus Voltage
% a2: Bus Current
% a3: Inverter Current
% a4: Inverter Voltage
% a5: Inverter 2 Current -> a(3)
% a6: Inverter 2 Voltage -> a(4)
% a7: Motor 1 Inductance -> a(5)
% a8: Motor 2 Inductance -> a(5)

a.Descriptions = ... 
    ["Bus Voltage";
    "Bus Current";
    "Inverter Current";
    "Inverter Voltage";
    "Motor Inductance";
    ];

% PARAMETERS
% theta1: D__Motor
% theta(2): D__Propeller
% theta(3): J__Motor
% theta(4): J__Propeller
% theta(5): N_p__Battery
% theta(6): N_s__Battery
% theta7: P__Propeller
% theta(8): Q__Battery
% theta(9): R_s__Battery
% theta(10): Rm__Motor
% theta(11): kV__Motor
% theta12: k_P__Propeller
% theta(13): k_P_mod__Propeller
% theta(14): k_T__Propeller
% theta(15): k_T_mod__Propeller
% theta16: Mass__Battery
% theta17: Mass__Motor
% theta18: Mass__Propeller
theta.Descriptions = ...
    ["D__Motor";
    "D__Propeller";
    "J__Motor";
    "J__Propeller";
    "N_p__Battery";
    "N_s__Battery";
    "P__Propeller";
    "Q__Battery";
    "R_s__Battery";
    "Rm__Motor";
    "kV__Motor";
    "k_P__Propeller";
    "k_P_mod__Propeller";
    "k_T__Propeller";
    "k_T_mod__Propeller";
    "Mass__Battery";
    "Mass__Motor";
    "Mass__Propeller"];

% OUTPUTS
y.Descriptions = ...
    ["Total Thrust"];

x = x.Syms;
a = a.Syms;
u = u.Syms;
theta = theta.Syms;

Rh = [a(2) - 2*u(1)*a(3);
    -(0.0010*(1000*theta(5)*a(1) + 3*theta(5)*a(2) - 3700*theta(5)*theta(6) + 1000*theta(6)*theta(9)*a(2)))/theta(5);
    u(1)*a(1) - 0.8165*a(4) - 0.1000*a(3);
    0.8165*a(3) - a(5);
    -(0.3183*(36.7423*x(1) - 3.1416*theta(11)*a(4) + 3.1416*theta(10)*theta(11)*a(5)))/theta(11)];

f = (4.5832e-18*(- 1.0599e+15*theta(11)*theta(7)*theta(13)*theta(2)^5*x(1)^2 + 2.5518e+18*a(5)))/(theta(11)*(theta(3) + theta(4)));
g = 2*0.0305*theta(2)^4*theta(14)*theta(15)*x(1)^2;

simple_model = DAEDesignModel(sv);
simple_model.Rh = Rh;
simple_model.f = f;
simple_model.g = g;


%% Export Models
opts = exportoptions(full_model, 'Method', 'PythonFunction', 'FlattenJacobian', true, 'ExportMetadata', true);
opts.Directory = "PlanarPowerTrainModel";
full_model.export(opts)
opts.Directory = "PlanarPowerTrainModel_Simple";
simple_model.export(opts)
