% Create martix maker oubject and pass path to 'trigger' file as first arg.
% and '.nirs' file as second arg.
smm = StimMatrixMaker('../stim_info.csv', '../EML1_055/EML1_055.nirs')

% PushMatrixToNirs method will return the new nirs matlab oubject as a
% variable.
% if you include an output path as an argument
% it will write a .nirs file to that filepath.
new_nirs = smm.PushMatrixToNirs('../out/new_nirs.nirs')
