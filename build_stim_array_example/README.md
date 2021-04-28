### Taking trigger information and putting into a .nirs file stim matrix.

At it's heart, this is what this code is trying to do. There are a lot of steps
up to getting the stimulus info into a readable format, and a few other technicalities,
but really the heart of all this code is very simple.

We want to take a .nirs file, and put the stimulus info (design matrix) into it,
so that it can easily be loaded into the nirs toolbox.

`./make_stim_matrix.py` does this with a very simple .csv file (`stim_info.csv`). Every line in this
file is commented. The code is meant to be as short as possible, and therefore does take a few shortcuts
(using pandas, etc). But this is the purest case I can manage of what this code is doing.
