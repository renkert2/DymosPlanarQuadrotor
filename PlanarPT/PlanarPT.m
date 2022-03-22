% Construct the PlanarPowerTrain System
ppt = PlanarPT_InitialDesign();
ppt.Params.update()

%% Get the System Model
ppt.createModel();
gm = ppt.Model;
opts = graphmodeloptions('ReduceDisturbances', true, 'SolveAlgebraics', false);
m = gm.Convert(opts);

%% Export the System Model
opts = exportoptions(m, "Method", "PythonFunction", 'Directory', "PlanarPTModelDAE", "ExportJacobians", true, "FlattenJacobian", true, "ExportVariableMetadata", true, "CleanParsing", false);
m.export(opts)

%% Simplify the Model
sv_simple = SymVars("DAE", [1,5,1,0,1,m.SymVars.theta.N]);

% DYNAMIC STATES
% x1: Rotor Speed
sv_simple.x.Descriptions = ["Rotor Speed"];
f = m.f.Sym(2);

% INPUTS
sv_simple.u.Descriptions = ["Inverter Input"];

% ALGEBRAIC STATES
% a1: Bus Voltage
% a2: Bus Current
% a3: Inverter Current
% a4: Inverter Voltage
% a5: Inverter 2 Current -> a(3)
% a6: Inverter 2 Voltage -> a(4)
% a7: Motor 1 Inductance -> a(5)
% a8: Motor 2 Inductance -> a(5)
sv_simple.a.Descriptions = ... 
    ["Bus Voltage";
    "Bus Current";
    "Inverter Current";
    "Inverter Voltage";
    "Motor Inductance";
    ];
h = m.h.Sym([1,2,3,4,7]);

% OUTPUTS
sv_simple.y.Descriptions = ...
    ["Total Thrust"];
g = 2*m.g.Sym(1);

% PARAMETERS
% Shared with Full Model
sv_simple.theta.Name = m.SymVars.theta.Name;
sv_simple.theta.Descriptions = m.SymVars.theta.Descriptions;
sv_simple.theta.Units = m.SymVars.theta.Units;
sv_simple.theta.Syms = m.SymVars.theta.Syms;
sv_simple.theta.SymsString = m.SymVars.theta.SymsString;
sv_simple.theta.Values = m.SymVars.theta.Values;

% SUBS
subs_from = [sym('x2'), sym('u2'), sym('a5'), sym('a6'), sym('a7'), sym('a8')];
subs_to = [sym('x1'), sym('u1'), sym('a3'), sym('a4'), sym('a5'), sym('a5')];

f = subs(f, subs_from, subs_to);
h = subs(h, subs_from, subs_to);
g = subs(g, subs_from, subs_to);

m_simple = Model(sv_simple, 'f', f, 'h', h, 'g', g);

%% Export the Simple Model
opts = exportoptions(m_simple, "Method", "PythonFunction", 'Directory', "PlanarPTModelSimple", "ExportJacobians", true, "FlattenJacobian", true, "ExportVariableMetadata", true, "CleanParsing", false);
m_simple.export(opts)


%% Export the Parameters
p = ppt.Params;
p.export('ExportMethod', "JSON", 'FilePath', "PlanarPTModelDAE/ParamMetadata.json", "FilterTunable", true);
