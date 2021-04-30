classdef StimMatrixMaker
    properties
        trigger_table
        nirs_f
        num_samples
        num_stims
        trigger_matrix
        trigger_ch_map
    end
    methods
        % Constructor.
        function this = StimMatrixMaker(trig_fpath, nirs_fpath)
            if nargin == 2     
                this.trigger_table = readtable(trig_fpath);
                this.nirs_f = load(nirs_fpath, '-mat');
                this.trigger_ch_map = DefineTriggerChannelMap( this );
                [this.trigger_matrix, this.num_samples, this.num_stims] = DefineTriggerMatrix( this );
            end
        end
        
        % Maps the stim channels in the array to the trigger
        % values in the table.
        function chmap = DefineTriggerChannelMap( this )
            stims = unique(sort(this.trigger_table.stimType));
            vals = zeros(length(stims), 0)
            for stim = 1 : length(stims)
                vals(stim) = stim
            end
            
            chmap = containers.Map(stims, vals)
        end
        
        % Set Properties - Make Stim Matrix
        function [tm, ns, nst] = DefineTriggerMatrix( this )
            % Creates empty trigger Matrix
            n_stim_types = size(transpose(unique(this.trigger_table.stimType)));
            sample_array_dims = size(this.nirs_f.t)
            ns = sample_array_dims(1);
            nst = n_stim_types(2);
            % Creates empty trigger Matrix of proper size.
            tm = zeros(ns, nst);

            % iterates through trigger file and sets on samples to 1.
            t_size = height(this.trigger_table);
            for row = 1:t_size
                mrow = this.trigger_table(row, :);
                onset = mrow.onset;
                duration = mrow.duration;
                trig_col = this.trigger_ch_map(mrow.stimType)
                tm(onset:onset+duration, trig_col) = 1;
            end
        end
       
        function nn = PushMatrixToNirs( this, out_fpath )
            new_nirs = this.nirs_f;
            new_nirs.s = this.trigger_matrix;
            nn = new_nirs;
            if length(out_fpath) > 0
                save(out_fpath, 'nn', '-mat');
            end
        end
        
    end
end

