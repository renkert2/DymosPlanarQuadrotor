classdef ComponentData
    %Value class encapsulating data corresponding to a physical component
    % It contains an array of compParamValues in its Data property that are
    % used to replace the values of system element parameters.  
    
    properties
        Component string % Corresponds to Component class name
        Make string
        Model string
        SKU string
        Description string
        
        Data (:,1) ParamValue
    end
    
    methods
        function obj = ComponentData(comp, make, model, data)
            if nargin == 1
                assert(isa(comp, "SystemElement"), "Single argument must be of type Component");
                
                obj = ComponentData.empty(numel(comp),0);
                for i = 1:numel(comp)
                    obj(i).Component = string(class(comp(i)));
                    obj(i).Data = export(comp(i).Params, 'FilterTunable', false, 'ExportMethod', "ParamValue");
                    for j = 1:numel(obj(i).Data)
                        obj(i).Data(j).Component = obj(i).Component;
                    end
                end
            elseif nargin > 1
                obj.Component = comp;
                obj.Make = make;
                obj.Model = model;
                obj.Data = data(:);

                for i = 1:numel(obj.Data)
                    obj.Data(i).Component = obj.Component;
                end
            end
        end
        
        function [cd_filtered, I] = filterComponent(obj_array, components)
            I = zeros(numel(obj_array),1);
            for i = 1:numel(components)
                I = I | vertcat(obj_array.Component) == components(i);
            end
            cd_filtered = obj_array(I);
        end
        
        function [tbl,param_table] = table(obj_array, opts)
            arguments
                obj_array
                opts.Display = false;
            end
            
            comps = unique([obj_array.Component]);
            N = numel(comps);
            if N == 1
                [tbl, param_table] = makeTable(obj_array);
            else
                tbls = cell.empty(0,N);
                fields = cell.empty(0,N);
                param_table = cell.empty(0,N);
                common_fields = string.empty();
                for c = 1:N
                    [tbls{c}, param_table{c}] = makeTable(filterComponent(obj_array, comps(c)));
                    fields{c} = string(tbls{c}.Properties.VariableNames);
                    if c == 1
                        common_fields = fields{c};
                    else
                        common_fields = intersect(common_fields, fields{c});
                    end
                end
                common_tbls = cell.empty(0,N);
                for c = 1:N
                    FI = arrayfun(@(f) ismember(f,common_fields), fields{c});
                    common_tbls{c} = tbls{c}(:,FI);
                end
                tbl = [tbls, {vertcat(common_tbls{:})}];
            end

            function [tbl, param_table] = makeTable(obj_array)
                pdat_all = vertcat(obj_array.Data);
                [params, I] = unique(vertcat(pdat_all.Name));
                unique_pdat = pdat_all(I);
                
                
                if opts.Display
                    param_table_full = table(unique_pdat);
                else
                    param_table_full = dispTable(unique_pdat);
                end
                
                pvars = string(param_table_full.Properties.VariableNames);
                pvi = pvars ~= "Value";
                param_table = param_table_full(:,pvi);
                
                comp_fields = ["Make", "Model", "SKU"];
                varnames = [comp_fields, params'];
                if ~opts.Display
                    vartypes = [repmat("string",1,numel(comp_fields)) repmat("double",1,numel(params))];
                else
                    vartypes = [repmat("string",1,numel(comp_fields)) repmat("string",1,numel(params))];
                end
                tbl = table('Size', [numel(obj_array), numel(varnames)], 'VariableTypes', vartypes, 'VariableNames', varnames);
                for i = 1:numel(obj_array)
                    for f = comp_fields
                        val = obj_array(i).(f);
                        if isempty(val)
                            val = "";
                        end
                        tbl(i,:).(f) = val;
                    end
                    dat = obj_array(i).Data;
                    for j = 1:numel(params)
                        f = params(j);
                        cpv = dat([dat.Name] == f);
                        if isempty(cpv)
                            val = NaN;
                        else
                            N_cpv = numel(cpv);
                            if N_cpv ~= 1
                                error("Multiple ParamVals of same name")
                            else
                                val = cpv.Value;
                                if ~(isnumeric(val) && isscalar(val))
                                    sz = size(val);
                                    type = class(val);
                                    val = sprintf("%dx%d %s", sz(1), sz(2), type);
                                end
                            end
                        end
                        tbl(i,:).(f) = val;
                    end
                end
            end
        end
        
        function dispTable(obj_array, opts)
            arguments
               obj_array
               opts.ParamTable logical = false
            end
            
            comps = unique([obj_array.Component]);
            for c = comps
                fprintf("Component: %s \n", c)
                cpv_c = obj_array([obj_array.Component] == c);
                [t,tp] = table(cpv_c, 'Display', true);
                disp(t);
                if opts.ParamTable
                    disp(tp);
                end
                disp(newline);
            end
        end
        
        function tbl = summaryTable(obj_array)
            comp_fields = ["Component", "Make", "Model", "SKU", "Description"];
            
            tbldat = cell.empty(0,numel(comp_fields));
            for i = 1:numel(comp_fields)
                S = strings(numel(obj_array),1);
                for j = 1:numel(obj_array)
                    s = obj_array(j).(comp_fields(i));
                    if ~isempty(s)
                        S(j) = s;
                    end
                end
                tbldat{1,i} = S;
            end

            tbl = table(tbldat{:}, 'VariableNames', comp_fields);
        end
    end
    
    methods (Static)
        function obj_array = import(source)
            arguments
                source
            end
            
            if isstring(source) || ischar(source)
                file = source;
                [~,~,ext] = fileparts(file);
                
                if ismember(ext,[".xls", ".xlsx", ".csv"])
                    data = readcell(file, 'TextType', 'string', 'MissingRule', 'fill');
                    obj_array = importFromSpreadsheet(data);
                elseif ext == ".json"
                    raw = fileread(file);
                    json = jsondecode(raw); % Struct array, each element is a component
                    obj_array = importFromStruct(json);
                else
                    error("Invalid file extension");
                end
            elseif isa(source, 'struct')
                obj_array = importFromStruct(source);
            else
                error("Invalid source");
            end

            % Helper Functions
            function l = matchText(str,patt)
                if isa(str, 'string') || isa(str, 'char')
                    l = contains(str,patt, 'IgnoreCase', true);
                else
                    l = false;
                end
            end
            function obj_array = importFromStruct(s)
                N = numel(s);
                obj_array = ComponentData.empty(N,0);
                
                for i = 1:N
                    if isa(s,'cell')
                        comp_struct = s{i};
                    elseif isa(s,'struct')
                        comp_struct = s(i);
                    else
                        error('Input argument must be struct array or cell array of structs')
                    end
                    dat = comp_struct.Data;
                    cpv = ParamValue.import(dat);
                    for j = 1:numel(cpv)
                        cpv(j).Component = comp_struct.Component;
                    end
                    comp_struct.Data = cpv;
                    
                    cd = ComponentData();
                    field_names = string(fields(comp_struct))';
                    for f = field_names
                        cd.(f) = comp_struct.(f);
                    end
                    obj_array(i,1) = cd;
                end
            end
            function obj_array = importFromSpreadsheet(data)
                % Breakpoints: Component ; empty ; Parameter Data; empty ; Component Data
                first_col = data(:,1);
                [ir_comp,ic_comp] = find(cellfun(@(x) matchText(x,"Component"), data));
                [ir_param, ~] = find(cellfun(@(x) matchText(x,"Parameter"), data));
                [ir_data, ic_data] = find(cellfun(@(x) matchText(x,"Data"), data));
                
                % Read Component
                component = data{ir_comp,ic_comp+1};
                
                % Read Parameters
                param_props = [first_col{ir_param:ir_data-1}];
                param_data = data(ir_param:ir_data-1,2:end);
                missing_cols = all(cellfun(@ismissing, param_data),1);
                param_data = param_data(:,~missing_cols)';
                param_table = cell2table(param_data, 'VariableNames', param_props);
                params = param_table{:,1}';
                
                % Component Properties
                comp_props = rmmissing([data{ir_data+1,ic_data:end}]);
                
                % Get Data
                varnames = [comp_props params];
                data_table = cell2table(data(ir_data+2:end,:),'VariableNames',varnames);
                
                % Make Template for compParamValue array
                data_template = ParamValue.import(param_table);
                
                % Create ComponentData Array
                N = height(data_table);
                obj_array = ComponentData.empty(N,0);
                
                for i = 1:N
                    cd = ComponentData();
                    cd.Component = component;
                    for j = 1:numel(comp_props)
                        field = comp_props(j);
                        cd.(field) = data_table(i,:).(field);
                    end
                    
                    cpvdata = data_template;
                    for j = 1:numel(params)
                        cpvdata(j).Value = data_table(i,:).(params(j));
                        cpvdata(j).Component = component;
                    end
                    cd.Data = cpvdata;
                    obj_array(i,1) = cd;
                end
            end
        end
    end
end

