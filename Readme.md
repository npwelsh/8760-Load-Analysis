# Readme

## 1.	Overview 
This python script is to take the output 8760 CVS files  produced by the HOMER microgrid software and produce a summary of the data.  That summary includes number of hours with capacity shortage, the number of hours battery capacity is below 30%, the System Average Interruption Duration Index in number of hours of outage in a year, the System Average Interruption Frequency Index in number of distinct outages per year, and total number of days with outages.  It also produces a file with a summary of each of those outages, both as a spreadsheet and a heat map.  The goal of this is to provide additional metrics and insights to multiple load profiles and system sizes for 100% renewable energy microgrid, to compare against with the other outputs from HOMER to see what system meet the most reliability metrics 

## 2.	How to run Code 
The script was built with MiniConda installation of Python in a Juptyer notebook. The code should run with your preferred method of running Jupyter notebooks.  If not, here is a step by step method to run the code. 
1.	Install MiniConda 
2.	Open Jupyter Notebook App.  The App will open a page in your browser 
3.	Scroll to the appropriate Jupyter Notebook File, 8760_code_GUI.ipynb
4.	In the open notebook tab, click the Cell dropdown menu.  Click ‘Run All’
5.	Another window with a tkinter symbol (a feather) should pop up.  Click select files
6.	Navigate to the folder containing the .csvs.  If there are no .csv in the folder an error will occur 
7.	Select ‘Process Files’ The code will begin going through the files
8.	When code is done, another message box will show up.  Results will show up in a folder called ‘results’ in the folder containing the .csvs selected earlier.  
