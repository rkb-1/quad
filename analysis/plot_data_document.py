import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
#from sklearn.metrics import mean_squared_error
from cProfile import label

from ctypes import util

import matplotlib as mpl

from cycler import cycler

# plot style settings

import matplotlib.pyplot as plt                                                                                          
params = {'text.usetex': True,
          'font.size': 15,
          'font.family': 'sans-serif',
          "font.sans-serif": ["Helvetica"],
          # 'text.latex.unicode': True,
          }
plt.rcParams.update(params)
mpl.rcParams['axes.prop_cycle'] = cycler(color=['#20639B',
                                                'orange',
                                                '#3CAEA3',
                                                '#ED553B',
                                                '#F6D55C',
                                                'dimgrey']) # color scheme


df_control = pd.read_csv('analysis/gabriele_forward_jump_pd/control_test.csv')
# print(df_control.head())
df_status =  pd.read_csv('analysis/gabriele_forward_jump_pd/status_test.csv')
# print(df_status.head())
# df_command = pd.read_csv('../results/csv_files/outside/quad_command_data_3mps_outside.csv')
# print(df_command.head())
# df_tauIDyn = pd.read_csv('../results/csv_files/inside/slow_walk_idyn.csv')
# print(df_tauIDyn.head())

# Getting data according to start and stop index
start_t = 4.425 # inside_reg
stop_t = 5.110 # inside_reg
df_control = df_control[df_control['t[s]'].between(start_t,stop_t)]
df_status = df_status[df_status['t[s]'].between(start_t,stop_t)]
#df_command = df_command[df_command['t[s]'].between(start_t,stop_t)]
#df_tauIDyn = df_tauIDyn[df_tauIDyn['t[s]'].between(start_t,stop_t)]

# Setting up the column names for plots
time_status = df_status['t[s]']
time_control = df_control['t[s]']
column_names_position = np.array(df_status.columns[df_status.columns.to_series().str.contains('q_')])
column_names_velocity = np.array(df_status.columns[df_status.columns.to_series().str.contains('qd_')])
column_names_acceleration = np.array(df_status.columns[df_status.columns.to_series().str.contains('qdd_')])
column_names_torque = np.array(df_status.columns[df_status.columns.to_series().str.contains('Tau_')])

# Commands plot
# fig, axes = plt.subplots(2)
# df_command.plot(kind='line',x='t[s]',y="command_vel",ax=axes[0])
# df_command.plot(kind='line',x='t[s]',y="command_omega",color = 'r',ax=axes[1])
# fig.set_size_inches(30, 12, forward=True)
# fig.suptitle('Commanded velocities', fontsize=16)
# axes[0].set_ylabel('m/s')
# axes[1].set_ylabel('rad/s')
# plt.savefig('../results/quad_3mps/outside/command.png')
# plt.show()
# plt.clf()
# plt.close()

# LEGS PLOTS
leg_names = ['Front Left Leg', 'Front Right Leg', 'Back Left Leg', 'Back Right Leg']
for i in range(1): # Legs 1,2,3,4
    fig, axes = plt.subplots(3, 2,sharex=False)
    #fig.set_size_inches(30, 12, forward=True)
    #plt.subplots_adjust(left  = 0.03, right = 0.97, hspace = 0.25, wspace = 0.25)
        
    for j in range(3): # joints 1,2,3
        x=3*i+j
        axes[j,0].plot(time_status,df_status[column_names_position[x]], label = r"$\mathrm{joint\, status}$")
        axes[j,0].plot(time_control,df_control[column_names_position[x]], label = r"$\mathrm{joint\, command}$")

        axes[j,0].set_title(r"$\mathrm{q_{name}}$".replace('name',column_names_position[x][2:5]))
        axes[j,0].set(xlabel=r"$\mathrm{Time\, \, [s]}$")
        axes[j,0].set(ylabel=r"$\mathrm{Position\, \, [rad]}$")

        axes[j,1].plot(time_status,df_status[column_names_velocity[x]], label = r"$\mathrm{joint\, status}$")
        axes[j,1].plot(time_control,df_control[column_names_velocity[x]], label = r"$\mathrm{joint\, command}$")
        axes[j,1].set_title(r"$\mathrm{\dot{q}_{name}}$".replace('name',column_names_velocity[x][3:6]))
        axes[j,1].set(xlabel=r"$\mathrm{Time\, \, [s]}$")
        axes[j,1].set(ylabel=r"$\mathrm{Velocity\, \, [rad/s]}$")

        #axes[j,2].plot(time_status,df_status[column_names_acceleration[x]], label = 'joint_status')
        #axes[j,2].plot(time_control,df_control[column_names_acceleration[x]], label = 'joint_control_command')
        #axes[j,2].set_title(column_names_acceleration[x])
        #axes[j,2].set(xlabel='time(s)')
        #axes[j,2].set(ylabel='rad/s^2')

        #axes[j,2].plot(time_status,df_status[column_names_torque[x]], label = 'joint_status')
        #axes[j,2].plot(time_control,df_control[column_names_torque[x]], label = 'joint_command')
        #axes[j,2].set_title(column_names_torque[x])
        #axes[j,2].set(xlabel='time(s)')
        #axes[j,2].set(ylabel='Nm')

    lines, labels = fig.axes[-1].get_legend_handles_labels()
    fig.legend(lines, labels, loc = 'upper right') 
    #fig.suptitle(str("LEG: {}".format(i+1) + " or {}".format(leg_names[i])), fontsize=16)
    #plt.savefig('analysis/gabriele_forward_jump_pdtau/leg{}.png'.format(i+1))
    #fig.legend(lines, labels) 
    fig.tight_layout()
    plt.savefig('analysis/gabriele_forward_jump_pd/leg{}.pdf'.format(i+1),format='pdf')
    plt.show()
    plt.close()


## Check Inverse dynamics from HyRoDyn with the torques from the quadruped

# time = df_tauIDyn['t[s]']
# column_names_quad = np.array(df_status.columns[df_status.columns.to_series().str.contains('Tau_')])
# column_names_urdf = np.array(df_tauIDyn.columns[df_tauIDyn.columns.to_series().str.contains('tau')])

# # plotting comparison
# fig, axes = plt.subplots(3, 4)
# fig.set_size_inches(30, 12, forward=True)
# plt.subplots_adjust(left  = 0.03, right = 0.97, hspace = 0.25, wspace = 0.25)
# for i in range(4):
#     for j in range(3):
#         x=3*i+j
#         axes[j,i].plot(time_status,df_status[column_names_quad[x]], label = 'torques_from_motors')
#         if (x == 2 or x== 11):
#             axes[j,i].plot(time,df_tauIDyn[column_names_urdf[x]].multiply(1), label = 'torques_from_HyRoDyn')
#         elif (x == 5 or x==8):
#             axes[j,i].plot(time,df_tauIDyn[column_names_urdf[x]].multiply(1), label = 'torques_from_HyRoDyn')
#         else:
#             axes[j,i].plot(time,df_tauIDyn[column_names_urdf[x]], label = 'torques_from_HyRoDyn')
#         # axes[j,i].set_title(column_names_urdf[x])
#         axes[j,i].set(ylabel='Nm')
#         axes[j,i].set(xlabel='time(s)')

# lines, labels = fig.axes[-1].get_legend_handles_labels()
# fig.legend(lines, labels, loc = 'upper right')   
# fig.suptitle('Inverse Dynamics Comparison', fontsize=16)
# cols = ['Leg: {}'.format(col) for col in ['Front Left', 'Front Right', 'Back Left', 'Back Right']]
# rows = ['Joint: {}'.format(row) for row in ['Hip', 'Thigh (Upper limb)', 'Knee (Lower limb)']]
# for ax, col in zip(axes[0], cols):
#    ax.set_title(col)
# for ax, row in zip(axes[:,0], rows):
#    ax.set_ylabel(row, rotation=90, size='large')
# #plt.savefig('../results/slowWalk/IDyn_comparison_inside_slowWalk.png')
# plt.show()
# plt.close()  



