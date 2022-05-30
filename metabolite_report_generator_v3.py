import math
import datetime
import pandas as pd
import numpy as np
import matplotlib as mp
import matplotlib.colors as mc
import matplotlib.cm as cm
from scipy import stats
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.font as font
from tkinter.filedialog import askopenfilename
from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from matplotlib.colors import Normalize
from matplotlib.collections import LineCollection

import io 

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import *
from reportlab.platypus import SimpleDocTemplate, Paragraph, \
    Spacer, Image, PageBreak, Table, Flowable, KeepTogether, \
    TableStyle as TS, HRFlowable
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import inch

import os
from matplotlib import font_manager as fm, rcParams
import json

#Report global variables
TYLE_TITLE = PS(name='Heading1', fontSize=28, leading=16, spaceAfter=0.2 * inch)
STYLE_TITLE_MIN = PS(name='Heading2', fontSize=22, leading=16, spaceAfter=0.2 * inch)
STYLE_H1 = PS(name='Heading1', fontSize=18, leading=16)
STYLE_H4 = PS(name='Heading4', fontSize=10, leading=16)
STYLE_MET_NAME = PS(name="Metname", fontSize=10, leading=10, spaceAfter=0.1 * inch)
STYLE_MET_RATIO_NAME = PS(name="Metname", fontSize=10, leading=10, spaceAfter=0.1 * inch)

HR_LINE = HRFlowable(width="100%", thickness=2, color="black", spaceBefore=1, spaceAfter=1, hAlign='CENTER',
                     vAlign='CENTER', dash=None)
HR_LINE_MIN = HRFlowable(width="100%", thickness=0.8, color="black", spaceBefore=1, spaceAfter=1, hAlign='CENTER',
                         vAlign='CENTER', dash=None)
VGAP_04 = Spacer(0, 0.4 * inch)
VGAP_02 = Spacer(0, 0.2 * inch)



class MetaboliteData():

    def __init__(self):
        
        filename = askopenfilename()

        self.iso_data = pd.read_excel(filename, sheet_name="Normalized", dtype={0: 'str'})
        self.pool_size_data = pd.read_excel(filename, sheet_name="PoolAfterDF", dtype={0: 'str'})

        self.pool_size_data.iloc[:, 0] = self.pool_size_data.iloc[:, 0].str.strip()

        self.analyte_classes = pd.read_csv("C:\\Users\\nmatulionis\\Desktop\\python_report\\analyte_classes_philic.csv",
                                dtype={0: 'str', 1: 'str', 2: 'str'})

        self.group_names = {}
        i = 1
        for name in Home_GUI.groups_str.get().split(","):
            self.group_names[i] = name
            i += 1

        #Normalizing Data Script
        self.normalizing_rows = []
        self.normalizing_names = []
        row_index = 0

        for row in self.pool_size_data['Compound']:

            if "*" in row:
                self.normalizing_rows.append(row_index)
                self.normalizing_names.append(row)

            row_index += 1

        if len(self.normalizing_rows) > 0:

            for col in range(1, len(self.pool_size_data.columns)):

                normalization_number = 1

                for row in self.normalizing_rows:
                    
                    normalization_number *= float(self.pool_size_data.iloc[row, col])
                    self.pool_size_data.iloc[1:, col] /= normalization_number                    

        print("_______________DATA__IS__NORMALIZED_____________")

        print(self.pool_size_data)       
        

        #Metabolite Ratio Implementation
        self.analyte_classes = self.analyte_classes['analyte_name'].dropna()

        for row in self.analyte_classes:

            if "<div>" in row:
                mets = row.split("<div>")

                row1 = self.pool_size_data[self.pool_size_data['Compound'] == mets[0]]
                row2 = self.pool_size_data[self.pool_size_data['Compound'] == mets[1]]

                if row1.empty == False and row2.empty == False:

                    ratio_vals = [str("[" + mets[0] + "/" + mets[1] + "]")]

                    for col in range(1, len(self.pool_size_data.columns)):

                        v1 = row1.iloc[0, col]
                        v2 = row2.iloc[0, col]
                        val = 0

                        if (math.isnan(v1) == False and math.isnan(v2) == False and v2 > 0):
                            val = v1 / v2

                        ratio_vals.append(val)

                    self.pool_size_data.loc[row_index] = ratio_vals
                    row_index += 1

        print("____________METABOLITE__RATIOS__IMPLEMENTED__________________")

        print(self.pool_size_data) 


        




    def getNumTotalGroups(self):
        total_num_groups = np.where(self.pool_size_data[self.pool_size_data['Compound'] == "group"])
        return total_num_groups

    

    def getMetaboliteData(self, group_num, met_name):
        
        sample_cols = np.where(self.pool_size_data[self.pool_size_data['Compound'] == "group"].values == group_num)[1]
        
        sub_data = self.pool_size_data[self.pool_size_data['Compound'] == met_name]
        sub_data.sort_values(by=sub_data.columns[2])
        sub_data = sub_data.iloc[:, sample_cols]
        return sub_data


    def getGroupedMetaboliteData(self, met_name):
        gp_data = pd.DataFrame()
        gp_std = pd.DataFrame()

        print(self.group_names)

        num_groups = self.getNumTotalGroups()

        for group_id in range(1, num_groups + 1):
            group_iso_dist = self.getMetaboliteData(group_id, met_name)
            group_mean = group_iso_dist.mean(axis=1).multiply(100)
            pd.concat([gp_data, group_mean], ignore_index=True)
            

            group_stdev = group_iso_dist.std(axis=1).multiply(100)
            
            pd.concat([gp_std, group_stdev], ignore_index=True)

        default_group_names = {}

        for i in range(1, num_groups + 1):
            default_group_names[i - 1] = "group " + repr(i)

        for group_id in self.group_names:
            default_group_names[group_id - 1] = self.group_names[group_id]

        gp_data = gp_data.rename(default_group_names)
        gp_std = gp_std.rename(default_group_names)

        for i in range(0, len(gp_data.columns)):
            default_group_names[gp_data.columns[i]] = "M" + repr(i)

        gp_data = gp_data.rename(default_group_names, axis="columns")
        gp_std = gp_std.rename(default_group_names, axis="columns")

        return (gp_data, gp_std)


    def getFractionalContributionData(self, met_name):

        def frac(val):
            return 1 - val

        gp_data = pd.DataFrame()

        num_groups = self.getNumTotalGroups()

        for group_id in range(1, num_groups + 1):
            group_iso_dist = self.getMetaboliteData(group_id, met_name)
            if group_iso_dist.empty: continue
            new_row = group_iso_dist.iloc[0, :].apply(frac).multiply(100)

            mappings = {}
            for i in range(0, new_row.size):
                mappings[new_row.index[i]] = i;

            pd.concat([gp_data,new_row.rename(mappings)], ignore_index=True)
            gp_data = gp_data.replace(np.nan, 0)

        default_group_names = {}
        for i in range(1, num_groups + 1):
            default_group_names[i - 1] = "group " + repr(i)

        for group_id in self.group_names:
            default_group_names[group_id - 1] = self.group_names[group_id]

        return gp_data.rename(default_group_names).transpose()





class MetaboliteReport():

    def __init__(self, ):
        
        pass
        
        
class PdfImage(Flowable):
    def __init__(self, fig, width=200, height=200, bgcolor="white"):
        self.img_width = width
        self.img_height = height
        idata = io.BytesIO()
        fig.savefig(idata, format='pdf', bbox_inches='tight', facecolor=bgcolor)
        idata.seek(0)
        self.img_data = self.form_xo_reader(idata)

    def form_xo_reader(self, imgdata):
        page, = PdfReader(imgdata).pages
        return pagexobj(page)

    def wrap(self, width, height):
        return self.img_width, self.img_height

    def drawOn(self, canv, x, y, _sW=0):
        if _sW > 0 and hasattr(self, 'hAlign'):
            a = self.hAlign
            if a in ('CENTER', 'CENTRE', 'TA_CENTER'):
                x += 0.5 * _sW
            elif a in ('RIGHT', 'TA_RIGHT'):
                x += _sW
            elif a not in ('LEFT', 'TA_LEFT'):
                raise ValueError("Bad hAlign value " + str(a))
        canv.saveState()
        img = self.img_data
        if isinstance(img, PdfDict):
            xscale = self.img_width / img.BBox[2]
            yscale = self.img_height / img.BBox[3]
            canv.translate(x, y)
            canv.scale(xscale, yscale)
            canv.doForm(makerl(canv, img))
        else:
            canv.drawImage(img, x, y, self.img_width, self.img_height)
        canv.restoreState()
        

class HomeGUI:

    def __init__(self, window):
        self.window = window
        window.title("Metabolite Report Generator v3")

        self.menu_title_list = ["Isotopomer Analysis", "Pool Size Analysis"]
        self.font =  fm.FontProperties(fname="C:\\Users\\nmatulionis\\Desktop\\python_report\\fonts\\Open_Sans\\OpenSans-Regular.ttf")

        self.title_str = tk.StringVar(value=self.menu_title_list[0])
        self.title_option = tk.OptionMenu(window, self.title_str, *self.menu_title_list).grid(row=0, column=1, padx=5, pady=10)

        self.project_str = tk.StringVar()
        tk.Label(window, text="Project").grid(sticky="w", row=1, padx=(5, 20))
        project_entry = tk.Entry(window, textvariable=self.project_str, width=50).grid(sticky="w", row=1, column=1, pady=10, padx=5)

        self.exp_title = tk.StringVar()
        tk.Label(window, text="Experiment Title").grid(sticky="w", row=2, padx=(5, 20))
        exp_entry = tk.Entry(window, textvariable=self.exp_title, width=50).grid(sticky="w", row=2, column=1, pady=10, padx=5)

        self.leader_str = tk.StringVar()
        tk.Label(window, text="Leader").grid(sticky="w", row=3, padx=(5, 20))
        leader_entry = tk.Entry(window, textvariable=self.leader_str, width=50).grid(sticky="w", row=3, column=1, pady=10, padx=5)

        tk.Label(window, text="Experimental Details").grid(sticky="w", row=4, padx=(10, 20))
        self.description_box = tk.Text(window, height=6, width=50, wrap="word")
        self.description_box.grid(sticky="w", row=4, column=1, padx=5, pady=10)

        self.groups_str = tk.StringVar()
        tk.Label(window, text="Group Names (,)").grid(sticky="w", row=5, padx=(5, 20))
        self.groups_entry = tk.Entry(window, textvariable=self.groups_str, width=50).grid(sticky="w", row=5, column=1, pady=10, padx=5)

        self.start_button = tk.Button(window, text="Generate Report", command=main).grid(sticky="w", row=6, column=1, padx=5, pady=5)
        self.save_entry_button = tk.Button(window, text="Save Entry", command=self.savePreviousEntry).grid(sticky="w", row=7, column=1, padx=5, pady=5)
        self.load_entry_button = tk.Button(window, text="Load Entry", command=self.loadPreviousEntry).grid(sticky="w", row=8, column=1, padx=5, pady=5)


    def savePreviousEntry(self):

        data = {}
        data['previous entry'] = []
        data['previous entry'].append({
            'project_str': self.project_str.get(),
            'exp_title': self.exp_title.get(),
            'leader_str': self.leader_str.get(),
            'description_box': self.description_box.get("1.0", "end-1c"),
            'groups_str': self.groups_str.get()
        })

        with open('previous_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)


    def loadPreviousEntry(self):
        with open('previous_data.json', 'r') as json_file:
            data = json.load(json_file)
            self.project_str.set(data["previous entry"][0]["project_str"])
            self.exp_title.set(data["previous entry"][0]["exp_title"])
            self.leader_str.set(data["previous entry"][0]["leader_str"])
            self.description_box.insert("end-1c", data["previous entry"][0]["description_box"])
            self.groups_str.set(data["previous entry"][0]["groups_str"])










def main():

    
    datasheet = MetaboliteData()

    print("Metabolite Data Check")
    
    print(datasheet.getFractionalContributionData("glucose"))

    root.destroy()




root = tk.Tk()
Home_GUI = HomeGUI(root)

root.mainloop()








