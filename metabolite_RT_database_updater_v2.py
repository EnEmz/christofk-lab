import mysql.connector
from mysql.connector import Error
import pandas as pd
from tkinter.filedialog import askopenfilename
import tkinter as tk
#from ttkwidgets.autocomplete import AutocompleteCombobox
import math

class DatabaseObj():
	
	def __init__(self):
		#Establish connection to the lab's database
		self.connection = mysql.connector.connect(host="192.185.39.245",
									database="christof_labdata",
									user="christof_python",
									password="PythonIsTheBest")

		#Check if connection is established and print server information
		if self.connection.is_connected():
			self.db_info = self.connection.get_server_info()
			print("Connected to MySQL Server version ", self.db_info)
			self.cursor = self.connection.cursor()
   
			#Set a new timeout to 15 min which will close connection with no activity
			self.cursor.execute('SET interactive_timeout = 900')

			#Get tuples of names and rts from the database ordered by name
			self.cursor.execute("""SELECT name, rt
								FROM zic_philic_master_ms1_rt_table 
								ORDER BY name ASC""")
			self.db_name_rt_tuple = self.cursor.fetchall()

			#Create a pandas dataframe from the db tuple list
			self.db_df = pd.DataFrame(self.db_name_rt_tuple, columns=["name", "rt"]).astype({"name": str})

	
	def get_db_name_list(self):
		
		list_str = self.db_df["name"].values.tolist()
		return list_str
		

	def update_all_rts(self):

		#Read metabolite standard CSV file with names and rts
		fpath = askopenfilename()
		std_df = pd.read_csv(fpath, encoding='ISO-8859-1')

	
		std_df = std_df.rename(columns={'row identity (main ID)': 'name'})

		#Drop duplicate rows
		std_df.drop_duplicates(subset="name", keep=False, inplace=True)
		std_df.dropna(axis="columns",inplace=True)

		#Rename M0 at the end of each metabolite name in the standard CSV file
		std_df['name'] = std_df['name'].map(lambda x: x.rstrip(' M0'))
		
		#Look for extra name rows and drop them, reset the index of the dataframe
		std_df = std_df[~std_df['name'].isin(['row identity (main ID)'])]
		std_df = std_df.reset_index()
		del std_df["index"]
		
		#Create new column "rt_mean" with all values 0 and type float
		std_df["rt_mean"] = 0.0
		
		#Loop through all dataset ignoring the name col and calculate the mean in each row
		for row in range(len(std_df)):
				row_sum = 0.0
				num_samples_in_mean = 0.0

				for col in range(1,len(std_df.columns)-1):
						if std_df.iloc[row,col] != 0:
								row_sum =+ float(std_df.iloc[row,col])
								num_samples_in_mean =+ 1
								
						else:
								pass

				mean = row_sum / num_samples_in_mean
				std_df.at[row,'rt_mean'] = mean
		
		std_df = std_df.round({'rt_mean': 2})
		print("Std rts successfully averaged.")

		#Create a list with metabolite names that are missing in std 
		self.missing_met_list = [x for x in list(self.db_df['name'].unique()) if x not in list(std_df['name'].unique())]

		#Generic database updating sql query
		query = """UPDATE zic_philic_master_ms1_rt_table
				SET rt = %s
				WHERE name = %s;"""

		#Iterate through the std df and update all the values corresponding by name
		for index in range(len(std_df)):
				met_name = std_df["name"].iloc[index]
				rt = std_df["rt_mean"].iloc[index].astype(float)

				data = (float(rt), met_name)

				if met_name in self.db_df['name'].values:
						self.cursor.execute(query, data)
						self.connection.commit()
						print(f"Updated {met_name} to {rt}.")

				else:
						print("Could not update ", met_name)


		print("Missing metabolites: ", self.missing_met_list)


	def update_single_rt(self, met_name, rt):

		query = """UPDATE zic_philic_master_ms1_rt_table
				   SET rt = %s
				   WHERE name = %s;"""

		data = (rt, met_name)
		self.cursor.execute(query, data)
		self.connection.commit()

		print(f"Updated {met_name} to {rt}")
  
		


class RTGui():

	def __init__(self, master, *args, **kwargs):
		self.master = master
		self.frame = tk.Frame(self.master)

		self.met_list = database.get_db_name_list()

		self.font = ("Helvetica", 12)

		self.met_value = tk.Entry(self.frame, width = 30, font = self.font)
		#self.metabolite_search = AutocompleteCombobox(self.frame, width = 30, font = self.font, completevalues = self.met_list)
		self.rt_value = tk.Entry(self.frame, width = 10, font = self.font)
		
		self.all_rt_button = tk.Button(self.frame, text = "Update all RTs", font = self.font, width = 15, command = database.update_all_rts)
		self.single_rt_button = tk.Button(self.frame, text = "Update single RT", font = self.font, width = 15, command = lambda : database.update_single_rt(self.met_value.get(),self.rt_value.get()))
		self.quit_button = tk.Button(self.frame, text = "Quit", font = self.font, width = 15, command = self.closeWindow)

		self.met_value.grid(row=0,column=0,padx=5,pady=5)
		self.rt_value.grid(row=0,column=1,padx=5,pady=5)

		self.single_rt_button.grid(row=1,column=1,padx=5,pady=5)
		self.all_rt_button.grid(row=2,column=1,padx=5,pady=10)
		self.quit_button.grid(row=3,column=1,padx=5,pady=5)

		self.frame.pack()


	def closeWindow(self):
     
		database.cursor.close()
		database.connection.close()
		print("Connection to database closed.")
  
		self.master.destroy()



if __name__ == "__main__":

	database = DatabaseObj()
 
	root = tk.Tk()
	app = RTGui(root)
	root.mainloop()

	