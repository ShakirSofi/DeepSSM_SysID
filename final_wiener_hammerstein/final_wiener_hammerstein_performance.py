import matplotlib.pyplot as plt
import os
import torch
import numpy as np
import csv
import pandas as pd
import sys

os.chdir('../')
sys.path.append(os.getcwd())

# %%
# set (high level) options dictionary
dataset = 'wiener_hammerstein'
logdir = 'gridsearch'
addlog = 'run_200226_1'
model = ['VRNN-Gauss']  # ['VAE-RNN', 'VRNN-Gauss-I', 'VRNN-Gauss', 'VRNN-GMM-I', 'VRNN-GMM', 'STORN']

h_values = np.array([30, 40, 50, 60])  # [10, 20, 30, 40, 50, 60, 70, 80],
# z_values = [10],
# n_values = [1],

rmse_all_multisine = []
rmse_all_sweptsine = []
nll_all_multisine = []
nll_all_sweptsine = []

# %% get the likelihood and rmse matrices

for i, model_sel in enumerate(model):
    # get saving path
    path_general = os.getcwd() + '/log_Server/{}/{}/{}/{}/'.format(logdir, dataset, addlog, model_sel)
    # get data
    file_name = dataset + '.pt'
    path = path_general + 'data/'
    data = torch.load(path + file_name)

    # load the data: RMSE
    rmse_all_multisine.append(data['all_rmse_multisine'])
    rmse_all_sweptsine.append(data['all_rmse_sweptsine'])
    # load the data: NLL
    nll_all_multisine.append(-data['all_likelihood_multisine'])
    nll_all_sweptsine.append(-data['all_likelihood_sweptsine'])

# %% plot everything

### Remove this later!!
for i, model_sel in enumerate(model):
    rmse_all_multisine[i] = rmse_all_multisine[i][:,1,:]
    rmse_all_sweptsine[i] = rmse_all_sweptsine[i][:, 1, :]


###

plt.figure(figsize=(5 * 2, 5 * 1))
# plot rmse: multisine
plt.subplot(1, 2, 1)
for i, model_sel in enumerate(model):
    mean = rmse_all_multisine[i].mean(1).squeeze()
    std = np.sqrt(rmse_all_multisine[i].var(1)).squeeze()
    # plot mean
    plt.plot(h_values, mean, label=model_sel)
    # plot std
    # plt.fill_between(ndata, mean, mean + std, alpha=0.3, facecolor='b')
    # plt.fill_between(ndata, mean, mean - std, alpha=0.3, facecolor='b')
plt.legend()
plt.xlabel('training data points')
plt.ylabel('RMSE')
plt.title('RMSE of multisine')

# plot rmse: sweptsine
plt.subplot(1, 2, 2)
for i, model_sel in enumerate(model):
    mean = rmse_all_sweptsine[i].mean(1).squeeze()
    std = np.sqrt(rmse_all_sweptsine[i].var(1)).squeeze()
    # plot mean
    plt.plot(h_values, mean, label=model_sel)
    # plot std
    # plt.fill_between(ndata, mean, mean + std, alpha=0.3, facecolor='b')
    # plt.fill_between(ndata, mean, mean - std, alpha=0.3, facecolor='b')
plt.legend()
plt.xlabel('training data points')
plt.ylabel('NLL')
plt.title('NLL of sweptsine')

plt.show()

# %% output of best values

for i, model_sel in enumerate(model):
    mean_rmse_multisine = rmse_all_sweptsine[i].mean(1).squeeze()
    mean_rmse_multisine_idx = np.argmin(mean_rmse_multisine)

    mean_rmse_swepsine = rmse_all_sweptsine[i].mean(1).squeeze()
    mean_rmse_swepsine_idx = np.argmin(mean_rmse_swepsine)

    print(model_sel)
    print('\tmin Multisine: RMSE={} at h={}'.format(mean_rmse_multisine[mean_rmse_multisine_idx], h_values[mean_rmse_multisine_idx]))
    print('\tmin Sweptsine RMSE={} at h={}\n'.format(mean_rmse_swepsine[mean_rmse_swepsine_idx], h_values[mean_rmse_swepsine_idx]))

# %% save data for pgfplots

data = {'x': h_values, }

for i, model_sel in enumerate(model):
    # RMSE: multisine
    mean_rmse_multisine = rmse_all_multisine[i].mean(1).squeeze().numpy()
    std_rmse_multisine = np.sqrt(rmse_all_multisine[i].var(1)).squeeze().numpy()
    update_mu_rmse_multisine = {'mu_rmse_ms_{}'.format(model[i]): mean_rmse_multisine}
    update_pstd_rmse_multisine = {'pstd_rmse_ms_{}'.format(model[i]): mean_rmse_multisine + std_rmse_multisine}
    update_mstd_rmse_multisine = {'mstd_rmse_ms_{}'.format(model[i]): mean_rmse_multisine - std_rmse_multisine}

    # update dictionary
    data.update(update_mu_rmse_multisine)
    data.update(update_pstd_rmse_multisine)
    data.update(update_mstd_rmse_multisine)

    # RMSE: Swept sine
    mean_rmse_sweptsine = rmse_all_sweptsine[i].mean(1).squeeze().numpy()
    std_rmse_sweptsine = np.sqrt(rmse_all_sweptsine[i].var(1)).squeeze().numpy()
    update_mu_rmse_sweptsine = {'mu_rmse_ss_{}'.format(model[i]): mean_rmse_sweptsine}
    update_pstd_rmse_sweptsine = {'pstd_rmse_ss_{}'.format(model[i]): mean_rmse_sweptsine + std_rmse_sweptsine}
    update_mstd_rmse_sweptsine = {'mstd_rmse_ss_{}'.format(model[i]): mean_rmse_sweptsine - std_rmse_sweptsine}

    # update dictionary
    data.update(update_mu_rmse_sweptsine)
    data.update(update_pstd_rmse_sweptsine)
    data.update(update_mstd_rmse_sweptsine)

df = pd.DataFrame(data)

path = os.getcwd() + '/final_wiener_hammerstein/' + 'WH_data_performance.csv'
df.to_csv(path, index=False)