# # 8760 Load Analysis v.0.0.1
# ## Purposea
# The goal of this code is to take 8760 .csv files from electrical systems and analyze when and where the load is not being met. It was specifically designed with the output from the HOMER microgrid software in mind. 

# %%
# import modules 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from tkinter import Tk, filedialog, Label, Button, Entry, messagebox
import seaborn as snsup
import os 
import pathlib
from glob  import glob

# %%
# define APP using class

class HomerLoadAnalysis:
    
    
    def get_files(self):
        #Get the selected directory 
        dir_path= filedialog.askdirectory()
        if not dir_path:
            messagebox.showwarning("No Directory", "Please select a Folder")
            return
        
        #find all .csv files in the directory
    
        self.data_files = glob(os.path.join(dir_path,'*.csv'))
        if not self.data_files:
            messagebox.showerror("No Files", "No CSV Files found in the selected directory")
            return
        
        self.results_dir = os.path.join(dir_path, 'results')
        os.makedirs(self.results_dir, exist_ok=True)

        messagebox.showinfo("Files Selected", f"Found {len(self.data_files)} CSV files.")

    #Function  to process CSV Files
    def process_files(self):
    
        if not self.data_files:
            messagebox.showerror("No Files", "Please Select a folder First")
            return
        
        #function within functions 
        def count_consecutive_groups(df):
            groups = (df['hour'].diff() != 1).cumsum()  # Identify consecutive groups
            return len(groups.unique()) 
        
        # define function for plotting heatmap from days 

        def plot_yearly_heatmap(outages_day):
            outages_day['date'] = pd.to_datetime({
            'year': 2000,  # Adjust the year if needed
            'month': outages_day['month'],
            'day': outages_day['day']
        })

            # Create a full-year calendar
            full_year = pd.date_range(start='2000-01-01', end='2000-12-31')
            full_year_df = pd.DataFrame({'date': full_year})
            full_year_df['day_of_week'] = full_year_df['date'].dt.dayofweek
            full_year_df['week'] = full_year_df['date'].dt.isocalendar().week

            # Merge outages_day into the full year to align with calendar dates
            full_year_df = full_year_df.merge(
                outages_day[['date', '#_of_outages']],
                on='date',
                how='left'
            )
            full_year_df['#_of_outages'] = full_year_df['#_of_outages'].fillna(0)  # Fill missing values with 0

            # Aggregate data to ensure unique combinations of week and day_of_week
            full_year_df_agg = full_year_df.groupby(['week', 'day_of_week']).agg({'#_of_outages': 'sum'}).reset_index()

            # Pivot the data for heat map structure
            heatmap_data = full_year_df_agg.pivot(index='week', columns='day_of_week', values='#_of_outages')

            #Title Heatmap based on file name
            heatmap_title = 'Daily Outages Heat Map for ' + f"{os.path.basename(data_path)}" 

            # Plot the heat map
            plt.figure(figsize=(12, 8))
            sns.heatmap(
                heatmap_data,
                cmap='cool',  # Color palette
                linewidths=0.5,   # Grid lines
                annot=False,      # Set True if you want annotations
                cbar_kws={'label': 'Number of Outages'}
            )
            plt.title(heatmap_title, fontsize=16)
            plt.xlabel('Day of the Week', fontsize=12)
            plt.ylabel('Week of the Year', fontsize=12)
            plt.xticks(ticks=np.arange(7), labels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=45)
            plt.yticks(rotation=0)
            plt.tight_layout()

            # Save the heat map
            output_path = os.path.join(self.results_dir, f"{os.path.basename(data_path)}_heatmap.png")
            plt.savefig(output_path)
            plt.close()

            return print(f"Saved heat map for {data_path} to {self.results_dir}")
    
        #list to store all results

        results = []
        outages_summary=[]


        for data_path in self.data_files:
            data = pd.read_csv(
                data_path,
                delimiter=',',
                header= 0,
                index_col='Time',
                skiprows=1)
            
            data= data[data.index.notnull()]

            data=data.reset_index() #Reset Index
            data["Time"] = pd.to_datetime(data["Time"])
            data["hour"] = data['Time'].map(lambda x: x.hour)
            data["day"] = data['Time'].map(lambda x: x.day)
            data["month"] = data['Time'].map(lambda x: x.month)
            

            #Initialize N/A
            hours_shortage = '0'
            hours_battery_shortage = '0'
            hours_unmet_load = '0' 
            num_days_outages = '0' 
            outages_year = '0' 
            # filter  how many hours load not met (capacity shortage > 0)
            if 'Capacity Shortage' in data.columns:
                data['Capacity Shortage'] = data['Capacity Shortage'].astype(float) #first need to force column to convert to float 
                capacity_shortage_df = data[data['Capacity Shortage'] > 0 ]
                hours_shortage = len(capacity_shortage_df)
        

            #Calculate how many hours annual load is unmet   #for Battery <30%
            if 'Generic 1kWh Li-Ion State of Charge' in data.columns:
                data['Generic 1kWh Li-Ion State of Charge'] = data['Generic 1kWh Li-Ion State of Charge'].astype(float)
                battery_shortage_df = data[data['Generic 1kWh Li-Ion State of Charge'] < 30 ]
                hours_battery_shortage = len(battery_shortage_df)

            # To find hours with Unmet Electrical Load
            if 'Unmet Electrical Load' in data.columns:
                data['Unmet Electrical Load'] = data['Unmet Electrical Load'].astype(float)
                unmet_load_df = data[data['Unmet Electrical Load'] > 0.01 ]
                hours_unmet_load = len(unmet_load_df)
            
            hours_per_day = unmet_load_df.groupby(['month','day']).size().reset_index()
            hours_per_day.columns=['month','day','hours_with_unmet_load']
            #Calculate number of days with outages 
            num_days_outages = len(hours_per_day)
            # Calulate number of outages per year
            outages_year = count_consecutive_groups (unmet_load_df)
            #Calculate number of distinct outages 
            outages_day = unmet_load_df.groupby(['month', 'day']).apply(count_consecutive_groups).reset_index()
            outages_day.columns = ['month','day','#_of_outages']


            #save heatmap for each file
            plot_yearly_heatmap(outages_day)

            #complile a list of results for summary 
            results.append ({
                'File': os.path.basename(data_path),
                'Hours with Capacity Shortage': hours_shortage,
                'Hours with Battery <30%': hours_battery_shortage,
                'SAIDI (hrs outages/year)': hours_unmet_load,
                'Days with Outages': num_days_outages,
                'SAIFI (outages/year)': outages_year,
            
            })

            #Merge hours_per_day and outages_day data frames
            if not hours_per_day.empty and not outages_day.empty:
                merged = pd.merge(hours_per_day, outages_day, on=['month', 'day'], how='outer')
                merged['File'] = os.path.basename(data_path)
                outages_summary.append(merged)

        results_df = pd.DataFrame(results)
        outages_summary_df = pd.concat(outages_summary, ignore_index=True)

        summary_path = os.path.join(self.results_dir, 'outages_summary_results.csv')
        results_df.to_csv(summary_path, index=False)

        outages_daily_detail_path = os.path.join(self.results_dir,'outages_daily_details.csv')
        outages_summary_df.to_csv(outages_daily_detail_path, index=False)

        messagebox.showinfo("Processing Complete", f"Results saved to {self.results_dir}")    

    def __init__(self, root):
        self.root = root
        self.root.title("8760 Load Processor v.0.0.1")
        self.root.geometry("400x300")

        self.data_files = []

        #directory selection box
        Label(root, text="Select a Folder Containing 8760 CSV Files").pack(pady=10)
        Button(root, text="Select Folder", command=self.get_files).pack(pady=5)

        #Process Button 
        Button(root, text = "Process Files", command=self.process_files).pack(pady=20)
        
    



    
        
    
    


# %%
# Run the GUI 

root = Tk()
app=HomerLoadAnalysis(root)
root.mainloop()


