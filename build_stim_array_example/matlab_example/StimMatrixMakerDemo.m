OUTPUT_DIR = '../out/EML1_055/'


% Create martix maker oubject and pass path to 'trigger' file as first arg.
% and '.nirs' file as second arg.
smm = StimMatrixMaker('../stim_info.csv', '../EML1_055/EML1_055.nirs')

% PushMatrixToNirs method will return the new nirs matlab oubject as a
% variable.
% if you include an output path as an argument
% it will write a .nirs file to that filepath.
new_nirs = smm.PushMatrixToNirs(strcat(OUTPUT_DIR, '/new_nirs.nirs'))

%Okay, in order to load stuff into the toolbox now we are going to need to
%move all of the other files that were in the original directory into the
%new directory.

dir_files = dir('../EML1_055/');
for file = 1:length(dir_files)
    if contains(dir_files(file).name, '.nirs') == 0 && length(dir_files(file).name) > 2
        src = strcat(dir_files(file).folder, '/' ,dir_files(file).name);
        copyfile(src, OUTPUT_DIR);
    end
end

% test
raw = nirs.io.loadDirectory(OUTPUT_DIR, {'Subject'}, {@nirs.io.loadNIRx})

