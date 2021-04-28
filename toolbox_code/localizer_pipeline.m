ROOT_DATA_DIR = '..\data\triggers_truncated_localizers'

raw = nirs.io.loadDirectory(ROOT_DATA_DIR, {'Subject'}, {@nirs.io.loadNIRx})

% STIM ORDER LOCALIZERS

demographics = nirs.createDemographicsTable(raw);

j = nirs.modules.RemoveStimless( );

j = nirs.modules.RenameStims( j );

j.listOfChanges = {'stim_channel1' 'start'
                   'stim_channel2' 'aloc_sentences'
                   'stim_channel3' 'bloc_words'
                   'stim_channel4' 'cloc_jabsent'
                   'stim_channel5' 'dloc_jabwords'};

stimsChanged = j.run(raw);

job = nirs.modules.DiscardStims();
job.listOfStims = {'start' 'stim_channel6'};
stimsChanged = job.run(stimsChanged)

% Pre-processing -----------------

% Resample --- default resample is to 4 hz.
job=nirs.modules.Resample
rs=job.run(stimsChanged)

% Convert Voltage to Optical Density (Also known as absorbtion)
job=nirs.modules.OpticalDensity
od=job.run(rs)
job.cite

% Convert Optical Density Values to (HbO and HbR)
job=nirs.modules.BeerLambertLaw
hb=job.run(od)
job.cite

% Short Channels
job=nirs.modules.LabelShortSeperation()
job.max_distance=8;
hb=job.run(hb)

% Motion Correction VIA Acc.
job=nirs.modules.AddAuxRegressors;
job.label={'aux'};
mot_corr=job.run(hb)
job.cite

% % End Pre-processing

% Fitting Data to GLM -------------------
job=nirs.modules.GLM
job.AddShortSepRegressors=true
SubjStats=job.run(mot_corr)

% Model

job = nirs.modules.MixedEffects();
job.formula = 'beta ~ -1 + cond + (1|subject)';
% job.formula = 'beta ~ -1 + group*cond + (1|subject)'
job.dummyCoding = 'full';
GroupStats = job.run(SubjStats);
job.cite


% Contrasts

% [1 1 1 1] - basic condition > baseline
% [1 0 0 -1] - Fedorenko → Sentence > Nonword list
% [1 -1 1 -1] - Syntactic  → (Sentences (S,J)) > (Words (W,N))
% [1 1 -1 -1] - Semantic   → (sensical (S,W)) > (nonsensical (J, N))
% [1 1 -1 -1] - Interaction   → Has syntax (Semantics yes >  Semantics no)

c_t = [1 1 1 1
       1 0 0 -1;
       1 -1 1 -1;
       1 1 -1 -1;
       1 -1 -1 1];

% ContrastStats = GroupStats.ftest(c)
ContrastStats = GroupStats.ttest(c_t)

ContrastStats.table

ContrastStats.probe.defaultdrawfcn = '2D';
% ContrastStats.probe.defaultdrawfcn = '3D Mesh';
% ContrastStats.draw
ContrastStats.printAll('tstat', [-10 10], 'q < 0.05', './output/figs', 'jpg')
% Write out table to csv ---

writetable(ContrastStats.table, './output/loc_con_results.csv')

% ROI Stuff.
% EML 1616.

% channels = [1  1;
%             1  2;
%             1  9;
%             2  1;
%             2  2;
%             2  3;
%             2  4;
%             2 16;
%             3  4; % *
%             3  5; % *
%             3  6; % *
%             3 17;
%             4  3;
%             4  4;
%             4  7;
%             5  5; % *
%             5  6; % *
%             6  4; % *
%             6  6; % *
%             6  7;
%             7  3;
%             7  7;
%             7 18;
%             8  8;
%             8 19;
%             9  1;
%             9  3;
%             9 10;
%             10  1;
%             10  9;
%             10 10;
%             10 11;
%             10 20;
%             11 11;
%             11 12;
%             11 13;
%             11 21;
%             12 10;
%             12 11;
%             12 14;
%             13 12;
%             13 13;
%             14 11;
%             14 13;
%             14 14;
%             15 10;
%             15 14;
%             15 22;
%             16 15;
%             16 23];
%
%
% lang_roi = channels([9:11], :)
% lang_roi_2 = channels([16:19], :)
%
% Region{1} = table(lang_roi(:,1), lang_roi(:,2), 'VariableNames',{'source', 'detector'});
% Region{2} = table(lang_roi_2(:,1), lang_roi_2(:,2), 'VariableNames',{'source', 'detector'});
%
% ROItable=nirs.util.roiAverage(ContrastStats,Region,{'region1','region2'});
% disp(ROItable);
