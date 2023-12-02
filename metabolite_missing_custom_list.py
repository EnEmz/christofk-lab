import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from pandastable import Table
import re

path_custom_list_neg = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\custom_list_neg.csv"
path_custom_list_pos = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\custom_list_pos.csv"

path_current_neg = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\current_zic_philic_ms1_rt_C13_neg.csv"
path_current_pos = "C:\\Users\\nmatulionis\\Desktop\\ms1_rt_database_lists\\current_zic_philic_ms1_rt_C13_pos.csv"

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
        
        self.df_met_neg = pd.read_csv(path_current_neg, index_col='index')
        self.df_met_pos = pd.read_csv(path_current_pos, index_col='index')
        
        self.df_met_total = pd.concat([self.df_met_neg, self.df_met_pos], ignore_index=True)
        self.met_list_total = self.df_met_total['name'].str.split(' M').str[0].unique().tolist()

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Metabolite Data Editor")
        self.root.geometry("1000x1200")
        listbox_font = ("Helvetica", 12)
        
        # Configure the main window's grid
        self.root.grid_rowconfigure(1, weight=1)  # Allocate extra space to the row with listboxes
        self.root.grid_columnconfigure(0, weight=1)  # Negative Data
        self.root.grid_columnconfigure(1, weight=0)  # Negative RT
        self.root.grid_columnconfigure(2, weight=1)  # Positive Data
        self.root.grid_columnconfigure(3, weight=0)  # Positive RT
        
        
        # File path entry and Load button frame
        file_path_frame = tk.Frame(self.root)
        file_path_frame.grid(row=0, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

        # Text entry for file path
        self.file_path_entry = tk.Entry(file_path_frame)
        self.file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Load button
        load_button = tk.Button(file_path_frame, text="Upload Analysis File", command=self.load_file)
        load_button.pack(side=tk.RIGHT, padx=5)

        # Path configuration frame
        self.path_display_frame = tk.LabelFrame(self.root, text="Current File Paths")
        self.path_display_frame.grid(row=4, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        self.path_display_frame.grid_columnconfigure(1, weight=1)

        self.display_path("Custom Met List Neg:", path_custom_list_neg, 0)
        self.display_path("Custom Met List Pos:", path_custom_list_pos, 1)
        self.display_path("Full Met List Neg:", path_current_neg, 2)
        self.display_path("Full Met List Pos:", path_current_pos, 3)

        # Edit paths button
        edit_paths_button = tk.Button(self.root, text="Edit Paths", command=self.edit_paths)
        edit_paths_button.grid(row=5, column=0, columnspan=1, sticky='ew', padx=5, pady=5)

        # Negative Data frame
        frame_neg = tk.Frame(root)
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
        self.frame_rt_neg = tk.Frame(self.root)
        self.frame_rt_neg.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        label_rt_neg = tk.Label(self.frame_rt_neg, text="Negative RT")
        label_rt_neg.pack(fill='x')
        self.listbox_rt_neg = tk.Listbox(self.frame_rt_neg, font=listbox_font)
        self.listbox_rt_neg.pack(fill="both", expand=True)
        
        # Positive Data frame
        frame_pos = tk.Frame(root)
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
        self.frame_rt_pos = tk.Frame(self.root)
        self.frame_rt_pos.grid(row=1, column=3, sticky='nsew', padx=5, pady=5)
        label_rt_pos = tk.Label(self.frame_rt_pos, text="Positive RT")
        label_rt_pos.pack(fill='x')
        self.listbox_rt_pos = tk.Listbox(self.frame_rt_pos, font=listbox_font)
        self.listbox_rt_pos.pack(fill="both", expand=True)
        
        # Initialize a Spinbox for M number input
        max_m_value = 10
        self.m_number_spinbox = CustomSpinbox(self.root, from_=0, to=max_m_value, write_to_terminal=self.write_to_terminal, initial_value=0)
        self.m_number_label = tk.Label(self.root, text="Enter M#:")
        self.m_number_label.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Add a label to display the text "Max M value:"
        self.max_m_label_text = tk.Label(self.root, text="Max M value:")
        self.max_m_label_text.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        # Add another label to display the actual max M value
        self.max_m_label = tk.Label(self.root, text="")
        self.max_m_label.grid(row=3, column=2, sticky='ew', padx=5, pady=5)

        # Save and quit buttons
        self.button_save = tk.Button(root, text="Save Data", command=self.save_data)
        self.button_save.grid(row=2, column=0, columnspan=1, sticky='ew', padx=5, pady=5)
        button_quit = tk.Button(root, text="Quit", command=root.destroy)
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
        
        # Add a terminal-like frame to the bottom
        self.terminal_frame = tk.Frame(self.root)
        self.terminal_frame.grid(row=6, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        self.terminal = tk.Text(self.terminal_frame, height=6, bg='black', fg='white')
        self.terminal.pack(fill='both', expand=True)
        
        
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
        
    def display_path(self, label, path, row):
        tk.Label(self.path_display_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=5)
        path_label = tk.Label(self.path_display_frame, text=path, anchor='center')
        path_label.grid(row=row, column=1, sticky='ew', padx=5)

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

        self.display_path("Custom Met List Neg:", path_custom_list_neg, 0)
        self.display_path("Custom Met List Pos:", path_custom_list_pos, 1)
        self.display_path("Full Met List Neg:", path_current_neg, 2)
        self.display_path("Full Met List Pos:", path_current_pos, 3)

        edit_window.destroy()
        
        
    def upload_path(self, label):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry = self.path_entries[label]
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
        
    
    def is_excel_file(self, filename):
        return filename.endswith('.xls') or filename.endswith('.xlsx')
    
    
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
        met_list_not_pool_set = set(self.met_list_total) - set(met_list_pool)
        met_list_not_pool = list(met_list_not_pool_set)

        if self.iso_present:
            met_list_iso = self.df_analysis_iso['Compound'].str.strip().unique().tolist()
            met_list_not_iso_set = set(self.met_list_total) - set(met_list_iso)
            met_list_not_iso = list(met_list_not_iso_set)
            
        combined_met_list_missing = list(set(met_list_not_pool + met_list_not_iso))

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