ROOT_DATA_DIR = 'E:\DotNIRSPythonTools\DotNIRSToolboxTools\build_stim_array_example\check_rank\out\'

raw = nirs.io.loadDirectory(ROOT_DATA_DIR, {'Subject'}, {@nirs.io.loadNIRx})

% Pre-processing -----------------

% Resample --- default resample is to 4 hz.
job=nirs.modules.Resample
rs=job.run(raw)

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
job.max_distance=15
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
