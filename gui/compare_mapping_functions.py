"""
Module for comparing two mapping table files (CSV or Excel)
Compares files with columns: Radarfile, Videofile
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


def compare_mapping_tables_dialog(root, append_info_text, set_window_icon):
    """
    Open dialog to select two mapping table files and compare them
    
    Args:
        root: Tkinter root window
        append_info_text: Function to append text to info console
        set_window_icon: Function to set window icon
    """
    # Create dialog window
    dialog = tk.Toplevel(root)
    set_window_icon(dialog)
    dialog.title("Compare Mapping Tables")
    dialog.geometry("750x300")
    dialog.resizable(False, False)
    
    # Center dialog
    dialog.transient(root)
    dialog.grab_set()
    
    # Header
    header_frame = tk.Frame(dialog, bg='#2196F3', pady=15)
    header_frame.pack(fill='x')
    tk.Label(header_frame, text="Compare Two Mapping Tables", 
             bg='#2196F3', fg='white', font=('Arial', 14, 'bold')).pack()
    
    # Main content
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    # File 1
    tk.Label(content_frame, text="File 1 (Original):", 
             font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))
    
    file1_frame = tk.Frame(content_frame)
    file1_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
    
    file1_var = tk.StringVar()
    file1_entry = tk.Entry(file1_frame, textvariable=file1_var, width=60, font=('Arial', 9))
    file1_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
    
    def browse_file1():
        file_path = filedialog.askopenfilename(
            title="Select First Mapping Table",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            file1_var.set(file_path)
    
    tk.Button(file1_frame, text="Browse", command=browse_file1, 
              width=10, bg='#4CAF50', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
    
    # File 2
    tk.Label(content_frame, text="File 2 (New):", 
             font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0, 5))
    
    file2_frame = tk.Frame(content_frame)
    file2_frame.grid(row=3, column=0, sticky='ew', pady=(0, 20))
    
    file2_var = tk.StringVar()
    file2_entry = tk.Entry(file2_frame, textvariable=file2_var, width=60, font=('Arial', 9))
    file2_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
    
    def browse_file2():
        file_path = filedialog.askopenfilename(
            title="Select Second Mapping Table",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            file2_var.set(file_path)
    
    tk.Button(file2_frame, text="Browse", command=browse_file2, 
              width=10, bg='#4CAF50', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
    
    content_frame.columnconfigure(0, weight=1)
    
    # Buttons
    button_frame = tk.Frame(dialog, pady=10)
    button_frame.pack()
    
    def do_compare():
        file1 = file1_var.get().strip()
        file2 = file2_var.get().strip()
        
        # Remove quotes if user wrapped path in quotes
        file1 = file1.strip('"').strip("'")
        file2 = file2.strip('"').strip("'")
        
        if not file1 or not file2:
            messagebox.showwarning("Warning", "Please select both files!")
            return
        
        if not os.path.isfile(file1):
            messagebox.showerror("Error", f"File 1 not found: {file1}")
            return
        
        if not os.path.isfile(file2):
            messagebox.showerror("Error", f"File 2 not found: {file2}")
            return
        
        dialog.destroy()
        perform_mapping_comparison(file1, file2, root, append_info_text, set_window_icon)
    
    tk.Button(button_frame, text="Compare", command=do_compare,
              bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
              width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Cancel", command=dialog.destroy,
              bg='#757575', fg='white', font=('Arial', 10),
              width=12, height=1).pack(side=tk.LEFT, padx=5)


def perform_mapping_comparison(file1_path, file2_path, root, append_info_text, set_window_icon):
    """
    Perform the actual comparison between two mapping tables
    
    Args:
        file1_path: Path to first file
        file2_path: Path to second file
        root: Tkinter root window
        append_info_text: Function to append text to info console
        set_window_icon: Function to set window icon
    """
    def worker():
        try:
            import pandas as pd
            
            root.after(0, lambda: append_info_text("[COMPARE] 📊 Starting mapping table comparison...\n"))
            root.after(0, lambda: append_info_text(f"[COMPARE] File 1: {os.path.basename(file1_path)}\n"))
            root.after(0, lambda: append_info_text(f"[COMPARE] File 2: {os.path.basename(file2_path)}\n"))
            
            # Read files
            root.after(0, lambda: append_info_text("[COMPARE] 📖 Reading File 1...\n"))
            if file1_path.lower().endswith('.csv'):
                df1 = pd.read_csv(file1_path, sep=';', encoding='utf-8')
            else:
                df1 = pd.read_excel(file1_path)
            
            root.after(0, lambda: append_info_text("[COMPARE] 📖 Reading File 2...\n"))
            if file2_path.lower().endswith('.csv'):
                df2 = pd.read_csv(file2_path, sep=';', encoding='utf-8')
            else:
                df2 = pd.read_excel(file2_path)
            
            # Validate columns
            expected_columns = ['Radarfile', 'Videofile']
            if list(df1.columns) != expected_columns:
                root.after(0, lambda: append_info_text(f"[COMPARE] ⚠️ File 1 columns: {list(df1.columns)}\n"))
                root.after(0, lambda: messagebox.showwarning("Warning", 
                    f"File 1 has unexpected columns: {list(df1.columns)}\nExpected: {expected_columns}"))
            
            if list(df2.columns) != expected_columns:
                root.after(0, lambda: append_info_text(f"[COMPARE] ⚠️ File 2 columns: {list(df2.columns)}\n"))
                root.after(0, lambda: messagebox.showwarning("Warning", 
                    f"File 2 has unexpected columns: {list(df2.columns)}\nExpected: {expected_columns}"))
            
            # Clean data
            df1 = df1.fillna('')
            df2 = df2.fillna('')
            df1 = df1.astype(str)
            df2 = df2.astype(str)
            
            # Strip whitespace
            for col in df1.columns:
                df1[col] = df1[col].str.strip()
            for col in df2.columns:
                df2[col] = df2[col].str.strip()
            
            root.after(0, lambda: append_info_text(f"[COMPARE] File 1: {len(df1)} rows\n"))
            root.after(0, lambda: append_info_text(f"[COMPARE] File 2: {len(df2)} rows\n"))
            
            # Sort both dataframes by Radarfile for comparison
            df1_sorted = df1.sort_values('Radarfile').reset_index(drop=True)
            df2_sorted = df2.sort_values('Radarfile').reset_index(drop=True)
            
            # Create sets for comparison (as tuples)
            set1 = set(df1.apply(tuple, axis=1))
            set2 = set(df2.apply(tuple, axis=1))
            
            # Find differences
            only_in_file1 = set1 - set2  # Rows removed in file2
            only_in_file2 = set2 - set1  # Rows added in file2
            common = set1 & set2  # Same rows in both
            
            # Convert back to dataframes
            removed_rows = pd.DataFrame(list(only_in_file1), columns=df1.columns) if only_in_file1 else pd.DataFrame(columns=df1.columns)
            added_rows = pd.DataFrame(list(only_in_file2), columns=df2.columns) if only_in_file2 else pd.DataFrame(columns=df2.columns)
            
            # Find modified rows (same Radarfile but different Videofile)
            df1_dict = dict(zip(df1['Radarfile'], df1['Videofile']))
            df2_dict = dict(zip(df2['Radarfile'], df2['Videofile']))
            
            modified_rows = []
            for radar in df1_dict.keys():
                if radar in df2_dict and df1_dict[radar] != df2_dict[radar]:
                    modified_rows.append({
                        'Radarfile': radar,
                        'Videofile_Old': df1_dict[radar],
                        'Videofile_New': df2_dict[radar]
                    })
            
            modified_df = pd.DataFrame(modified_rows)
            
            root.after(0, lambda: append_info_text(f"[COMPARE] ✅ Analysis complete!\n"))
            root.after(0, lambda: append_info_text(f"[COMPARE] 📊 Common rows: {len(common)}\n"))
            root.after(0, lambda: append_info_text(f"[COMPARE] ➖ Removed rows: {len(removed_rows)}\n"))
            root.after(0, lambda: append_info_text(f"[COMPARE] ➕ Added rows: {len(added_rows)}\n"))
            root.after(0, lambda: append_info_text(f"[COMPARE] 🔄 Modified rows: {len(modified_df)}\n"))
            
            # Show results
            results = {
                'file1_name': os.path.basename(file1_path),
                'file2_name': os.path.basename(file2_path),
                'total_file1': len(df1),
                'total_file2': len(df2),
                'common': len(common),
                'removed': removed_rows,
                'added': added_rows,
                'modified': modified_df,
                'df1_sorted': df1_sorted,
                'df2_sorted': df2_sorted
            }
            
            root.after(0, lambda: show_comparison_results(results, root, set_window_icon))
            
        except Exception as e:
            import traceback
            error_msg = f"[COMPARE] ❌ Error: {str(e)}\n{traceback.format_exc()}"
            root.after(0, lambda: append_info_text(error_msg))
            root.after(0, lambda: messagebox.showerror("Error", f"Comparison failed: {str(e)}"))
    
    threading.Thread(target=worker, daemon=True).start()


def show_comparison_results(results, root, set_window_icon):
    """
    Show comparison results in a new window with tabs
    
    Args:
        results: Dictionary containing comparison results
        root: Tkinter root window
        set_window_icon: Function to set window icon
    """
    # Create results window
    result_window = tk.Toplevel(root)
    set_window_icon(result_window)
    result_window.title("Mapping Tables Comparison Results")
    result_window.geometry("1000x700")
    
    # Header
    header_frame = tk.Frame(result_window, bg='#2196F3', pady=10)
    header_frame.pack(fill='x')
    
    title_text = f"Comparison: {results['file1_name']} vs {results['file2_name']}"
    tk.Label(header_frame, text=title_text, 
             bg='#2196F3', fg='white', font=('Arial', 12, 'bold')).pack()
    
    # Create notebook for tabs
    notebook = ttk.Notebook(result_window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Tab 1: Summary
    summary_frame = create_summary_tab(notebook, results)
    notebook.add(summary_frame, text="📊 Summary")
    
    # Tab 2: Modified Rows
    if len(results['modified']) > 0:
        modified_frame = create_modified_tab(notebook, results['modified'])
        notebook.add(modified_frame, text=f"🔄 Modified ({len(results['modified'])})")
    
    # Tab 3: Removed Rows
    if len(results['removed']) > 0:
        removed_frame = create_removed_tab(notebook, results['removed'])
        notebook.add(removed_frame, text=f"➖ Removed ({len(results['removed'])})")
    
    # Tab 4: Added Rows
    if len(results['added']) > 0:
        added_frame = create_added_tab(notebook, results['added'])
        notebook.add(added_frame, text=f"➕ Added ({len(results['added'])})")
    
    # Tab 5: Full File 1
    file1_frame = create_file_view_tab(notebook, results['df1_sorted'], f"File 1: {results['file1_name']}")
    notebook.add(file1_frame, text=f"📄 File 1 ({results['total_file1']})")
    
    # Tab 6: Full File 2
    file2_frame = create_file_view_tab(notebook, results['df2_sorted'], f"File 2: {results['file2_name']}")
    notebook.add(file2_frame, text=f"📄 File 2 ({results['total_file2']})")
    
    # Bottom buttons frame
    button_frame = tk.Frame(result_window, pady=10)
    button_frame.pack()
    
    def export_results():
        """Export comparison results to Excel file"""
        try:
            from tkinter import filedialog
            import pandas as pd
            from datetime import datetime
            
            # Ask user for save location
            default_name = f"comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                title="Save Comparison Results",
                defaultextension=".xlsx",
                initialfile=default_name,
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Write summary
                summary_data = {
                    'Metric': ['File 1', 'File 2', 'Total Rows File 1', 'Total Rows File 2', 
                               'Common Rows', 'Removed Rows', 'Added Rows', 'Modified Rows'],
                    'Value': [results['file1_name'], results['file2_name'], 
                             results['total_file1'], results['total_file2'],
                             results['common'], len(results['removed']), 
                             len(results['added']), len(results['modified'])]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Write modified rows
                if len(results['modified']) > 0:
                    results['modified'].to_excel(writer, sheet_name='Modified', index=False)
                
                # Write removed rows
                if len(results['removed']) > 0:
                    results['removed'].to_excel(writer, sheet_name='Removed', index=False)
                
                # Write added rows
                if len(results['added']) > 0:
                    results['added'].to_excel(writer, sheet_name='Added', index=False)
                
                # Write full files
                results['df1_sorted'].to_excel(writer, sheet_name='File1_Full', index=False)
                results['df2_sorted'].to_excel(writer, sheet_name='File2_Full', index=False)
            
            messagebox.showinfo("Success", f"Results exported successfully to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    tk.Button(button_frame, text="💾 Export to Excel", command=export_results,
              width=18, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Close", command=result_window.destroy, 
              width=15, bg='#757575', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)


def create_summary_tab(parent, results):
    """Create summary tab with statistics"""
    frame = tk.Frame(parent)
    
    # Create text widget with scrollbar
    text_frame = tk.Frame(frame)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10),
                          yscrollcommand=scrollbar.set)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)
    
    # Build summary text
    summary = f"""
╔═══════════════════════════════════════════════════════════════════╗
                    MAPPING TABLES COMPARISON SUMMARY
╚═══════════════════════════════════════════════════════════════════╝

FILE INFORMATION:
{'─'*70}
📄 File 1 (Original): {results['file1_name']}
   Total rows: {results['total_file1']}

📄 File 2 (New): {results['file2_name']}
   Total rows: {results['total_file2']}

COMPARISON RESULTS:
{'─'*70}
✅ Common rows (unchanged):     {results['common']}
🔄 Modified rows:                {len(results['modified'])}
➖ Removed rows (only in File 1): {len(results['removed'])}
➕ Added rows (only in File 2):   {len(results['added'])}

ANALYSIS:
{'─'*70}
"""
    
    if len(results['modified']) > 0:
        summary += f"\n🔄 MODIFIED ROWS ({len(results['modified'])} changes):\n"
        summary += "   These rows exist in both files but have different Videofile values.\n"
        for idx, row in results['modified'].head(10).iterrows():
            summary += f"\n   • Radarfile: {row['Radarfile']}\n"
            summary += f"     Old: {row['Videofile_Old']}\n"
            summary += f"     New: {row['Videofile_New']}\n"
        if len(results['modified']) > 10:
            summary += f"\n   ... and {len(results['modified']) - 10} more modified rows\n"
    
    if len(results['removed']) > 0:
        summary += f"\n➖ REMOVED ROWS ({len(results['removed'])} rows):\n"
        summary += "   These rows exist in File 1 but not in File 2.\n"
        for idx, row in results['removed'].head(10).iterrows():
            summary += f"   • {row['Radarfile']} → {row['Videofile']}\n"
        if len(results['removed']) > 10:
            summary += f"   ... and {len(results['removed']) - 10} more removed rows\n"
    
    if len(results['added']) > 0:
        summary += f"\n➕ ADDED ROWS ({len(results['added'])} rows):\n"
        summary += "   These rows exist in File 2 but not in File 1.\n"
        for idx, row in results['added'].head(10).iterrows():
            summary += f"   • {row['Radarfile']} → {row['Videofile']}\n"
        if len(results['added']) > 10:
            summary += f"   ... and {len(results['added']) - 10} more added rows\n"
    
    if results['common'] == results['total_file1'] == results['total_file2']:
        summary += "\n✅ PERFECT MATCH! Both files are identical.\n"
    
    summary += f"\n{'═'*70}\n"
    
    text_widget.insert(tk.END, summary)
    text_widget.config(state=tk.DISABLED)
    
    return frame


def create_modified_tab(parent, modified_df):
    """Create tab showing modified rows"""
    frame = tk.Frame(parent)
    
    # Create treeview with scrollbars
    tree_frame = tk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Scrollbars
    vsb = tk.Scrollbar(tree_frame, orient="vertical")
    hsb = tk.Scrollbar(tree_frame, orient="horizontal")
    
    # Treeview
    tree = ttk.Treeview(tree_frame, columns=('Radarfile', 'Old Value', 'New Value'),
                        show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Configure columns
    tree.heading('Radarfile', text='Radarfile')
    tree.heading('Old Value', text='Old Videofile (File 1)')
    tree.heading('New Value', text='New Videofile (File 2)')
    
    tree.column('Radarfile', width=300)
    tree.column('Old Value', width=300)
    tree.column('New Value', width=300)
    
    # Insert data
    for idx, row in modified_df.iterrows():
        tree.insert('', tk.END, values=(row['Radarfile'], row['Videofile_Old'], row['Videofile_New']))
    
    return frame


def create_removed_tab(parent, removed_df):
    """Create tab showing removed rows"""
    frame = tk.Frame(parent)
    
    # Create treeview with scrollbars
    tree_frame = tk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Scrollbars
    vsb = tk.Scrollbar(tree_frame, orient="vertical")
    hsb = tk.Scrollbar(tree_frame, orient="horizontal")
    
    # Treeview
    tree = ttk.Treeview(tree_frame, columns=('Radarfile', 'Videofile'),
                        show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Configure columns
    tree.heading('Radarfile', text='Radarfile')
    tree.heading('Videofile', text='Videofile')
    
    tree.column('Radarfile', width=400)
    tree.column('Videofile', width=400)
    
    # Insert data
    for idx, row in removed_df.iterrows():
        tree.insert('', tk.END, values=(row['Radarfile'], row['Videofile']))
    
    return frame


def create_added_tab(parent, added_df):
    """Create tab showing added rows"""
    frame = tk.Frame(parent)
    
    # Create treeview with scrollbars
    tree_frame = tk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Scrollbars
    vsb = tk.Scrollbar(tree_frame, orient="vertical")
    hsb = tk.Scrollbar(tree_frame, orient="horizontal")
    
    # Treeview
    tree = ttk.Treeview(tree_frame, columns=('Radarfile', 'Videofile'),
                        show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Configure columns
    tree.heading('Radarfile', text='Radarfile')
    tree.heading('Videofile', text='Videofile')
    
    tree.column('Radarfile', width=400)
    tree.column('Videofile', width=400)
    
    # Insert data
    for idx, row in added_df.iterrows():
        tree.insert('', tk.END, values=(row['Radarfile'], row['Videofile']))
    
    return frame


def create_file_view_tab(parent, df, title):
    """Create tab showing full file content"""
    frame = tk.Frame(parent)
    
    # Create treeview with scrollbars
    tree_frame = tk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Scrollbars
    vsb = tk.Scrollbar(tree_frame, orient="vertical")
    hsb = tk.Scrollbar(tree_frame, orient="horizontal")
    
    # Treeview
    tree = ttk.Treeview(tree_frame, columns=('Radarfile', 'Videofile'),
                        show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Configure columns
    tree.heading('Radarfile', text='Radarfile')
    tree.heading('Videofile', text='Videofile')
    
    tree.column('Radarfile', width=400)
    tree.column('Videofile', width=400)
    
    # Insert data
    for idx, row in df.iterrows():
        tree.insert('', tk.END, values=(row['Radarfile'], row['Videofile']))
    
    return frame
