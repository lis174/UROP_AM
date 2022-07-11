# UROP_AM

Run the AM_script.py or AMf_automated.ipynb to get the action measure for daily datasets in nc format. Then run EOFs.ipynb to calculate the Emperical Orthogonal Functions (EOFs) and to plot the action measure spatially. 

For an explanation of the code, AM_function_exp.ipynb can be viewed that explains the function step by step. For an explanation on plotting NetCDF files, look at compare_datasets.ipynb to get an idea of the different plots and analysis that can be done with Jasmin and xarray.

For the world analysis of AM_script.py, I have used the datasets:
- CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.highres-future.r1i1p1f1.day.tas.gn
- CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.hist-1950.r1i1p1f1.day.tas.gn

Most datasets can be also be found under this link (Imperial institutional access only):
https://imperiallondon-my.sharepoint.com/:f:/g/personal/lb1519_ic_ac_uk/Eqjxf4Z0VVdJiFwe9pOY_7cB4b77GnWHq0WsCBc5jYeUIg?e=z7mzaN