classdef paramFit < handle
    % Wraps Curve Fitting Toolbox fits used for data-based surrogate models
    % that use continuous functions to estimate dependent Params from
    % other Params
    properties
        Inputs (:,1) Param
        Outputs (:,1) Param
        
        FitTypes (:,1) cell
        FitOpts (:,1) cell % cell of structs
        
        BoundaryWarning logical = true
    end
    
    properties (SetAccess = private)
        Data (:,1) struct % Struct array (obj.N_outs, 1), each with Inputs and Outputs field for use with model creation
        Boundary Boundary
        Models (:,1) cell % Cell array of fit objects or function handles
        Functions (:,1) cell % Cell array of function handles, wrap Models with additional functionality like boundary checking
    end
    
    properties (SetAccess = private)
        N_ins double = []
        N_outs double = []
    end
    
    methods
        function obj = paramFit(ins, outs)
            if nargin == 2
                if isa(ins, 'Param') && isa(outs, 'Param')
                    obj.Inputs = ins;
                    obj.Outputs = outs;
                elseif isnumeric(ins) && isnumeric(outs)
                    mustBeInteger(ins);
                    mustBeInteger(outs);
                    obj.N_ins = ins;
                    obj.N_outs = outs;
                else
                    error("invalid constructor arguments.  Must be the input and output Params arrays or the number of inputs and outputs")
                end
            end
        end
        
        function set.Inputs(obj, ins)
            obj.Inputs = ins;
            obj.N_ins = numel(ins);
            if ~isempty(obj.Boundary)
                args = [obj.Inputs.StrID];
                obj.Boundary.Args = args;
            end
        end
        
        function set.Outputs(obj, outs)
            obj.Outputs = outs;
            obj.N_outs = numel(outs);
        end
        
        function set.FitTypes(obj, types)
            if obj.N_outs
                assert(numel(types) == obj.N_outs, "Each output must be associated with a fit")
            end
            obj.FitTypes = types;
        end
        
        function set.FitOpts(obj, opts)
            if obj.N_outs
                assert(numel(opts) == obj.N_outs, "Each output must be associated with a fit")
            end
            obj.FitOpts = opts;
        end
        
        function setData(obj, input_data, output_data)
            N_points = size(input_data,1);
            assert(N_points == size(output_data,1), 'Input and Output Data must have equal number of rows');
            
            for i = 1:obj.N_outs
                [obj.Data(i,1).Inputs, obj.Data(i,1).Outputs] = prepareData(obj, input_data, output_data(:,i));
            end
        end
        
        function setBoundary(obj)
            args = [obj.Inputs.StrID];
            obj.Boundary = Boundary(obj.Data(1).Inputs, args);
        end
        
        function setModels(obj, fit_type, fit_opts)
            arguments
                obj
            end
            arguments (Repeating)
                fit_type
                fit_opts
            end
            if nargin > 1
                obj.FitTypes = fit_type;
                obj.FitOpts = fit_opts;
            end
            
            for i = 1:obj.N_outs
                model = makeFit(obj, obj.Data(i).Inputs, obj.Data(i).Outputs, obj.FitTypes{i}, obj.FitOpts{i});
                obj.Models{i} = model;
                obj.Functions{i} = makeModelWrapper(obj,model);
            end
            
            if ~isempty(obj.Outputs)
                setOutputDependency(obj);
            end
            
            function fh = makeModelWrapper(obj,model)
                fh = @ModelWrapper;
                
                function out = ModelWrapper(varargin)
                    if obj.BoundaryWarning
                        if all(isnumeric([varargin{:}]))
                            in_bounds = obj.Boundary.isInBoundary(varargin{:});
                            if any(~in_bounds)
                                out_i = find(~in_bounds);
                                out_str = num2str(out_i, '%d, ');
                                warning("Points %s Outside Boundary", out_str)
                            end
                        end
                    end
                    out = model(varargin{:});
                    % Can add post process functionality like LB < out < UB later
                end
            end
        end
        
        function setOutputDependency(obj)
            for i = 1:obj.N_outs
                f = obj.Functions{i};
                setDependency(obj.Outputs(i), f, obj.Inputs);
            end
        end
        
        function setSpan(obj, span)
           assert(isnumeric(span) && span >= 0 && span <= 1, "Span must be between 0 and 1");
           for i = 1:obj.N_outs
               ft = obj.FitTypes{i};
               if checkL(ft)
                   obj.FitOpts{i}.Span = span;
               end
           end
           setModels(obj);
           
            function i = checkL(ft)
               t = string(type(ft));
               i = (t == "lowess" | t == "loess");
            end
        end
        
        function outs = calcParams(obj, varargin)
            outs = zeros(obj.N_outs,1);
            for i = 1:obj.N_outs
                f = obj.Functions{i};
                outs(i,1) =  f(varargin{:});
            end
        end
        
        function p = plot(obj, opts)
            arguments
                obj
                opts.Outputs = 1:obj.N_outs
            end
            
            if ~isempty(obj.Inputs) && ~isempty(obj.Outputs)
                ins = {obj.Inputs.Value};
                outs = calcParams(obj, ins{:});
            else
                ins = {};
                outs = [];
            end
            
            out_plts = opts.Outputs;
            f = figure();
            t = tiledlayout(f,1,numel(out_plts));
            
            for i = 1:numel(out_plts)
                nexttile(t,i)
                
                out_I = out_plts(i);
                plot(obj.Models{out_I}, obj.Data(out_I).Inputs, obj.Data(out_I).Outputs);
                
                [olb,oub] = bounds(obj.Data(out_I).Outputs);
                
                switch obj.N_ins
                    case 1
                        pfun = @plot;
                        ylim([olb oub]);
                        if ~isempty(obj.Inputs)
                            xlabel(latex(obj.Inputs(1)),'Interpreter','latex');
                        end
                        if ~isempty(obj.Outputs)
                            ylabel(latex(obj.Outputs(out_I)),'Interpreter','latex');
                        end
                    case 2
                        pfun = @plot3;
                        zlim([olb oub]);
                        if ~isempty(obj.Inputs)
                            xlabel(latex(obj.Inputs(1)),'Interpreter','latex');
                            ylabel(latex(obj.Inputs(2)),'Interpreter','latex');
                        end
                        if ~isempty(obj.Outputs)
                            zlabel(latex(obj.Outputs(out_I)),'Interpreter','latex');
                        end
                end
                
                if ~isempty(outs)
                    hold on
                    pfun(ins{:}, outs(out_I),'or', 'MarkerSize',10, 'LineWidth', 2, 'MarkerEdgeColor', 'w', 'MarkerFaceColor','r')
                    hold off
                end
                p = gca;
            end
        end
        
        function p = plotBoundary(obj, varargin)
            plot(obj.Boundary, varargin{:});
            switch obj.N_ins
                case 1
                    xlabel(latex(obj.Inputs(1)),'Interpreter','latex');
                case 2
                    xlabel(latex(obj.Inputs(1)),'Interpreter','latex');
                    ylabel(latex(obj.Inputs(2)),'Interpreter','latex');
            end
            p = gca;
        end
        
        function cftool(obj, output_number)
            dat = obj.Data(output_number);
            switch obj.N_ins
                case 1
                    cftool(dat.Inputs(:,1),dat.Outputs);
                case 2
                    cftool(dat.Inputs(:,1),dat.Inputs(:,2),dat.Outputs);
            end
        end
    end
    methods (Sealed)
        function S = export(obj, opts)
            arguments
                obj
                opts.SamplePoints = 100
                opts.ExportFile logical = false
                opts.FilePath string = "./FitMetadata"
            end
            % Make Grid using Boundary
            B = obj.Boundary;
            if ~isempty(B)
                X_lb = B.X_lb;
                X_ub = B.X_ub;
            else
                % Get the max and min from the combined dataset for each model
                dat = vertcat(obj.Data.Inputs);
                X_lb = zeros(obj.N_ins,1);
                X_ub = zeros(obj.N_ins,1);
                for i = 1:obj.N_ins
                    X_lb(i,1) = min(dat(:,i));
                    X_ub(i,1) = max(dat(:,i));
                end
            end
            
            X_vec = {};
            for i = 1:obj.N_ins
                if isscalar(opts.SamplePoints)
                    N = opts.SamplePoints;
                else
                    N = opts.SamplePoints(i);
                end
                X_vec{i} = linspace(X_lb(i), X_ub(i), N);
            end
            
            X_grid = cell(obj.N_ins,1);
            [X_grid{:}] = ndgrid(X_vec{:});
            
            % Sample Surrogates over Grid
            bw_cache = obj.BoundaryWarning;
            obj.BoundaryWarning = false; % Temporarily disable boundary checking
            Y_grid = cell(obj.N_outs,1);
            for i = 1:obj.N_outs
                f = obj.Functions{i};
                Y_grid{i} = f(X_grid{:});
            end
            obj.BoundaryWarning = bw_cache;
            
            % Output Structures
            S = struct();
            S.Outputs = [obj.Outputs.StrID];
            S.OutputsName = [obj.Outputs.Name];
            S.Inputs = [obj.Inputs.StrID];
            S.InputsName = [obj.Inputs.Name];
            
            S.X_vec = X_vec;
            S.X_grid = X_grid;
            S.Y_grid = Y_grid;
            
            % Output to file
            if opts.ExportFile
                if verLessThan('matlab', '9.10')
                    jsonenc_args = {};
                else
                    jsonenc_args = {"PrettyPrint", true};
                end
                S_json = jsonencode(S, jsonenc_args{:});
                file_path = opts.FilePath;
                [path,name,~] = fileparts(file_path);
                file_path = fullfile(path, name); % Remove extension from path
                fname = file_path + ".json";
                f = fopen(fname, 'w');
                fprintf(f, S_json);
                fclose(f);
            end
        end
    end
    methods (Access = protected)
        function [inputs_out, outputs_out] = prepareData(obj, inputs_in, outputs_in)
            % Override in subclasses for custom data prep
            switch obj.N_ins
                case 1
                    [inputs_out, outputs_out] = prepareCurveData(inputs_in, outputs_in);
                case 2
                    [inputs_out(:,1), inputs_out(:,2), outputs_out] = prepareSurfaceData(inputs_in(:,1),inputs_in(:,2), outputs_in);
                otherwise
                    inputs_out = inputs_in;
                    outputs_out = outputs_in;
            end
        end
        
        function [model] = makeFit(obj, input_data, output_data, ft, fo)
            if obj.N_ins == 1 || obj.N_ins == 2
                model = fit(input_data, output_data, ft, fo);
            else
                error("paramFit.Models not compatible with more than two input variables")
            end
        end
    end
end

