# %% [markdown]
# # 8760 Load Analysis 
# ## Purpose
# The goal of this code is to take 8760 .csv files from electrical system and analyze when and where the load is not being met. It was specifically designed with the output from the HOMER microgrid software in mind. 

# %%
# import modules 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import os 
import pathlib
from glob  import glob

# %%
#load csv file file path 
dir_path = os.path.join(
    pathlib.Path.home(),
        'code-projects',
        'load-8760'
        )


data_path = glob(os.path.join(dir_path,'*.csv'))[0]

data_path

# %%
#load data and check structure 
data = pd.read_csv(
    data_path,
    delimiter=',',
    header= 0,
    index_col='Time',
    skiprows=1
    )

data = data[data.index.notnull()]

data.head()

# %% [markdown]
# Separate time into hour, day, and month

# %%
# Convert time to hour, day, and month

#Reset Index 
data=data.reset_index()


data["Time"] = pd.to_datetime(data["Time"])

data["hour"] = data['Time'].map(lambda x: x.hour)
data["day"] = data['Time'].map(lambda x: x.day)
data["month"] = data['Time'].map(lambda x: x.month)

data.head()



# %% [markdown]
# # Calculation 
# Since the data is loaded, we are going to filer the amount of hours were capacity shortage > 0 

# %%
# filter  how many hours load not met (capacity shortage > 0)
#first need to force column to convert to float 
data['Capacity Shortage'] = data['Capacity Shortage'].astype(float)

capacity_shortage_df = data[data['Capacity Shortage'] > 0 ]

#Calculate how man hour load is unmet   

hours_shortage = len(capacity_shortage_df)

hours_shortage

# %% [markdown]
# Now to try with battery capacity (<30%)
# 
# 

# %%
data['Generic 1kWh Li-Ion State of Charge'] = data['Generic 1kWh Li-Ion State of Charge'].astype(float)

battery_shortage_df = data[data['Generic 1kWh Li-Ion State of Charge'] < 30 ]

hours_battery_shortage = len(battery_shortage_df)

hours_battery_shortage


# %%
#hours with unmet electrical load 
data['Unmet Electrical Load'] = data['Unmet Electrical Load'].astype(float)

unmet_load_df = data[data['Unmet Electrical Load'] > 0.01 ]

hours_unmet_load = len(unmet_load_df)

hours_per_day = unmet_load_df.groupby(['month','day']).size()

num_days_outages = len(hours_per_day)

hours_per_day

# %%
# find consecutive hours with outages 

def count_consecutive_groups(df):
    groups = (df['hour'].diff() != 1).cumsum()  # Identify consecutive groups
    return len(groups.unique()) 

outages_year = count_consecutive_groups (unmet_load_df)

outages_year

 

# %%
outages_day = unmet_load_df.groupby(['month', 'day']).apply(count_consecutive_groups)

outages_day

# %% [markdown]
# Print all  results 

# %%
pd.set_option('display.max_rows', None)
print(hours_per_day)
print(outages_day)
print(
    'Hours with Capacity Shortage=',
    hours_shortage, 'hours')

print(
    'Hours with Battery Capacity <30%= ',
    hours_battery_shortage, 'hours'
)
print(
    '# of Days with Outages (unmet load)= ',
    num_days, 'days'
)
print(
    '# of outages per year= ',
    outages_year, 'outages'
)



