import time
import pandas as pd
import numpy as np


csv_file_name = "planarProblemBackflip_23012023_frameCorrected_interp"
df_control = pd.read_csv(csv_file_name+".csv")

df_control['q_fl2'] = df_control['q_fl2'].apply(lambda x: x*-1)
df_control['q_fr2'] = df_control['q_fr2'].apply(lambda x: x*-1)
df_control['q_bl2'] = df_control['q_bl2'].apply(lambda x: x*-1)
df_control['q_br2'] = df_control['q_br2'].apply(lambda x: x*-1)
df_control['q_fl3'] = df_control['q_fl3'].apply(lambda x: x*-1)
df_control['q_fr3'] = df_control['q_fr3'].apply(lambda x: x*-1)
df_control['q_bl3'] = df_control['q_bl3'].apply(lambda x: x*-1)
df_control['q_br3'] = df_control['q_br3'].apply(lambda x: x*-1)

df_control['qd_fl2'] = df_control['qd_fl2'].apply(lambda x: x*-1)
df_control['qd_fr2'] = df_control['qd_fr2'].apply(lambda x: x*-1)
df_control['qd_bl2'] = df_control['qd_bl2'].apply(lambda x: x*-1)
df_control['qd_br2'] = df_control['qd_br2'].apply(lambda x: x*-1)
df_control['qd_fl3'] = df_control['qd_fl3'].apply(lambda x: x*-1)
df_control['qd_fr3'] = df_control['qd_fr3'].apply(lambda x: x*-1)
df_control['qd_bl3'] = df_control['qd_bl3'].apply(lambda x: x*-1)
df_control['qd_br3'] = df_control['qd_br3'].apply(lambda x: x*-1)

df_control['Tau_fl2'] = df_control['Tau_fl2'].apply(lambda x: x*-1)
df_control['Tau_fr2'] = df_control['Tau_fr2'].apply(lambda x: x*-1)
df_control['Tau_bl2'] = df_control['Tau_bl2'].apply(lambda x: x*-1)
df_control['Tau_br2'] = df_control['Tau_br2'].apply(lambda x: x*-1)
df_control['Tau_fl3'] = df_control['Tau_fl3'].apply(lambda x: x*-1)
df_control['Tau_fr3'] = df_control['Tau_fr3'].apply(lambda x: x*-1)
df_control['Tau_bl3'] = df_control['Tau_bl3'].apply(lambda x: x*-1)
df_control['Tau_br3'] = df_control['Tau_br3'].apply(lambda x: x*-1)


df_control.to_csv(csv_file_name+"_frameCorrected.csv")

