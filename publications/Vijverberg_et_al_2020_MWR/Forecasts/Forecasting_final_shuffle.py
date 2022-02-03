#!/usr/bin/env python
# coding: utf-8

# # Forecasting
# Below done with test data, same format as df_data

#get_ipython().run_line_magic('load_ext', 'autoreload')
#get_ipython().run_line_magic('autoreload', '2')
import os, inspect, sys
import numpy as np
from time import time
curr_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
main_dir = '/'.join(curr_dir.split('/')[:-3])
data_dir = '/'.join(curr_dir.split('/')[:-1]) + '/data'
RGCPD_dir = os.path.join(main_dir, 'RGCPD')
fc_dir = os.path.join(main_dir, 'forecasting')
df_ana_dir = os.path.join(main_dir, 'df_analysis/df_analysis/')
if fc_dir not in sys.path:
    sys.path.append(main_dir)
    sys.path.append(RGCPD_dir)
    sys.path.append(df_ana_dir)
    sys.path.append(fc_dir)

user_dir = os.path.expanduser('~')
if sys.platform == 'linux':
    import matplotlib as mpl
    mpl.use('Agg')



from class_fc import fcev


# Define statmodel:
logit = ('logit', None)

#%%
start_time = time()

ERA_q65tail = data_dir + '/1q65tail_df_data_sst_CPPAs30_sm2_sm3_dt1_c378f.h5'

kwrgs_events = {'event_percentile': 'std',
                'window':'single_event', 'min_dur':2, 'max_break':1,
                'grouped':True}

kwrgs_events = kwrgs_events
precur_aggr = 15
add_autocorr = False
use_fold = None
n_boot = 5000
lags_i = np.arange(0,120, 10)
start_end_TVdate = None # ('7-04', '8-22')


list_of_fc = [fcev(path_data=ERA_q65tail, precur_aggr=precur_aggr,
                    use_fold=use_fold, start_end_TVdate=None,
                    stat_model= ('logitCV',
                                {'Cs':10, #np.logspace(-4,1,10)
                                'class_weight':{ 0:1, 1:1},
                                 'scoring':'neg_brier_score',
                                 'penalty':'l2',
                                 'solver':'lbfgs',
                                 'max_iter':100,
                                 'kfold':5,
                                 'seed':1}),
                    kwrgs_pp={'add_autocorr':add_autocorr, 'normalize':'datesRV'},
                    dataset=f'CV shuffle 1',
                    keys_d='CPPA+sm'),
               fcev(path_data=ERA_q65tail, precur_aggr=precur_aggr,
                     use_fold=use_fold, start_end_TVdate=None,
                     stat_model= ('logitCV',
                                 {'Cs':10, #np.logspace(-4,1,10)
                                 'class_weight':{ 0:1, 1:1},
                                  'scoring':'neg_brier_score',
                                  'penalty':'l2',
                                  'solver':'lbfgs',
                                  'max_iter':100,
                                  'kfold':5,
                                  'seed':2}),
                     kwrgs_pp={'add_autocorr':add_autocorr, 'normalize':'datesRV'},
                     dataset=f'CV shuffle 2',
                     keys_d='CPPA+sm'),
                fcev(path_data=ERA_q65tail, precur_aggr=precur_aggr,
                      use_fold=use_fold, start_end_TVdate=None,
                      stat_model= ('logitCV',
                                  {'Cs':10, #np.logspace(-4,1,10)
                                  'class_weight':{ 0:1, 1:1},
                                   'scoring':'neg_brier_score',
                                   'penalty':'l2',
                                   'solver':'lbfgs',
                                   'max_iter':100,
                                   'kfold':5,
                                   'seed':3}),
                      kwrgs_pp={'add_autocorr':add_autocorr, 'normalize':'datesRV'},
                      dataset=f'CV shuffle 3',
                      keys_d='CPPA+sm')]






#%%
times = []
t00 = time()
for fc in list_of_fc:
    t0 = time()
    fc.get_TV(kwrgs_events=kwrgs_events)

    fc.fit_models(lead_max=lags_i, verbosity=1)

    fc.perform_validation(n_boot=n_boot, blocksize='auto', alpha=0.05,
                          threshold_pred=50)

    single_run_time = int(time()-t0)
    times.append(single_run_time)
    total_n_runs = len(list_of_fc)
    ETC = (int(np.mean(times) * total_n_runs))
    print(f'Time elapsed single run in {single_run_time} sec\t'
          f'ETC {int(ETC/60)} min \t Progress {int(100*(time()-t00)/ETC)}% ')


# In[8]:
working_folder, filename = list_of_fc[0]._print_sett(list_of_fc=list_of_fc)

store = False
if __name__ == "__main__":
    filename = list_of_fc[0].filename
    store = True

import valid_plots as dfplots
import functions_pp


dict_all = dfplots.merge_valid_info(list_of_fc, store=store)
if store:
    dict_merge_all = functions_pp.load_hdf5(filename+'.h5')


kwrgs = {'wspace':0.16, 'hspace':.25, 'col_wrap':2, 'skip_redundant_title':True,
         'lags_relcurve':[50], 'fontbase':14, 'figaspect':2}
#kwrgs = {'wspace':0.25, 'col_wrap':3, 'threshold_bin':fc.threshold_pred}
met = ['AUC-ROC', 'AUC-PR', 'Precision', 'BSS', 'Accuracy', 'Rel. Curve']
line_dim = 'dataset'
group_line_by = None

fig = dfplots.valid_figures(dict_merge_all,
                          line_dim=line_dim,
                          group_line_by=group_line_by,
                          met=met, **kwrgs)


f_format = '.pdf'
pathfig_valid = os.path.join(filename + f_format)
fig.savefig(pathfig_valid,
            bbox_inches='tight') # dpi auto 600



#%%

# im = 0
# il = 1
# ifc = 0
# f_format = '.pdf'
# if os.path.isdir(fc.filename) == False : os.makedirs(fc.filename)
# import valid_plots as dfplots
# if __name__ == "__main__":
#     for ifc, fc in enumerate(list_of_fc):
#         for im, m in enumerate([n[0] for n in fc.stat_model_l]):
#             for il, l in enumerate(fc.lags_i):
#                 fc = list_of_fc[ifc]
#                 m = [n[0] for n in fc.stat_model_l][im]
#                 l = fc.lags_i[il]
#                 # visual analysis
#                 f_name = os.path.join(filename, f'ifc{ifc}_va_l{l}_{m}')
#                 fig = dfplots.visual_analysis(fc, lag=l, model=m)
#                 fig.savefig(os.path.join(working_folder, f_name) + f_format,
#                             bbox_inches='tight') # dpi auto 600
#                 # plot deviance
#                 if m[:3] == 'GBC':
#                     fig = dfplots.plot_deviance(fc, lag=l, model=m)
#                     f_name = os.path.join(filename, f'ifc{ifc}_deviance_l{l}')


#                     fig.savefig(os.path.join(working_folder, f_name) + f_format,
#                                 bbox_inches='tight') # dpi auto 600

#                     fig = fc.plot_oneway_partial_dependence()
#                     f_name = os.path.join(filename, f'ifc{ifc}_partial_depen_l{l}')
#                     fig.savefig(os.path.join(working_folder, f_name) + f_format,
#                                 bbox_inches='tight') # dpi auto 600

#                 if m[:7] == 'logitCV':
#                     fig = fc.plot_logit_regularization(lag_i=l)
#                     f_name = os.path.join(filename, f'ifc{ifc}_logitregul_l{l}')
#                     fig.savefig(os.path.join(working_folder, f_name) + f_format,
#                             bbox_inches='tight') # dpi auto 600

#             df_importance, fig = fc.plot_feature_importances(lag=55)
#             f_name = os.path.join(filename, f'ifc{ifc}_feat_l{l}_{m}')
#             fig.savefig(os.path.join(working_folder, f_name) + f_format,
#                         bbox_inches='tight') # dpi auto 600


#%%


#rename_ERA =    {'ERA-5: sst(PEP)+sm':'PEP+sm',
#             'ERA-5: sst(PDO,ENSO)+sm':'PDO+ENSO+sm',
#             'ERA-5: sst(CPPA)+sm':'CPPA+sm'}
#
#for old, new in rename_ERA.items():
#    if new not in dict_experiments.keys():
#        dict_experiments[new] = dict_experiments.pop(old)

#rename_EC = {'ERA-5 PEP':'PEP',
#             'ERA-5 CPPA':'CPPA',
#             'EC-earth 2.3 PEP':'PEP ',
#             'EC-earth 2.3 CPPA':'CPPA '}
#
#for old, new in rename_EC.items():
#    if new not in dict_experiments.keys():
#        dict_experiments[new] = dict_experiments.pop(old)

#rename_CPPA_comp =    {'ERA-5: CPPAregs+sm' : 'precursor regions + sm',
#                       'ERA-5: CPPApattern+sm': 'precursor pattern + sm',
#                       'ERA-5: sst(CPPA)+sm' : 'CPPA (all) + sm'}
#
#for old, new in rename_CPPA_comp.items():
#    if new not in dict_experiments.keys():
#        dict_experiments[new] = dict_experiments.pop(old)
