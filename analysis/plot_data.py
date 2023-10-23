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



import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-s', '--single', type=str, default=None)
parser.add_argument('-f', '--folder', type=str)
args = parser.parse_args()

folder = args.folder
single = args.single
df_control = pd.read_csv(folder + 'control_test.csv')
# print(df_control.head())
df_status =  pd.read_csv(folder + 'status_test.csv')
# print(df_status.head())
# df_power = pd.read_csv(folder + 'power.csv')
# df_command = pd.read_csv('../results/csv_files/outside/quad_command_data_3mps_outside.csv')
# print(df_command.head())
# df_tauIDyn = pd.read_csv('../results/csv_files/inside/slow_walk_idyn.csv')
# print(df_tauIDyn.head())

## Load Timing Information
phases_timing = np.load(folder + 'phase_timings.npz')
replay_start = phases_timing['replay_start']
exertion_phase = phases_timing['exertion_phase']
flight_phase = phases_timing['flight_phase']
land_phase = phases_timing['land_phase']
replay_end = phases_timing['replay_end']

# print(single)
# Getting data according to start and stop index
if(single):
    start_t = exertion_phase[0] # inside_reg
    stop_t = exertion_phase[1] # inside_reg
    df_control = df_control[df_control['t[s]'].between(start_t,stop_t)]
    df_status = df_status[df_status['t[s]'].between(start_t,stop_t)]
    # df_power = df_power[df_power['t[s]'].between(start_t,stop_t)]

    flight_phase = flight_phase[0]
    land_phase = land_phase[0]
    # #df_command = df_command[df_command['t[s]'].between(start_t,stop_t)]
    # #df_tauIDyn = df_tauIDyn[df_tauIDyn['t[s]'].between(start_t,stop_t)]

    # # Setting up the column names for plots
    time_status = df_status['t[s]']
    time_control = df_control['t[s]']
    column_names_position = np.array(df_status.columns[df_status.columns.to_series().str.contains('q_')])
    column_names_velocity = np.array(df_status.columns[df_status.columns.to_series().str.contains('qd_')])
    column_names_acceleration = np.array(df_status.columns[df_status.columns.to_series().str.contains('qdd_')])
    column_names_torque = np.array(df_status.columns[df_status.columns.to_series().str.contains('Tau_')])

    # LEGS PLOTS
    leg_names = ['Front Left Leg', 'Front Right Leg', 'Back Left Leg', 'Back Right Leg']
    for i in range(4): # Legs 1,2,3,4
        fig, axes = plt.subplots(3, 3)
        fig.set_size_inches(25, 15, forward=True)
        plt.subplots_adjust(left  = 0.03, right = 0.97, hspace = 0.25, wspace = 0.25)
            
        for j in range(3): # joints 1,2,3
            x=3*i+j
            axes[j,0].plot(time_status,df_status[column_names_position[x]], label = 'joint_status')
            axes[j,0].plot(time_control,df_control[column_names_position[x]], label = 'joint_command')
            axes[j,0].set_title(column_names_position[x])
            axes[j,0].set(xlabel='time(s)')
            axes[j,0].set(ylabel='rad')

            axes[j,1].plot(time_status,df_status[column_names_velocity[x]], label = 'joint_status')
            axes[j,1].plot(time_control,df_control[column_names_velocity[x]], label = 'joint_command')
            axes[j,1].set_title(column_names_velocity[x])
            axes[j,1].set(xlabel='time(s)')
            axes[j,1].set(ylabel='rad/s')

            axes[j,2].plot(time_status,df_status[column_names_torque[x]], label = 'joint_status')
            axes[j,2].plot(time_control,df_control[column_names_torque[x]], label = 'joint_command')
            axes[j,2].set_title(column_names_torque[x])
            axes[j,2].set(xlabel='time(s)')
            axes[j,2].set(ylabel='Nm')

            # for event in exertion_phase:
            #     axes[j,0].axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
            #     axes[j,1].axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
            #     axes[j,2].axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
            # for event in flight_phase:
            axes[j,0].axvline(x=flight_phase, color='g', linestyle='--',label= 'flight_phase')
            axes[j,1].axvline(x=flight_phase, color='g', linestyle='--',label= 'flight_phase')
            axes[j,2].axvline(x=flight_phase, color='g', linestyle='--',label= 'flight_phase')
            # for event in land_phase:
            axes[j,0].axvline(x=land_phase, color='c', linestyle='--', label= 'land_phase')
            axes[j,1].axvline(x=land_phase, color='c', linestyle='--', label= 'land_phase')
            axes[j,2].axvline(x=land_phase, color='c', linestyle='--', label= 'land_phase')
        lines, labels = axes[0,0].get_legend_handles_labels()
        # labels =  np.unique(labels)
        #fig.legend(lines, labels, loc = 'upper right') 
        fig.suptitle(str("LEG: {}".format(i+1) + " or {}".format(leg_names[i])), fontsize=16)
        fig.legend(lines, labels) 
        plt.savefig(folder+'leg{}clipped.pdf'.format(i+1),format='pdf',bbox_inches='tight')
        plt.show()
        plt.close()

    ## POWER Consumption data plots

    # plt.plot(df_power['t[s]'], df_power['power_W'])
    # # for event in (exertion_phase):
    # #     plt.axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
    # #     plt.axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
    # #     plt.axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
    # # for event in (flight_phase):
    # plt.axvline(x=flight_phase, color='g', linestyle='--',label= 'flight_phase')
    # #     plt.axvline(x=event, color='g', linestyle='--',label= 'flight_phase')
    # #     plt.axvline(x=event, color='g', linestyle='--',label= 'flight_phase')
    # # for event in (land_phase):
    # plt.axvline(x=land_phase, color='c', linestyle='--', label= 'land_phase')
    # #     plt.axvline(x=event, color='c', linestyle='--', label= 'land_phase')
    # #     plt.axvline(x=event, color='c', linestyle='--', label= 'land_phase')
    # plt.xlabel('Time (s)')
    # plt.ylabel('Power (W)')
    # plt.legend()
    # plt.title('Power = Voltage*Current')
    # plt.savefig(folder+'powerClipped.pdf',format='pdf',bbox_inches='tight')
    # plt.show()
else:
    start_t = replay_start[0] # inside_reg
    stop_t = replay_end[0] # inside_reg
    df_control = df_control[df_control['t[s]'].between(start_t,stop_t)]
    df_status = df_status[df_status['t[s]'].between(start_t,stop_t)]
    # df_power = df_power[df_power['t[s]'].between(start_t,stop_t)]

    # #df_command = df_command[df_command['t[s]'].between(start_t,stop_t)]
    # #df_tauIDyn = df_tauIDyn[df_tauIDyn['t[s]'].between(start_t,stop_t)]

    # # Setting up the column names for plots
    time_status = df_status['t[s]']
    time_control = df_control['t[s]']
    column_names_position = np.array(df_status.columns[df_status.columns.to_series().str.contains('q_')])
    column_names_velocity = np.array(df_status.columns[df_status.columns.to_series().str.contains('qd_')])
    column_names_acceleration = np.array(df_status.columns[df_status.columns.to_series().str.contains('qdd_')])
    column_names_torque = np.array(df_status.columns[df_status.columns.to_series().str.contains('Tau_')])




    # # Commands plot
    # # fig, axes = plt.subplots(2)
    # # df_command.plot(kind='line',x='t[s]',y="command_vel",ax=axes[0])
    # # df_command.plot(kind='line',x='t[s]',y="command_omega",color = 'r',ax=axes[1])
    # # fig.set_size_inches(30, 12, forward=True)
    # # fig.suptitle('Commanded velocities', fontsize=16)
    # # axes[0].set_ylabel('m/s')
    # # axes[1].set_ylabel('rad/s')
    # # plt.savefig('../results/quad_3mps/outside/command.png')
    # # plt.show()
    # # plt.clf()
    # # plt.close()

    # LEGS PLOTS
    leg_names = ['Front Left Leg', 'Front Right Leg', 'Back Left Leg', 'Back Right Leg']
    for i in range(4): # Legs 1,2,3,4
        fig, axes = plt.subplots(3, 3)
        fig.set_size_inches(25, 15, forward=True)
        plt.subplots_adjust(left  = 0.03, right = 0.97, hspace = 0.25, wspace = 0.25)
            
        for j in range(3): # joints 1,2,3
            x=3*i+j
            axes[j,0].plot(time_status,df_status[column_names_position[x]], label = 'joint_status')
            axes[j,0].plot(time_control,df_control[column_names_position[x]], label = 'joint_command')
            axes[j,0].set_title(column_names_position[x])
            axes[j,0].set(xlabel='time(s)')
            axes[j,0].set(ylabel='rad')

            axes[j,1].plot(time_status,df_status[column_names_velocity[x]], label = 'joint_status')
            axes[j,1].plot(time_control,df_control[column_names_velocity[x]], label = 'joint_command')
            axes[j,1].set_title(column_names_velocity[x])
            axes[j,1].set(xlabel='time(s)')
            axes[j,1].set(ylabel='rad/s')

            #axes[j,2].plot(time_status,df_status[column_names_acceleration[x]], label = 'joint_status')
            #axes[j,2].plot(time_control,df_control[column_names_acceleration[x]], label = 'joint_control_command')
            #axes[j,2].set_title(column_names_acceleration[x])
            #axes[j,2].set(xlabel='time(s)')
            #axes[j,2].set(ylabel='rad/s^2')

            axes[j,2].plot(time_status,df_status[column_names_torque[x]], label = 'joint_status')
            axes[j,2].plot(time_control,df_control[column_names_torque[x]], label = 'joint_command')
            axes[j,2].set_title(column_names_torque[x])
            axes[j,2].set(xlabel='time(s)')
            axes[j,2].set(ylabel='Nm')

            for k,event in enumerate(exertion_phase):
                if k == len(exertion_phase)-1:
                    axes[j,0].axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
                    axes[j,1].axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
                    axes[j,2].axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
                else:
                    axes[j,0].axvline(x=event, color='r', linestyle='--')
                    axes[j,1].axvline(x=event, color='r', linestyle='--')
                    axes[j,2].axvline(x=event, color='r', linestyle='--')

            for k, event in enumerate(flight_phase):
                if k == len(flight_phase)-1 :
                    axes[j,0].axvline(x=event, color='g', linestyle='--', label= 'flight_phase')
                    axes[j,1].axvline(x=event, color='g', linestyle='--', label= 'flight_phase')
                    axes[j,2].axvline(x=event, color='g', linestyle='--', label= 'flight_phase')
                else:
                    axes[j,0].axvline(x=event, color='g', linestyle='--')
                    axes[j,1].axvline(x=event, color='g', linestyle='--')
                    axes[j,2].axvline(x=event, color='g', linestyle='--')
            for k, event in enumerate(land_phase):
                if k == len(land_phase) - 1:
                    axes[j,0].axvline(x=event, color='c', linestyle='--', label= 'land_phase')
                    axes[j,1].axvline(x=event, color='c', linestyle='--', label= 'land_phase')
                    axes[j,2].axvline(x=event, color='c', linestyle='--', label= 'land_phase')
                else:        
                    axes[j,0].axvline(x=event, color='c', linestyle='--')
                    axes[j,1].axvline(x=event, color='c', linestyle='--')
                    axes[j,2].axvline(x=event, color='c', linestyle='--')
        lines, labels = axes[0,0].get_legend_handles_labels()
        # labels =  np.unique(labels)
        #fig.legend(lines, labels, loc = 'upper right') 
        fig.suptitle(str("LEG: {}".format(i+1) + " or {}".format(leg_names[i])), fontsize=16)
        fig.legend(lines, labels) 
        plt.savefig(folder+'leg{}.pdf'.format(i+1),format='pdf',bbox_inches='tight')
        #plt.savefig(folder+'leg{}clipped.pdf'.format(i+1),format='pdf',bbox_inches='tight')
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


    ## POWER Consumption data plots

    # plt.plot(df_power['t[s]'], df_power['power_W'])
    # for k, event in enumerate(exertion_phase):
    #     if k == len(exertion_phase)-1:
    #         plt.axvline(x=event, color='r', linestyle='--', label= 'exertion_phase')
    #     else:
    #         plt.axvline(x=event, color='r', linestyle='--')
    # for k, event in enumerate(flight_phase):
    #     if k == len(flight_phase)-1:
    #         plt.axvline(x=event, color='g', linestyle='--', label= 'flight_phase')
    #     else:
    #         plt.axvline(x=event, color='g', linestyle='--')
    # for k, event in enumerate(land_phase):
    #     if k == len(land_phase)-1:
    #         plt.axvline(x=event, color='c', linestyle='--', label= 'land_phase')
    #     else:
    #         plt.axvline(x=event, color='c', linestyle='--')
    # plt.xlabel('Time (s)')
    # plt.ylabel('Power (W)')
    # plt.legend()
    # plt.title('Power = Voltage*Current')
    # plt.savefig(folder+'power.pdf',format='pdf',bbox_inches='tight')
    # #plt.savefig(folder+'powerClipped.pdf',format='pdf',bbox_inches='tight')
    # plt.show()
