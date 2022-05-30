import mysql.connector
from mysql.connector import Error
from numpy import NaN
import pandas as pd
from tkinter.filedialog import askopenfilename
import math

#Establish connection to the lab's database
connection = mysql.connector.connect(host="192.185.39.245",
                               database="christof_labdata",
                               user="christof_python",
                               password="PythonIsTheBest")

#Check if connection is established and print server information
if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()

        #Get tuples of names and rts from the database ordered by name
        cursor.execute("""SELECT name, rt
                          FROM zic_philic_master_ms1_rt_table 
                          ORDER BY name ASC""")
        db_name_rt_tuple = cursor.fetchall()

        #Create a pandas dataframe from the db tuple list
        db_df = pd.DataFrame(db_name_rt_tuple, columns=["name", "rt"]).astype({"name": str})     

        #Read metabolite standard CSV file with names and rts
        fpath = askopenfilename()
        std_df = pd.read_csv(fpath)

       
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
        
        #Create new column "rt_mean" with all values null and type float
        std_df["rt_mean"] = NaN
        
        #Iterate through the name column and split names with " / " to a list
        for row in std_df["name"]:
                if " / " in row:
                        std_df["name"][row] = row.split(" / ")
                        print(row)
        
        #Explode creates a new row for every list item in the row
        std_df = std_df.explode("name")
        
                        
        
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
        missing_met_list = [x for x in list(db_df['name'].unique()) if x not in list(std_df['name'].unique())]

        #Generic database updating sql query
        query = """UPDATE zic_philic_master_ms1_rt_table
                   SET rt = %s
                   WHERE name = %s;"""

        #Iterate through the std df and update all the values corresponding by name
        for index in range(len(std_df)):
                met_name = std_df["name"].iloc[index]
                rt = std_df["rt_mean"].iloc[index].astype(float)

                data = (rt, met_name)

                if met_name in db_df['name'].values:
                        cursor.execute(query, data)
                        connection.commit()
                        print("Successfully updated: ", met_name)

                else:
                        print("Could not update: ", met_name)


        print("Missing metabolites:", missing_met_list)
        #Commit changes and close the connection to the database when the script is finished
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

else:
    print("Connection is not established with the database")
