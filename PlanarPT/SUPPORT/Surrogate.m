classdef Surrogate < handle & matlab.mixin.Heterogeneous
    %SURROGATE Summary of this class goes here
    %   Detailed explanation goes here
    
    properties (Abstract)
        ComponentName string
        CD ComponentData
        Fit paramFit
    end
    
    methods (Sealed)
        function S = export(obj_array, opts)
            arguments
                obj_array
                opts.SamplePoints = 100
                opts.ExportFile logical = false
                opts.FilePath string = "./SurrogateMetadata"
            end
            
            for i = 1:numel(obj_array)
                obj = obj_array(i);
                
                S(i).ComponentName = obj.ComponentName;
                
                % Export Fits
                S(i).Fits = obj.Fit.export('ExportFile', false, 'SamplePoints', opts.SamplePoints);

                % Export Boundaries?
                S(i).Boundary = obj.Fit.Boundary.export('ExportFile', false);
            
                % Export ComponentData
                S(i).ComponentData = export(obj.CD, 'ExportFile', false);
            end
            
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
        

end

