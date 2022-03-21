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

%% Export the Parameters
p = ppt.Params;
p.export('ExportMethod', "JSON", 'FilePath', "PlanarPTModelDAE/ParamMetadata.json", "FilterTunable", true);
