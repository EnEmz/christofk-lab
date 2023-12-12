import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, simpledialog
from pandastable import Table
import re

path_custom_list_neg = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\custom_list_neg.csv"
path_custom_list_pos = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\custom_list_pos.csv"

path_current_neg = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\current_zic_philic_ms1_rt_C13_neg.csv"
path_current_pos = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\current_zic_philic_ms1_rt_C13_pos.csv"

# Read the CSV files and extract unique metabolite names
def get_unique_metabolites(file_path):
    df = pd.read_csv(file_path)
    metabolites = df['name'].str.split(' M', n=1, expand=True)[0].str.strip().unique()
    return metabolites

unique_metabolites_neg = get_unique_metabolites(path_current_neg)
unique_metabolites_pos = get_unique_metabolites(path_current_pos)

class MetaboliteApp:
    def __init__(self, root):
        self.root = root
        self.df_analysis_pool = None
        self.df_analysis_iso = None
        self.iso_present = False
        self.filtered_df_neg = None
        self.filtered_df_pos = None
        self.path_entries = {}
        self.deleted_items_neg = []
        self.deleted_items_pos = []
        self.updating_selection = False
        self.prevent_loop = False
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')
        self.tab_metabolomics_conversion = ttk.Frame(self.notebook)
        self.tab_missing_mets_detection = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_metabolomics_conversion, text='Metabolomics Conversion Normalization')
        self.notebook.add(self.tab_missing_mets_detection, text='Missing Mets Detection')
        
        # Add the terminal frame at the bottom
        self.terminal_frame = tk.Frame(self.root)
        self.terminal_frame.pack(fill='x', side='bottom')
        self.terminal = tk.Text(self.terminal_frame, height=10, bg='black', fg='white')
        self.terminal.pack(fill='x')
        
        self.df_met_neg = pd.read_csv(path_current_neg, index_col='index')
        self.df_met_pos = pd.read_csv(path_current_pos, index_col='index')
        
        self.df_met_total = pd.concat([self.df_met_neg, self.df_met_pos], ignore_index=True)
        self.met_list_total = self.df_met_total['name'].str.split(' M').str[0].unique().tolist()

        self.root.title("Metabolite Data Editor")
        self.root.geometry("1000x1200")

        self.setup_missing_mets_ui()
        self.setup_metabolomics_conversion_ui()


    def setup_missing_mets_ui(self):
        listbox_font = ("Helvetica", 12)
        
        # Configure the grid for the Missing Mets Detection tab
        self.tab_missing_mets_detection.grid_rowconfigure(1, weight=1)
        self.tab_missing_mets_detection.grid_columnconfigure(0, weight=1)  # Negative Data
        self.tab_missing_mets_detection.grid_columnconfigure(1, weight=0)  # Negative RT
        self.tab_missing_mets_detection.grid_columnconfigure(2, weight=1)  # Positive Data
        self.tab_missing_mets_detection.grid_columnconfigure(3, weight=0)  # Positive RT
        
        
        # File path entry and Load button frame
        file_path_frame = tk.Frame(self.tab_missing_mets_detection)
        file_path_frame.grid(row=0, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

        # Text entry for file path
        self.file_path_entry = tk.Entry(file_path_frame)
        self.file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Load button
        load_button = tk.Button(file_path_frame, text="Upload Analysis File", command=self.load_file)
        load_button.pack(side=tk.RIGHT, padx=5)

        # Path configuration frame
        self.path_display_frame = tk.LabelFrame(self.tab_missing_mets_detection, text="Current File Paths")
        self.path_display_frame.grid(row=4, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        self.path_display_frame.grid_columnconfigure(1, weight=1)

        # Filepath display for csv files
        self.display_path_missing("Custom Met List Neg:", path_custom_list_neg, 0)
        self.display_path_missing("Custom Met List Pos:", path_custom_list_pos, 1)
        self.display_path_missing("Full Met List Neg:", path_current_neg, 2)
        self.display_path_missing("Full Met List Pos:", path_current_pos, 3)

        # Edit paths button
        edit_paths_button = tk.Button(self.tab_missing_mets_detection, text="Edit Paths", command=self.edit_paths)
        edit_paths_button.grid(row=5, column=0, columnspan=1, sticky='ew', padx=5, pady=5)

        # Negative Data frame
        frame_neg = tk.Frame(self.tab_missing_mets_detection)
        frame_neg.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        frame_neg.grid_rowconfigure(0, weight=1)
        frame_neg.grid_columnconfigure(0, weight=1)
        label_neg = tk.Label(frame_neg, text="Negative Data")
        label_neg.pack(fill='x')
        scrollbar_neg = tk.Scrollbar(frame_neg, orient="vertical")
        self.listbox_neg = tk.Listbox(frame_neg, yscrollcommand=scrollbar_neg.set, selectmode='extended', font=listbox_font)
        scrollbar_neg.config(command=self.listbox_neg.yview)
        scrollbar_neg.pack(side="right", fill="y")
        self.listbox_neg.pack(fill="both", expand=True)
        self.button_del_neg = tk.Button(frame_neg, text="Delete Selected", command=self.delete_selected_neg)
        self.button_del_neg.pack(fill='x')
        
        # Negative rt frame
        self.frame_rt_neg = tk.Frame(self.tab_missing_mets_detection)
        self.frame_rt_neg.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        label_rt_neg = tk.Label(self.frame_rt_neg, text="Negative RT")
        label_rt_neg.pack(fill='x')
        self.listbox_rt_neg = tk.Listbox(self.frame_rt_neg, font=listbox_font)
        self.listbox_rt_neg.pack(fill="both", expand=True)
        
        # Positive Data frame
        frame_pos = tk.Frame(self.tab_missing_mets_detection)
        frame_pos.grid(row=1, column=2, sticky='nsew', padx=5, pady=5)
        frame_pos.grid_rowconfigure(0, weight=1)  # Add weight to the row inside frame_pos
        frame_pos.grid_columnconfigure(0, weight=1)
        label_pos = tk.Label(frame_pos, text="Positive Data")
        label_pos.pack(fill='x')
        scrollbar_pos = tk.Scrollbar(frame_pos, orient="vertical")
        self.listbox_pos = tk.Listbox(frame_pos, yscrollcommand=scrollbar_pos.set, selectmode='extended', font=listbox_font)
        scrollbar_pos.config(command=self.listbox_pos.yview)
        scrollbar_pos.pack(side="right", fill="y")
        self.listbox_pos.pack(fill="both", expand=True)
        self.button_del_pos = tk.Button(frame_pos, text="Delete Selected", command=self.delete_selected_pos)
        self.button_del_pos.pack(fill='x')

        # Positive rt frame
        self.frame_rt_pos = tk.Frame(self.tab_missing_mets_detection)
        self.frame_rt_pos.grid(row=1, column=3, sticky='nsew', padx=5, pady=5)
        label_rt_pos = tk.Label(self.frame_rt_pos, text="Positive RT")
        label_rt_pos.pack(fill='x')
        self.listbox_rt_pos = tk.Listbox(self.frame_rt_pos, font=listbox_font)
        self.listbox_rt_pos.pack(fill="both", expand=True)
        
        # Initialize a Spinbox for M number input
        max_m_value = 10
        self.m_number_spinbox = CustomSpinbox(self.tab_missing_mets_detection, from_=0, to=max_m_value, write_to_terminal=self.write_to_terminal, initial_value=0)
        self.m_number_label = tk.Label(self.tab_missing_mets_detection, text="Enter M#:")
        self.m_number_label.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Add a label to display the text "Max M value:"
        self.max_m_label_text = tk.Label(self.tab_missing_mets_detection, text="Max M value:")
        self.max_m_label_text.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        # Add another label to display the actual max M value
        self.max_m_label = tk.Label(self.tab_missing_mets_detection, text="")
        self.max_m_label.grid(row=3, column=2, sticky='ew', padx=5, pady=5)

        # Save and quit buttons
        self.button_save = tk.Button(self.tab_missing_mets_detection, text="Save Data", command=self.save_data)
        self.button_save.grid(row=2, column=0, columnspan=1, sticky='ew', padx=5, pady=5)
        button_quit = tk.Button(self.tab_missing_mets_detection, text="Quit", command=root.destroy)
        button_quit.grid(row=3, column=0, columnspan=1, sticky='ew', padx=5, pady=5)

        self.button_del_neg.config(state='disabled')
        self.button_del_pos.config(state='disabled')
        self.button_save.config(state='disabled')
        self.listbox_neg.config(state='disabled')
        self.listbox_pos.config(state='disabled')
        
        root.bind('<BackSpace>', self.on_key_press)
        root.bind('<z>', self.on_key_press)
        for i in range(10):
            root.bind(f'<Key-{i}>', self.on_number_press)
        root.bind("`", self.on_number_press)
            

        self.listbox_neg.bind('<Double-Button-1>', self.on_double_click)
        self.listbox_pos.bind('<Double-Button-1>', self.on_double_click)
        self.listbox_rt_neg.bind('<Double-Button-1>', self.edit_rt_value)
        self.listbox_rt_pos.bind('<Double-Button-1>', self.edit_rt_value)
        
        # Bind the select event to a new method for both metabolites and RT listboxes
        self.listbox_neg.bind('<<ListboxSelect>>', self.on_metabolite_select_neg)
        self.listbox_rt_neg.bind('<<ListboxSelect>>', self.on_rt_select_neg)
        self.listbox_pos.bind('<<ListboxSelect>>', self.on_metabolite_select_pos)
        self.listbox_rt_pos.bind('<<ListboxSelect>>', self.on_rt_select_pos)
        
        
    def setup_metabolomics_conversion_ui(self):
        # Conversion Section
        normalization_label = tk.Label(self.tab_metabolomics_conversion, text="Data Conversion", font=("Helvetica", 14))
        normalization_label.pack(pady=(20, 10))
        
        # Upload CSV File UI
        self.file_path_frame_conv = tk.Frame(self.tab_metabolomics_conversion)
        self.file_path_frame_conv.pack(fill='x', pady=15)
        self.file_path_entry_conv = tk.Entry(self.file_path_frame_conv)
        self.file_path_entry_conv.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.upload_button_conv = tk.Button(self.file_path_frame_conv, text="Upload Metabolomics CSV File", command=self.upload_csv_file)
        self.upload_button_conv.pack(side=tk.RIGHT, padx=5)
        
        # Checkbox for "Labelling Present"
        self.labelling_present_var = tk.BooleanVar()
        self.checkbox_labelling = tk.Checkbutton(self.tab_metabolomics_conversion, text="Labelling Present", variable=self.labelling_present_var)
        self.checkbox_labelling.pack(pady=10)

        # Convert button
        self.convert_button = tk.Button(self.tab_metabolomics_conversion, text="Convert Metabolomics File", command=self.convert_metabolomics_file)
        self.convert_button.pack(pady=10)
        
        # Normalization Section
        normalization_label = tk.Label(self.tab_metabolomics_conversion, text="Normalization", font=("Helvetica", 14))
        normalization_label.pack(pady=(20, 10))

        # Frame for normalization file upload
        normalization_file_frame = tk.Frame(self.tab_metabolomics_conversion)
        normalization_file_frame.pack(fill='x', pady=10)
        self.normalization_file_entry = tk.Entry(normalization_file_frame)
        self.normalization_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        normalization_file_button = tk.Button(normalization_file_frame, text="Upload Normalization File", command=self.upload_normalization_file)
        normalization_file_button.pack(side=tk.RIGHT, padx=5)
        
        # Frame for normalization options
        normalization_frame = tk.Frame(self.tab_metabolomics_conversion)
        normalization_frame.pack(pady=5)
        
         # Pool Normalize by Label and Combobox
        pool_normalize_label = tk.Label(normalization_frame, text="Pool Normalize by:")
        pool_normalize_label.grid(row=0, column=0, padx=5)

        self.pool_normalize_var = tk.StringVar(value='none')  # Default value set to 'none'
        self.pool_normalize_combobox = ttk.Combobox(normalization_frame, textvariable=self.pool_normalize_var, width=15)
        self.pool_normalize_combobox['values'] = ('none', 'TIC', 'Custom')
        self.pool_normalize_combobox.grid(row=0, column=1, padx=15)

        # Isotopologue Normalize by Label and Combobox
        isotopologue_normalize_label = tk.Label(normalization_frame, text="Isotopologue Normalize by:")
        isotopologue_normalize_label.grid(row=0, column=2, padx=15)

        self.isotopologue_normalize_var = tk.StringVar(value='none')  # Default value set to 'none'
        self.isotopologue_normalize_combobox = ttk.Combobox(normalization_frame, textvariable=self.isotopologue_normalize_var, width=15)
        self.isotopologue_normalize_combobox['values'] = ('none', 'Glucose M6', 'Glutamine M5')
        self.isotopologue_normalize_combobox.grid(row=0, column=3, padx=5)
        
        # Button for triggering pool data normalization
        self.normalize_pool_button = tk.Button(normalization_frame, text="Normalize Pool Data", command=self.normalize_pool_data)
        self.normalize_pool_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Button for triggering isotopologue data normalization
        self.normalize_iso_button = tk.Button(normalization_frame, text="Normalize Iso Data", command=self.normalize_iso_data)
        self.normalize_iso_button.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky='ew')

        # File Combiner Section
        combiner_label = tk.Label(self.tab_metabolomics_conversion, text="File Combiner", font=("Helvetica", 14))
        combiner_label.pack(pady=(20, 10))

        # Main File Upload
        self.main_file_frame = tk.Frame(self.tab_metabolomics_conversion)
        self.main_file_frame.pack(fill='x', pady=5)
        self.main_file_path_entry = tk.Entry(self.main_file_frame)
        self.main_file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        main_upload_button = tk.Button(self.main_file_frame, text="Upload Main File", command=lambda: self.upload_file(self.main_file_path_entry))
        main_upload_button.pack(side=tk.RIGHT, padx=5)

        # Additional File Upload
        self.additional_file_frame = tk.Frame(self.tab_metabolomics_conversion)
        self.additional_file_frame.pack(fill='x', pady=5)
        self.add_file_path_entry = tk.Entry(self.additional_file_frame)
        self.add_file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        additional_upload_button = tk.Button(self.additional_file_frame, text="Upload Additional File", command=lambda: self.upload_file(self.add_file_path_entry))
        additional_upload_button.pack(side=tk.RIGHT, padx=5)

        # Export File Name Entry and Combine Button
        self.combine_frame = tk.Frame(self.tab_metabolomics_conversion)
        self.combine_frame.pack(fill='x', pady=10)
        tk.Label(self.combine_frame, text="Export File Name:").pack(side=tk.LEFT, padx=5)
        self.export_file_name_entry = tk.Entry(self.combine_frame)
        self.export_file_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.combine_button = tk.Button(self.combine_frame, text="Combine Files", command=self.combine_files)
        # Place Combine button in the center
        self.combine_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Adjust the combine button to center it below the file path entries
        self.combine_frame.pack_configure(pady=(5, 10))
        self.combine_button.pack_configure(side=tk.LEFT, padx=5, expand=True)
        
        # Create a frame specifically for displaying paths in this tab
        self.path_display_frame_conversion = tk.LabelFrame(self.tab_metabolomics_conversion, text="File Paths")
        self.path_display_frame_conversion.pack(side='bottom', fill='x', padx=5, pady=5)
        
        # Use display_path to add paths
        self.display_path_conversion("Full Met List Neg:", path_current_neg, 0)
        self.display_path_conversion("Full Met List Pos:", path_current_pos, 1)

                    

    def upload_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path_entry_conv.delete(0, tk.END)
            self.file_path_entry_conv.insert(0, file_path)
            self.write_to_terminal("File uploaded successfully")
        else:
            self.write_to_terminal("No file selected")

    def is_csv_file(self, filename):
        return filename.endswith('.csv')
        
        
    def write_to_terminal(self, message):
        self.terminal.insert(tk.END, message + '\n')
        self.terminal.see(tk.END)  # Scroll to the end to see latest message
        
    def on_number_press(self, event):
        if event.char.isdigit():
            digit = int(event.char)
            self.m_number_spinbox.set_value(digit)
        elif event.char == "`":
            self.m_number_spinbox.set_value(0)
        
    def edit_rt_value(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            current_value = widget.get(index)
            new_value = simpledialog.askstring("Edit RT Value", "New RT Value:", initialvalue=current_value)
            if new_value is not None:
                widget.delete(index)
                widget.insert(index, new_value)
                self.write_to_terminal(f"RT updated from {current_value} to {new_value}")
        
    def display_path_missing(self, label, path, row):
        tk.Label(self.path_display_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        path_label = tk.Label(self.path_display_frame, text=path, anchor='w')
        path_label.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        self.path_display_frame.grid_rowconfigure(row, weight=1)

    def edit_paths(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Paths")
        edit_window.geometry("800x250")  # Adjust size if needed

        # Configure column widths for a tighter layout
        edit_window.grid_columnconfigure(0, minsize=200)  # Adjust minsize as needed
        edit_window.grid_columnconfigure(1, minsize=20)   # Space between label and entry
        edit_window.grid_columnconfigure(2, minsize=100)  # Adjust minsize for button column

        self.edit_path_widget("Custom Met List Neg:", path_custom_list_neg, 0, edit_window)
        self.edit_path_widget("Custom Met List Pos:", path_custom_list_pos, 2, edit_window)
        self.edit_path_widget("Full Met List Neg:", path_current_neg, 4, edit_window)
        self.edit_path_widget("Full Met List Pos:", path_current_pos, 6, edit_window)

        save_button = tk.Button(edit_window, text="Save Changes", command=lambda: self.save_path_changes(edit_window))
        save_button.grid(row=8, column=0, columnspan=3, sticky='ew', padx=5, pady=5)


    def edit_path_widget(self, label, current_path, row, parent_window):
        # Label and Upload button in the same row
        tk.Label(parent_window, text=label).grid(row=row, column=0, sticky=tk.W, pady=(10, 0))  # Padding for visual separation
        upload_button = tk.Button(parent_window, text="Upload", command=lambda: self.upload_path(label))
        upload_button.grid(row=row, column=2, padx=5, pady=(10, 0))

        # Entry to display the file path in the next row
        entry = tk.Entry(parent_window, width=125)
        entry.insert(0, current_path)
        entry.grid(row=row + 1, column=0, columnspan=3, sticky='ew')
        self.path_entries[label] = entry
        
        
    def save_path_changes(self, edit_window):
        global path_custom_list_neg, path_custom_list_pos, path_current_neg, path_current_pos

        path_custom_list_neg = self.path_entries["Custom Met List Neg:"].get()
        path_custom_list_pos = self.path_entries["Custom Met List Pos:"].get()
        path_current_neg = self.path_entries["Full Met List Neg:"].get()
        path_current_pos = self.path_entries["Full Met List Pos:"].get()

        self.display_path_missing("Custom Met List Neg:", path_custom_list_neg, 0)
        self.display_path_missing("Custom Met List Pos:", path_custom_list_pos, 1)
        self.display_path_missing("Full Met List Neg:", path_current_neg, 2)
        self.display_path_missing("Full Met List Pos:", path_current_pos, 3)

        edit_window.destroy()
        
        
    def upload_path(self, label):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry = self.path_entries[label]
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
        
    
    def is_excel_file(self, filename):
        return filename.endswith('.xls') or filename.endswith('.xlsx')
    
    def is_csv_file(self, filename):
        return filename.endswith('.csv')
    
    def load_file(self):
        analysis_fpath = filedialog.askopenfilename()
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, analysis_fpath)

        if self.is_excel_file(analysis_fpath):
            xls = pd.ExcelFile(analysis_fpath)

            if 'PoolAfterDF' in xls.sheet_names:
                self.df_analysis_pool = pd.read_excel(analysis_fpath, sheet_name='PoolAfterDF')
            else:
                self.write_to_terminal("'PoolAfterDF' excel sheet not present.")
                return

            if 'Normalized' in xls.sheet_names:
                self.df_analysis_iso = pd.read_excel(analysis_fpath, sheet_name='Normalized')
                self.iso_present = True
            else:
                self.write_to_terminal("'Normalized' excel sheet not present.")
                self.iso_present = False

            self.perform_operations()
            
            # Set the state of all elements to 'normal' to enable them
            self.listbox_neg.config(state='normal')
            self.listbox_pos.config(state='normal')
            self.button_del_neg.config(state='normal')
            self.button_del_pos.config(state='normal')
            self.button_save.config(state='normal')
            
            # Populate the listboxes here
            self.update_listboxes()
            
        else:
            self.write_to_terminal("Not an Excel file uploaded.")
            
            
    def perform_operations(self):
        if self.df_analysis_pool is None or self.df_analysis_pool.empty:
            self.write_to_terminal("No data in df_analysis_pool. Load data first.")
            return
        
        pool_duplicates = self.df_analysis_pool['Compound'][self.df_analysis_pool['Compound'].duplicated()].unique().tolist()
        if pool_duplicates:
            self.write_to_terminal("Duplicate values in 'Compound' column:")
            self.write_to_terminal(pool_duplicates)
        else:
            self.write_to_terminal("No metabolite duplicates found.")
            
        met_list_pool = self.df_analysis_pool['Compound'].str.strip().tolist()
        met_list_not_pool = set(self.met_list_total) - set(met_list_pool)

        if self.iso_present:
            met_list_iso = self.df_analysis_iso['Compound'].str.strip().unique().tolist()
            met_list_not_iso = set(self.met_list_total) - set(met_list_iso)
        else:
            met_list_not_iso = set()

        # Combine the missing metabolite lists from both PoolAfterDF and Normalized (if present)
        combined_met_list_missing = list(met_list_not_pool.union(met_list_not_iso))

        self.df_met_neg['simple_name'] = self.df_met_neg['name'].str.split(' M').str[0]
        self.df_met_pos['simple_name'] = self.df_met_pos['name'].str.split(' M').str[0]

        self.filtered_df_neg = self.df_met_neg[self.df_met_neg['simple_name'].isin(combined_met_list_missing)]
        self.filtered_df_pos = self.df_met_pos[self.df_met_pos['simple_name'].isin(combined_met_list_missing)]

        self.filtered_df_neg = self.filtered_df_neg.reset_index(drop=True)
        self.filtered_df_pos = self.filtered_df_pos.reset_index(drop=True)

        
        
    def update_listboxes(self):
        padding = " " * 3

        self.listbox_neg.delete(0, tk.END)
        self.listbox_pos.delete(0, tk.END)
        self.listbox_rt_neg.delete(0, tk.END)
        self.listbox_rt_pos.delete(0, tk.END)

        if self.filtered_df_neg is not None and not self.filtered_df_neg.empty:
            unique_names_neg = self.filtered_df_neg['simple_name'].unique()
            for name in unique_names_neg:
                padded_name = f"{padding}{name}{padding}"
                self.listbox_neg.insert(tk.END, padded_name)

                rt_value = self.filtered_df_neg[self.filtered_df_neg['simple_name'] == name]['rt'].iloc[0]
                self.listbox_rt_neg.insert(tk.END, rt_value)

        if self.filtered_df_pos is not None and not self.filtered_df_pos.empty:
            unique_names_pos = self.filtered_df_pos['simple_name'].unique()
            for name in unique_names_pos:
                padded_name = f"{padding}{name}{padding}"
                self.listbox_pos.insert(tk.END, padded_name)
                rt_value = self.filtered_df_pos[self.filtered_df_pos['simple_name'] == name]['rt'].iloc[0]
                self.listbox_rt_pos.insert(tk.END, rt_value)

                   
    # Updated delete_selected_neg function
    def delete_selected_neg(self, event=None):
        selected_items = self.listbox_neg.curselection()
        for item in selected_items[::-1]:
            simple_name_to_delete = self.listbox_neg.get(item).strip()
            rt_to_delete = self.listbox_rt_neg.get(item)
            self.deleted_items_neg.append((simple_name_to_delete, rt_to_delete))
            self.listbox_neg.delete(item)
            self.listbox_rt_neg.delete(item)

    # Updated delete_selected_pos function
    def delete_selected_pos(self, event=None):
        selected_items = self.listbox_pos.curselection()
        for item in selected_items[::-1]:
            simple_name_to_delete = self.listbox_pos.get(item).strip()
            rt_to_delete = self.listbox_rt_pos.get(item)
            self.deleted_items_pos.append((simple_name_to_delete, rt_to_delete))
            self.listbox_pos.delete(item)
            self.listbox_rt_pos.delete(item)
            
            
    # Updated restore_last_deleted_item function
    def restore_last_deleted_item(self, listbox, listbox_rt, deleted_stack):
        padding = " " * 3
        if deleted_stack:
            last_deleted = deleted_stack.pop()
            padded_name = f"{padding}{last_deleted[0]}{padding}"
            listbox.insert(tk.END, padded_name)
            listbox_rt.insert(tk.END, last_deleted[1])

    # Updated on_key_press function
    def on_key_press(self, event):
        focused_widget = self.root.focus_get()
        
        if event.keysym == 'BackSpace':
            if focused_widget == self.listbox_neg:
                self.delete_selected_neg()
            elif focused_widget == self.listbox_pos:
                self.delete_selected_pos()
        
        if event.keysym.lower() == 'z':
            if focused_widget == self.listbox_neg:
                self.restore_last_deleted_item(self.listbox_neg, self.listbox_rt_neg, self.deleted_items_neg)
            elif focused_widget == self.listbox_pos:
                self.restore_last_deleted_item(self.listbox_pos, self.listbox_rt_pos, self.deleted_items_pos)
                
                
    def on_double_click(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            base_molecule_name = widget.get(index).strip()
            self.copy_mz_to_clipboard(base_molecule_name)


    def copy_mz_to_clipboard(self, base_molecule_name):
        # Get the selected M number from the CustomSpinbox
        selected_m_number = self.m_number_spinbox.value.get()

        try:
            # Check if the entered M number is a valid integer
            m_number_int = int(selected_m_number)
            # Append the M number to the base molecule name
            molecule_name_with_m = f"{base_molecule_name} M{m_number_int}"
        except ValueError:
            # If not a valid integer, default to M0
            molecule_name_with_m = f"{base_molecule_name} M0"
            self.write_to_terminal(f"Invalid M number '{selected_m_number}', defaulted to M0")

        # Ensure no leading/trailing whitespace
        self.df_met_total['name'] = self.df_met_total['name'].str.strip()

        # Look up the molecule
        molecule_entry = self.df_met_total[self.df_met_total['name'] == molecule_name_with_m]
        if not molecule_entry.empty:
            mz_value = molecule_entry['mz'].iloc[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(str(mz_value))
            self.write_to_terminal(f"mz value '{mz_value}' for '{molecule_name_with_m}' copied to clipboard")
        else:
            self.write_to_terminal(f"mz value for '{molecule_name_with_m}' not found")
        
    
    def clear_highlight(self, listbox):
        for i in range(listbox.size()):
            listbox.itemconfig(i, {'bg': 'white'})

    def highlight_item(self, listbox, index):
        self.clear_highlight(listbox)
        listbox.itemconfig(index, {'bg': 'lightgray'})


    def clear_metabolite_highlights(self):
        self.clear_highlight(self.listbox_neg)
        self.clear_highlight(self.listbox_pos)
        
    def clear_rt_highlights(self):
        self.clear_highlight(self.listbox_rt_neg)
        self.clear_highlight(self.listbox_rt_pos)


    def on_metabolite_select_neg(self, event):
        if self.prevent_loop:
            return
        self.prevent_loop = True
        try:
            index = self.listbox_neg.curselection()
            if index:
                index = index[0]
                base_molecule_name = self.listbox_neg.get(index).strip()
                # Update the max M value label
                self.update_max_m_label(base_molecule_name)
                self.clear_rt_highlights()
                self.clear_metabolite_highlights()
                self.highlight_item(self.listbox_rt_neg, index)
        finally:
            self.prevent_loop = False


    def on_rt_select_neg(self, event):
        if self.prevent_loop:
            return
        self.prevent_loop = True
        try:
            index = self.listbox_rt_neg.curselection()
            if index:
                index = index[0]
                self.clear_metabolite_highlights()
                self.clear_rt_highlights()
                self.highlight_item(self.listbox_neg, index)
        finally:
            self.prevent_loop = False


    def on_metabolite_select_pos(self, event):
        if self.prevent_loop:
            return
        self.prevent_loop = True
        try:
            index = self.listbox_pos.curselection()
            if index:
                index = index[0]
                base_molecule_name = self.listbox_pos.get(index).strip()
                # Update the max M value label
                self.update_max_m_label(base_molecule_name)
                self.clear_rt_highlights()
                self.clear_metabolite_highlights()
                self.highlight_item(self.listbox_rt_pos, index)
        finally:
            self.prevent_loop = False


    def on_rt_select_pos(self, event):
        if self.prevent_loop:
            return
        self.prevent_loop = True
        try:
            index = self.listbox_rt_pos.curselection()
            if index:
                index = index[0]
                self.clear_metabolite_highlights()
                self.clear_rt_highlights()
                self.highlight_item(self.listbox_pos, index)
        finally:
            self.prevent_loop = False
            
            
    def find_max_m_value(self, base_molecule_name):
        pattern = f'{re.escape(base_molecule_name)} M(\\d+)'

        m_values = self.df_met_total['name'].str.extract(pattern)[0].dropna().astype(int)

        return m_values.max() if not m_values.empty else 0


    def update_max_m_label(self, base_molecule_name):
        max_m_value = self.find_max_m_value(base_molecule_name)
        self.max_m_label.config(text=str(max_m_value))

        # Update the Spinbox range
        self.m_number_spinbox.to = max_m_value  # Update this line
        
        
    def countdown_before_exit(self, seconds):
        if seconds > 0:
            self.write_to_terminal(f"Closing in {seconds} seconds...")
            # Call this method again after 1000 milliseconds (1 second) with decremented seconds
            self.root.after(1000, lambda: self.countdown_before_exit(seconds - 1))
        else:
            self.root.destroy()


    def save_data(self):
        try:
            # Collect remaining names from listboxes
            remaining_names_neg = [self.listbox_neg.get(idx).strip() for idx in range(self.listbox_neg.size())]
            remaining_names_pos = [self.listbox_pos.get(idx).strip() for idx in range(self.listbox_pos.size())]

            # When filtering the dataframes, explicitly create copies
            self.filtered_df_neg = self.df_met_neg[self.df_met_neg['simple_name'].isin(remaining_names_neg)].copy()
            self.filtered_df_pos = self.df_met_pos[self.df_met_pos['simple_name'].isin(remaining_names_pos)].copy()

            # Now, you can safely drop the 'simple_name' column
            self.filtered_df_neg.drop(columns=['simple_name'], inplace=True)
            self.filtered_df_pos.drop(columns=['simple_name'], inplace=True)

            # Reset the index of the DataFrames
            self.filtered_df_neg.reset_index(drop=True, inplace=True)
            self.filtered_df_pos.reset_index(drop=True, inplace=True)

            # Save the DataFrames to CSV
            self.filtered_df_neg.to_csv(path_custom_list_neg, index=True)
            self.filtered_df_pos.to_csv(path_custom_list_pos, index=True)
            self.write_to_terminal("Data saved successfully.")
            
            self.countdown_before_exit(5)
            
        except Exception as e:
            messagebox.showerror("Error", "Failed to save data: " + str(e))
            self.write_to_terminal("Error: " + str(e))  # For terminal output
            
            
    def convert_metabolomics_file(self):
        file_path = self.file_path_entry_conv.get()
        if not file_path or not self.is_csv_file(file_path):
            self.write_to_terminal("No valid CSV file selected.")
            return

        try:
            df = pd.read_csv(file_path)

            # Process column names
            df.columns = [col.replace('___pos', '') if '___pos' in col else col for col in df.columns]
            df.columns = [self.replace_p_with_dot(col) for col in df.columns]

            if self.labelling_present_var.get():
                self.convert_save_csv_file(df, file_path)
            else:
                self.convert_save_excel_file(df, file_path)

        except Exception as e:
            self.write_to_terminal(f"Error in file conversion: {e}")

    def replace_p_with_dot(self, string):
        return re.sub(r'(\d)p(\d)', r'\1.\2', string)

    def convert_save_csv_file(self, df, file_path):
        new_file_path = file_path.replace('.csv', '_edited.csv')
        df.to_csv(new_file_path, index=False)
        self.write_to_terminal(f"File saved successfully as {new_file_path}")

    def convert_save_excel_file(self, df, file_path):
        new_file_path = file_path.replace('.csv', '_edited.xlsx')
        df.drop(columns=['Formula', 'IsotopeLabel'], errors='ignore', inplace=True)
        with pd.ExcelWriter(new_file_path) as writer:
            df.to_excel(writer, sheet_name='PoolAfterDF', index=False)
        self.write_to_terminal(f"File saved successfully as {new_file_path}")
        
        
    def upload_normalization_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            self.normalization_file_entry.delete(0, tk.END)
            self.normalization_file_entry.insert(0, file_path)
            self.write_to_terminal("Normalization file uploaded successfully")
        else:
            self.write_to_terminal("No file selected")
    
    
    def normalize_iso_data(self):
        normalization_file_path = self.normalization_file_entry.get()
        isotopologue_norm_method = self.isotopologue_normalize_var.get()
        self.write_to_terminal(f"Normalization selected: Isotopologue - {isotopologue_norm_method}")
        
        # Check if the file is uploaded and is an Excel file
        if not normalization_file_path or not self.is_excel_file(normalization_file_path):
            self.write_to_terminal("No valid Excel file selected for normalization.")
            return
        
        try:
            xls = pd.ExcelFile(normalization_file_path)
            if "Corrected" not in xls.sheet_names:
                self.write_to_terminal("'Corrected' sheet not found in the Excel file.")
                return

            # Load PoolAfterDF sheet for further processing
            df_pool = pd.read_excel(normalization_file_path, sheet_name='Corrected')

            if isotopologue_norm_method == 'none':
                return
            
            # Normalization logic based on isotopologue normalization method
            # Check for isotopologue normalization
            if isotopologue_norm_method != 'none':
                
                # Load Corrected sheet for further processing
                df_corrected = pd.read_excel(normalization_file_path, sheet_name='Corrected')
                # Implement isotopologue normalization logic here
                # ...

            self.write_to_terminal("Normalization completed.")
            
        except Exception as e:
            self.write_to_terminal(f"Error during pool normalization: {e}")
        
        
    def normalize_pool_data(self):
        
        normalization_file_path = self.normalization_file_entry.get()
        pool_norm_method = self.pool_normalize_var.get()
        self.write_to_terminal(f"Normalization selected: Pool - {pool_norm_method}")

        # Check if the file is uploaded and is an Excel file
        if not normalization_file_path or not self.is_excel_file(normalization_file_path):
            self.write_to_terminal("No valid Excel file selected for normalization.")
            return

        try:
            xls = pd.ExcelFile(normalization_file_path)
            if "PoolAfterDF" not in xls.sheet_names:
                self.write_to_terminal("'PoolAfterDF' sheet not found in the Excel file.")
                return

             # Load PoolAfterDF sheet for further processing
            df_pool_original = pd.read_excel(normalization_file_path, sheet_name='PoolAfterDF')
            df_pool_normalized = df_pool_original.copy()  # Make a copy for normalization

            if pool_norm_method == 'none':
                return
            
            if pool_norm_method == "TIC":
                if "TIC" not in xls.sheet_names:
                    self.write_to_terminal("'TIC' sheet not found in the Excel file.")
                    return

                # Normalize PoolAfterDF by TIC values
                df_tic = pd.read_excel(normalization_file_path, sheet_name='TIC')
                
                for index, row in df_pool_normalized.iterrows():
                    compound = row['Compound']
                    if 'quantity/sample' in compound.lower():
                        continue
                    
                     # Set is_neg to true for 'trifluoromethanesulfonate'
                    if 'trifluoromethanesulfonate' in compound.lower():
                        is_neg = True
                    else:
                        is_neg = compound in unique_metabolites_neg

                    is_pos = compound in unique_metabolites_pos
                    
                    if is_neg or is_pos:
                        tic_row = df_tic.loc[df_tic['row identity (main ID)'] == ('TIC_neg' if is_neg else 'TIC_pos')]
                        if tic_row.empty:
                            self.write_to_terminal(f"No TIC values found for {'negative (TIC_neg)' if is_neg else 'positive (TIC_pos)'} ions.")
                            return
                        for col in df_pool_normalized.columns[1:]:
                            df_pool_normalized.at[index, col] = df_pool_normalized.at[index, col] / tic_row.iloc[0][col]
                    else:
                        self.write_to_terminal(f"Compound {compound} not found in positive or negative metabolite lists.")
                        continue

            elif pool_norm_method != "TIC":
                # For Custom or any other metabolite selected from the combobox
                normalization_metabolite = pool_norm_method
                normalization_row = df_pool_normalized[df_pool_normalized['Compound'] == normalization_metabolite]

                if normalization_row.empty:
                    self.write_to_terminal(f"Normalization metabolite '{normalization_metabolite}' not found in 'Compound' column.")
                    pass

                # Extracting the row as a Series for easy division
                normalization_values = normalization_row.iloc[0][1:]

                # Normalize other rows by the selected metabolite's values
                for index, row in df_pool_normalized.iterrows():
                    if row['Compound'] != normalization_metabolite:
                        for col in df_pool_normalized.columns[1:]:
                            df_pool_normalized.at[index, col] = df_pool_normalized.at[index, col] / normalization_values[col]

                self.write_to_terminal(f"Pool data normalized using the compound '{normalization_metabolite}'.")
                
            # Export the normalized data
            self.export_normalized_pool_data(df_pool_original, df_pool_normalized)

        except Exception as e:
            self.write_to_terminal(f"Error during pool normalization: {e}")
            
            
    def export_normalized_pool_data(self, df_pool_original, df_pool_normalized):
        normalization_file_path = self.normalization_file_entry.get()
        
        if not normalization_file_path or not self.is_excel_file(normalization_file_path):
            self.write_to_terminal("No valid Excel file selected for export.")
            return

        try:
            # Create new file path with '_normalized' appended
            new_file_path = normalization_file_path.rsplit('.', 1)[0] + '_normalized.xlsx'

            # Read the original Excel file
            xls = pd.ExcelFile(normalization_file_path)

            # Prepare a writer object
            with pd.ExcelWriter(new_file_path) as writer:
                # Write the original PoolAfterDF data as 'Unnormalized Pool'
                df_pool_original.to_excel(writer, sheet_name='Unnormalized Pool', index=False)

                # Write the normalized PoolAfterDF data
                df_pool_normalized.to_excel(writer, sheet_name='PoolAfterDF', index=False)

                # Copy all other sheets from the original file
                for sheet_name in xls.sheet_names:
                    if sheet_name not in ['PoolAfterDF']:
                        df_sheet = pd.read_excel(normalization_file_path, sheet_name=sheet_name)
                        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

            self.write_to_terminal(f"Exported normalized data to {new_file_path}")

        except Exception as e:
            self.write_to_terminal(f"Error during data export: {e}")
            
            
    def display_path_conversion(self, label, path, row):
        # Create labels for the path and place them in the conversion path display frame
        tk.Label(self.path_display_frame_conversion, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        path_label = tk.Label(self.path_display_frame_conversion, text=path, anchor='w')
        path_label.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        self.path_display_frame_conversion.grid_rowconfigure(row, weight=1)  
        
        
    def create_file_upload_ui(self, parent, button_text, row):
        file_path_frame = tk.Frame(parent)
        file_path_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        file_path_entry = tk.Entry(file_path_frame)
        file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        upload_button = tk.Button(file_path_frame, text=button_text, command=lambda: self.upload_file(file_path_entry))
        upload_button.pack(side=tk.RIGHT, padx=5)

        return file_path_entry      
    
    def upload_file(self, entry):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
            
    def combine_files(self):
        main_file_path = self.main_file_path_entry.get()
        add_file_path = self.add_file_path_entry.get()
        export_file_name = self.export_file_name_entry.get().strip()

        if not main_file_path or not add_file_path or not export_file_name:
            self.write_to_terminal("Please upload both files and specify an export file name.")
            return

        try:
            # Read the Excel files
            df_main_pool = pd.read_excel(main_file_path, sheet_name="PoolAfterDF")
            df_add_pool = pd.read_excel(add_file_path, sheet_name="PoolAfterDF")

            # Combine the dataframes
            df_main_pool['Compound'] = df_main_pool['Compound'].str.strip()
            df_add_pool['Compound'] = df_add_pool['Compound'].str.strip()
            df_comb = df_main_pool.merge(df_add_pool, on='Compound', how='outer')
            df_comb = df_comb.fillna(0)

            # Export the combined dataframe
            export_dir = "C:/Users/nmatulionis/Desktop/"
            df_comb.T.reset_index().T.to_excel(export_dir + export_file_name, sheet_name='PoolAfterDF', index=False, header=None)

            self.write_to_terminal(f"Files combined and saved as {export_dir + export_file_name}")

        except Exception as e:
            self.write_to_terminal(f"Error during file combination: {e}")
    

                
            
class CustomSpinbox:
    def __init__(self, parent, from_, to, write_to_terminal, initial_value=0):
        self.value = tk.IntVar(value=initial_value)
        self.from_ = from_
        self.to = to
        
        self.write_to_terminal = write_to_terminal

        # Entry widget for the number display
        self.entry = tk.Entry(parent, textvariable=self.value, justify='center', width=5)
        self.entry.grid(row=2, column=2, sticky='ew', padx=5, pady=5)

        # Define a consistent width for buttons
        button_width = 9

        # Create a frame to contain the buttons
        self.button_frame = tk.Frame(parent)
        self.button_frame.grid(row=2, column=3)

        # Increment button
        self.incr_button = tk.Button(self.button_frame, text="▲", command=self.increment, width=button_width)
        self.incr_button.pack(side=tk.LEFT)  # Use pack with side option to place it within the frame

        # Decrement button
        self.decr_button = tk.Button(self.button_frame, text="▼", command=self.decrement, width=button_width)
        self.decr_button.pack(side=tk.LEFT)  # Use pack with side option to place it next to the increment button

        # Reset button
        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset, width=button_width)
        self.reset_button.pack(side=tk.LEFT)  # Use pack with side option to place it next to the decrement button
        
        

    def increment(self):
        if self.value.get() < self.to:
            self.value.set(self.value.get() + 1)

    def decrement(self):
        if self.value.get() > self.from_:
            self.value.set(self.value.get() - 1)

    def reset(self):
        self.value.set(0)
        
        
    def set_value(self, value):
        if self.from_ <= value <= self.to:
            self.value.set(value)
        else:
            self.value.set(self.from_)



# Running the Application
root = tk.Tk()
app = MetaboliteApp(root)
root.mainloop()