ppt = PlanarPT_InitialDesign();

%% Get Tunable Params
params = ppt.Params;
params = params(isTunable(params));

param_struct = struct();
for i = 1:numel(params)
    p = params(i);
    s = struct();
    s.Value = p.Value;
    s.Unit = p.Unit;
    s.Description = p.Description;
    
    param_struct.(p.SymID) = s;
end

ParamMetadata = param_struct;
save ParamMetadata.mat ParamMetadata

