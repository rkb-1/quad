import time
import pandas as pd
import numpy as np


csv_file_name = "traj_high_freq3"
df_control = pd.read_csv(csv_file_name+".csv")

df_control['q_fl2'] = df_control['q_fl2'].apply(lambda x: x*-1)
df_control['q_fl3'] = df_control['q_fl3'].apply(lambda x: x*-1)
df_control['q_fr2'] = df_control['q_fr2'].apply(lambda x: x*-1)
df_control['q_fr3'] = df_control['q_fr3'].apply(lambda x: x*-1)
df_control['q_bl1'] = df_control['q_bl1'].apply(lambda x: x*-1)
df_control['q_br1'] = df_control['q_br1'].apply(lambda x: x*-1)

df_control['qd_fl2'] = df_control['qd_fl2'].apply(lambda x: x*-1)
df_control['qd_fl3'] = df_control['qd_fl3'].apply(lambda x: x*-1)
df_control['qd_fr2'] = df_control['qd_fr2'].apply(lambda x: x*-1)
df_control['qd_fr3'] = df_control['qd_fr3'].apply(lambda x: x*-1)
df_control['qd_bl1'] = df_control['qd_bl1'].apply(lambda x: x*-1)
df_control['qd_br1'] = df_control['qd_br1'].apply(lambda x: x*-1)

df_control['Tau_fl2'] = df_control['Tau_fl2'].apply(lambda x: x*-1)
df_control['Tau_fl3'] = df_control['Tau_fl3'].apply(lambda x: x*-1)
df_control['Tau_fr2'] = df_control['Tau_fr2'].apply(lambda x: x*-1)
df_control['Tau_fr3'] = df_control['Tau_fr3'].apply(lambda x: x*-1)
df_control['Tau_bl1'] = df_control['Tau_bl1'].apply(lambda x: x*-1)
df_control['Tau_br1'] = df_control['Tau_br1'].apply(lambda x: x*-1)


df_control.to_csv(csv_file_name+"_frameCorrected.csv")

