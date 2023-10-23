#!/usr/bin/env python3

# Copyright 2020 Josh Pieper, jjp@pobox.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Align video to robot logs, assuming that the side of the robot was
slapped in a unique pattern during the video recording.'''

import argparse
from ntpath import join
import numpy as np
import pylab
import subprocess
import tempfile
import pandas as pd
import os
from datetime import datetime

import scipy
import scipy.signal as signal
import scipy.interpolate
import scipy.io
import scipy.io.wavfile

import mjlib.telemetry.file_reader as file_reader

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    #parser.add_argument('-v', '--video', type=str)
    parser.add_argument('-l', '--log', type=str)
    #parser.add_argument('-s', '--video-start', type=float, default=0.0)
    #parser.add_argument('-e', '--video-end', type=float, default=-1.0)
    parser.add_argument('--log-start', type=float, default=0.0)
    parser.add_argument('--log-end', type=float, default=-1.0)
    #parser.add_argument('--distance', type=float, default=1.5,
    #                    help='distance in meters between robot and camera')
    #parser.add_argument('--fudge', type=float, default=0.025)

    args = parser.parse_args()

    fr = file_reader.FileReader(args.log)
    
    folder_name = os.path.splitext(os.path.basename(args.log))[0]
    folder = os.path.join('analysis/', folder_name)
    # os.makedirs(folder)

    # #IMU DATA 

    # imu_data = [(x.data.timestamp, x.data.accel_mps2[0]) #x-component of imu sensor
    #             for x in fr.items(['imu'])]
    # start_s = imu_data[0][0]
    # size_s = imu_data[-1][0] - start_s

    # if args.log_start < 0:
    #     args.log_start = size_s

    # time = np.array([x[0] - start_s for x in imu_data])
    # imu_x = np.array([x[1] for x in imu_data])
    # print("time: ", time)
    
    # imu_df = pd.DataFrame({'t[s]': time, 'imu_x': imu_x})
    # imu_df.to_csv('imu_df.csv')
    
    #pylab.plot(orig_imu_x, orig_imu_y, linewidth=2, label='imu')
    #pylab.legend()
    #pylab.show()
    
    # Input commands
    # print("command data: ")
    # velocity = [(x.data.timestamp, x.data.v_R[0]) for x in fr.items(['qc_command'])] # translational velocity in mps
    # omega = [(x.data.timestamp, x.data.w_R[2]*np.pi/180.0) for x in fr.items(['qc_command'])] #rotational vel in dps, convert to rad/s
    # start_s = velocity[0][0]
    # time = np.array([x[0] - start_s for x in velocity])
    # command_vel = np.array([x[1] for x in velocity])
    # command_omega = np.array([x[1] for x in omega])
    # df_command = pd.DataFrame({'t[s]': time})
    # df_command['command_vel'] = command_vel
    # df_command['command_omega'] = command_omega
    # df_command.to_csv('quad_command_data_3mps_outside.csv')
    
    # Joints control commands
    # i = 0
    # for x in fr.items(['qc_control']):
    #     # print(len([x.data.timestamp]))
    #     if i == 3120:
    #         print(i)
    #         print(x.data.timestamp)
    #         print(x.data.joints[0][3])
    #     i+=1
        
    # i=0
    # for x in fr.items(['qc_control']):
    #     print(len([x.data.joints[0][3]]))
    #     print(x.data.joints[0][3])
    #     i+=1
    #     # print(i)
    #     print(x.data.timestamp)


    for i in range(12):
        j=0
        print("data: ",i)
        # joint_try = [(x.data.joints[0][3]) for x in fr.items(['qc_control'])]
        # print(joint_try[0])
        joint_pos = [(x.data.timestamp, x.data.joints[i][3]*np.pi/180.0) for x in fr.items(['qc_control'])] #pos in degrees, convert to rad
        joint_vel = [(x.data.timestamp, x.data.joints[i][4]*np.pi/180.0) for x in fr.items(['qc_control'])] #vel in dps, convert to rad/s
        joint_tau = [(x.data.timestamp, x.data.joints[i][5]) for x in fr.items(['qc_control'])]
        
        # print(joint_pos, joint_vel, joint_tau)
        start_s = joint_pos[0][0]
        time = np.array([x[0] - start_s for x in joint_pos])
        pos = np.array([x[1] for x in joint_pos])
        vel = np.array([x[1] for x in joint_vel])
        tau = np.array([x[1] for x in joint_tau])
        
        # get accelerations from velocity using finite difference method
        acc = np.gradient(vel,time)
       
        if i<2: #leg1
            pos_name = str("q_fl"+str(i+2))
            vel_name = str("qd_fl"+str(i+2))
            acc_name = str("qdd_fl"+str(i+2))
            tau_name = str("Tau_fl"+str(i+2))
        if (i>2 and i<5): #leg2
            pos_name = str("q_fr"+str(i+2-3))
            vel_name = str("qd_fr"+str(i+2-3))
            acc_name = str("qdd_fr"+str(i+2-3))
            tau_name = str("Tau_fr"+str(i+2-3))
        if (i>5 and i<8): #leg3
            pos_name = str("q_bl"+str(i+2-6))
            vel_name = str("qd_bl"+str(i+2-6))
            acc_name = str("qdd_bl"+str(i+2-6))
            tau_name = str("Tau_bl"+str(i+2-6))
        if (i>8 and i<11): #leg4
            pos_name = str("q_br"+str(i+2-9))
            vel_name = str("qd_br"+str(i+2-9))
            acc_name = str("qdd_br"+str(i+2-9))
            tau_name = str("Tau_br"+str(i+2-9))
        if i==2:
            pos_name = str("q_fl1")
            vel_name = str("qd_fl1")
            acc_name = str("qdd_fl1")
            tau_name = str("Tau_fl1")
        if i==5:
            pos_name = str("q_fr1")
            vel_name = str("qd_fr1")
            acc_name = str("qdd_fr1")
            tau_name = str("Tau_fr1")
        if i==8:
            pos_name = str("q_bl1")
            vel_name = str("qd_bl1")
            acc_name = str("qdd_bl1")
            tau_name = str("Tau_bl1")
        if i==11:
            pos_name = str("q_br1")
            vel_name = str("qd_br1")
            acc_name = str("qdd_br1")
            tau_name = str("Tau_br1")
            
        
        if i==0:
            df = pd.DataFrame({'t[s]': time})
        df[pos_name] = pos
        df[vel_name] = vel
        df[acc_name] = acc
        df[tau_name] = tau
        print(pos_name)
        #pylab.plot(orig_x, orig_y, linewidth=2, label=str('joint '+str(i)))
        #pylab.legend()
        #pylab.show()
    column_names = ["t[s]", "q_fl1", "qd_fl1","qdd_fl1","Tau_fl1","q_fl2", "qd_fl2","qdd_fl2","Tau_fl2","q_fl3", "qd_fl3","qdd_fl3","Tau_fl3",
                            "q_fr1", "qd_fr1","qdd_fr1","Tau_fr1","q_fr2", "qd_fr2","qdd_fr2","Tau_fr2","q_fr3", "qd_fr3","qdd_fr3","Tau_fr3",
                            "q_bl1", "qd_bl1","qdd_bl1","Tau_bl1","q_bl2", "qd_bl2","qdd_bl2","Tau_bl2","q_bl3", "qd_bl3","qdd_bl3","Tau_bl3",
                            "q_br1", "qd_br1","qdd_br1","Tau_br1","q_br2", "qd_br2","qdd_br2","Tau_br2","q_br3", "qd_br3","qdd_br3","Tau_br3"]
    df = df.reindex(columns=column_names)
    print(df.head())
    df.to_csv(folder+'/control_test.csv')
    
    # Joints status output
    
    for i in range(12):
        j=0
        joint_pos = [(x.data.timestamp, x.data.state.joints[i][j+1]*np.pi/180.0) for x in fr.items(['qc_status'])] #pos in degrees, convert to rad
        joint_vel = [(x.data.timestamp, x.data.state.joints[i][j+2]*np.pi/180.0) for x in fr.items(['qc_status'])] #vel in dps, convert to rad/s
        joint_tau = [(x.data.timestamp, x.data.state.joints[i][j+3]) for x in fr.items(['qc_status'])]
        print("data: ",i)
        start_s = joint_pos[0][0]
        time = np.array([x[0] - start_s for x in joint_pos])
        pos = np.array([x[1] for x in joint_pos])
        vel = np.array([x[1] for x in joint_vel])
        tau = np.array([x[1] for x in joint_tau])
        b, a = signal.butter(3, 0.2)
        vel = signal.filtfilt(b, a, vel)

        # get accelerations from velocity using finite difference method
        acc = np.gradient(vel,time)
        acc = signal.filtfilt(b, a, acc)
        tau = signal.filtfilt(b, a, tau)
        if i<2: #leg1
            pos_name = str("q_fl"+str(i+2))
            vel_name = str("qd_fl"+str(i+2))
            acc_name = str("qdd_fl"+str(i+2))
            tau_name = str("Tau_fl"+str(i+2))
        if (i>2 and i<5): #leg2
            pos_name = str("q_fr"+str(i+2-3))
            vel_name = str("qd_fr"+str(i+2-3))
            acc_name = str("qdd_fr"+str(i+2-3))
            tau_name = str("Tau_fr"+str(i+2-3))
        if (i>5 and i<8): #leg3
            pos_name = str("q_bl"+str(i+2-6))
            vel_name = str("qd_bl"+str(i+2-6))
            acc_name = str("qdd_bl"+str(i+2-6))
            tau_name = str("Tau_bl"+str(i+2-6))
        if (i>8 and i<11): #leg4
            pos_name = str("q_br"+str(i+2-9))
            vel_name = str("qd_br"+str(i+2-9))
            acc_name = str("qdd_br"+str(i+2-9))
            tau_name = str("Tau_br"+str(i+2-9))
        if i==2:
            pos_name = str("q_fl1")
            vel_name = str("qd_fl1")
            acc_name = str("qdd_fl1")
            tau_name = str("Tau_fl1")
        if i==5:
            pos_name = str("q_fr1")
            vel_name = str("qd_fr1")
            acc_name = str("qdd_fr1")
            tau_name = str("Tau_fr1")
        if i==8:
            pos_name = str("q_bl1")
            vel_name = str("qd_bl1")
            acc_name = str("qdd_bl1")
            tau_name = str("Tau_bl1")
        if i==11:
            pos_name = str("q_br1")
            vel_name = str("qd_br1")
            acc_name = str("qdd_br1")
            tau_name = str("Tau_br1")
            
        
        if i==0:
            df_status = pd.DataFrame({'t[s]': time})
        df_status[pos_name] = pos
        df_status[vel_name] = vel
        df_status[acc_name] = acc
        df_status[tau_name] = tau
        print(i,pos_name)
    column_names = ["t[s]", "q_fl1", "qd_fl1","qdd_fl1","Tau_fl1","q_fl2", "qd_fl2","qdd_fl2","Tau_fl2","q_fl3", "qd_fl3","qdd_fl3","Tau_fl3",
                            "q_fr1", "qd_fr1","qdd_fr1","Tau_fr1","q_fr2", "qd_fr2","qdd_fr2","Tau_fr2","q_fr3", "qd_fr3","qdd_fr3","Tau_fr3",
                            "q_bl1", "qd_bl1","qdd_bl1","Tau_bl1","q_bl2", "qd_bl2","qdd_bl2","Tau_bl2","q_bl3", "qd_bl3","qdd_bl3","Tau_bl3",
                            "q_br1", "qd_br1","qdd_br1","Tau_br1","q_br2", "qd_br2","qdd_br2","Tau_br2","q_br3", "qd_br3","qdd_br3","Tau_br3"]
    # print(df_status.head())
    df_status = df_status.reindex(columns=column_names)
    # print(df_status.head())
    df_status.to_csv(folder + '/status_test.csv')
    
    ## Legs catesian position, velocity and force data in x,y,and z direction  

    # for i in range(4):
    #     j=1
    #     _pos = [(x.data.timestamp, x.data.state.legs_B[i][j+1]) for x in fr.items(['qc_status'])] 
    #     _vel = [(x.data.timestamp, x.data.state.legs_B[i][j+2]) for x in fr.items(['qc_status'])] 
    #     _force = [(x.data.timestamp, x.data.state.legs_B[i][j+3]) for x in fr.items(['qc_status'])]
    #     _stance = [(x.data.timestamp, x.data.state.legs_B[i][j+4]) for x in fr.items(['qc_status'])]
    #     print("Leg: ",i+1)
    #     start_s = _pos[0][0]
    #     time = np.array([x[0] - start_s for x in _pos])
    #     pos = np.array([x[1] for x in _pos])
    #     vel = np.array([x[1] for x in _vel])
    #     force = np.array([x[1] for x in _force])
    #     stance = np.array([x[1] for x in _stance])
    #     print(pos.shape, vel.shape, force.shape, stance.shape)
    #     df_leg_pos = pd.DataFrame(pos, columns=['pos_x_leg{}'.format(i+1), 'pos_y_leg{}'.format(i+1), 'pos_z_leg{}'.format(i+1)])
    #     df_leg_vel = pd.DataFrame(vel, columns=['vel_x_leg{}'.format(i+1), 'vel_y_leg{}'.format(i+1), 'vel_z_leg{}'.format(i+1)])
    #     df_leg_force = pd.DataFrame(force, columns=['force_x_leg{}'.format(i+1), 'force_y_leg{}'.format(i+1), 'force_z_leg{}'.format(i+1)])
    #     df_leg_stance = pd.DataFrame(stance, columns=['stance_leg{}'.format(i+1)])
    #     if i==0:
    #         df_leg = pd.DataFrame({'t[s]': time})
    #     temp = pd.concat([df_leg_pos,df_leg_vel,df_leg_force,df_leg_stance],axis=1)
    #     df_leg = pd.concat([df_leg, temp], axis = 1)
    # print(df_leg)
    # df_leg.to_csv(dir_name+'leg_measured_data.csv')
    
    # POWER CONSUMPTION DATA

    # power_data = [(x.data.timestamp, x.data.power_W) for x in fr.items(['power'])]
    # start_s = power_data[0][0]
    # size_s = power_data[-1][0] - start_s

    # time = np.array([x[0] - start_s for x in power_data])
    # power = np.array([x[1] for x in power_data])
    # # print("time: ", time)
    
    # power_df = pd.DataFrame({'t[s]': time, 'power_W': power})
    # power_df.to_csv(folder + '/power.csv')
    
    # pylab.plot(time, power, linewidth=2, label='imu')
    # pylab.legend()
    # pylab.show()

    # timings information
    mode_status = [(x.data.timestamp, x.data.mode) for x in fr.items(['qc_status'])]
    phase_timings = [(x.data.timestamp, x.data.state.replay_behavior.mode) for x in fr.items(['qc_status'])]
    start_s = phase_timings[0][0]
    size_s = phase_timings[-1][0] - start_s

    time = np.array([x[0] - start_s for x in phase_timings])
    phases = np.array([x[1] for x in phase_timings])
    replay_mode = np.array([x[1] for x in mode_status])
    print(phases)
    exertion_phase =[]
    flight_phase =[]
    land_phase =[]
    replay_start =[]
    replay_end =[]
    for i in range(len(time)):
        if (replay_mode[i]==11 and replay_mode[i-1]==7):
            replay_start.append(time[i])
        if (phases[i]==1 and phases[i-1]==0 or phases[i]==1 and phases[i-1]==3):
            # print(time[i], phases[i])
            exertion_phase.append(time[i])
        if (phases[i]==2 and phases[i-1]==1):
            # print(time[i], phases[i])
            flight_phase.append(time[i])
        if (phases[i]==3 and phases[i-1]==2):
            # print(time[i],phases[i])
            land_phase.append(time[i])
        if (phases[i]==4 and phases[i-1]==3):
            # print(time[i], phases[i])
            replay_end.append(time[i])

    # print("Replay start: ", replay_start)
    # print(" Exertion Phases: ", exertion_phase)
    # print(" Flight phase : ", flight_phase)
    # print("Land phase: ", land_phase)
    # print("Replay end : ", replay_end)  

    phase_timings_dict = {
        'replay_start' : replay_start,
        'exertion_phase' : exertion_phase,
        'flight_phase' : flight_phase,
        'land_phase' : land_phase,
        'replay_end' : replay_end,
    }
    np.savez(folder + '/phase_timings.npz', **phase_timings_dict)
    # if(mode == 11)

    print("done")

if __name__ == '__main__':
    main()

