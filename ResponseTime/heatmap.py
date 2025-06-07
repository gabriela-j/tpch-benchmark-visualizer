import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from tkinter import messagebox
import os

class HeatmapApp(ctk.CTkFrame):
    """
    Tkinter Frame for visualizing TPC-H benchmark execution times as heatmaps.
    Supports user selection of dataset size, node count, and metric (Average/Total Time),
    with options for dynamic custom input.
    """

    def __init__(self, parent, go_back):
        """
        Initialize the HeatmapApp GUI. Build all dropdowns, buttons, and Matplotlib canvas.
        Args:
            parent: Parent widget (Tk root or another frame)
            go_back: Callback to return to the previous menu
        """
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.help_popup_window = None

        # --- Dynamic dropdown options (can be expanded with custom input) ---
        self.datasets = ["1GB", "10GB", "20GB", "+Add own"]
        self.nodes_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "15", "+Add own"]
        self.metric_options = ["Average Time", "Total Time"]

        # --- User selection variables
        self.dataset_var = ctk.StringVar(value=self.datasets[0])
        self.nodes_var = ctk.StringVar(value=self.nodes_options[0])
        self.metric_var = ctk.StringVar(value=self.metric_options[0])

        self.dataset_entry = None
        self.nodes_entry = None

        # --- Top: parameter selection dropdowns
        dropdown_frame = ctk.CTkFrame(self)
        dropdown_frame.pack(pady=10, padx=10)

        ctk.CTkLabel(dropdown_frame, text="Dataset Size:").grid(row=0, column=0, padx=12, pady=10)
        self.dataset_menu = ctk.CTkOptionMenu(
            dropdown_frame, variable=self.dataset_var, values=self.datasets, width=120, command=self.on_dataset_select
        )
        self.dataset_menu.grid(row=0, column=1, padx=8)

        ctk.CTkLabel(dropdown_frame, text="Nodes:").grid(row=0, column=2, padx=12, pady=10)
        self.nodes_menu = ctk.CTkOptionMenu(
            dropdown_frame, variable=self.nodes_var, values=self.nodes_options, width=80, command=self.on_nodes_select
        )
        self.nodes_menu.grid(row=0, column=3, padx=8)

        ctk.CTkLabel(dropdown_frame, text="Metric:").grid(row=0, column=4, padx=12, pady=10)
        self.metric_menu = ctk.CTkOptionMenu(
            dropdown_frame, variable=self.metric_var, values=self.metric_options, width=160
        )
        self.metric_menu.grid(row=0, column=5, padx=8)

        # --- Action buttons: Generate and Save
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Generate Heatmap", command=self.generate_heatmap, width=150).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Save Heatmap", command=self.save_heatmap, width=150, fg_color="#10B981", hover_color="#059669").pack(side="left", padx=10)

        # --- Matplotlib Figure setup
        self.fig = plt.Figure(figsize=(10, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.heatmap = None  # Store handle for current plot

        # Redraw heatmap if window resized
        self.bind("<Configure>", self.on_resize)

        # --- Bottom: Go Back and Help buttons
        bottom_btn_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_btn_row.pack(pady=10, side="bottom")

        ctk.CTkButton(
            bottom_btn_row, text="Go Back", command=self.go_back,
            fg_color="#6B7280", hover_color="#4B5563", width=160
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom_btn_row, text="Help", command=self.show_help_popup,
            fg_color="#F59E0B", hover_color="#D97706", width=160
        ).pack(side="left", padx=10)

    # --------------- Dynamic dropdowns for "+Add own" options ----------------

    def on_dataset_select(self, value):
        """
        If user selects '+Add own', show a text entry for custom dataset size.
        Otherwise, set the selected dataset and restore dropdown.
        """
        if value == "+Add own":
            if self.dataset_entry:
                self.dataset_entry.destroy()
                self.dataset_entry = None
            self.dataset_menu.grid_remove()
            self.dataset_entry = ctk.CTkEntry(self.dataset_menu.master, placeholder_text="Type size, e.g. 50GB")
            self.dataset_entry.grid(row=0, column=1, padx=8)
            self.dataset_entry.focus_set()
            self.dataset_entry.delete(0, "end")
            self.dataset_entry.bind("<Return>", self.add_custom_dataset)
            self.dataset_entry.bind("<FocusOut>", self.add_custom_dataset)
            self.dataset_var.set("")
        elif value != "":
            if self.dataset_entry:
                self.dataset_entry.destroy()
                self.dataset_entry = None
            self.dataset_var.set(value)
            self.dataset_menu.grid()  # Restore menu if user returns from entry

    def add_custom_dataset(self, event):
        """
        Add user-typed custom dataset size to the dropdown and select it.
        """
        if not self.dataset_entry:
            return
        value = self.dataset_entry.get().strip()
        if value and value not in self.datasets:
            self.datasets.insert(-1, value)
            self.dataset_menu.configure(values=self.datasets)
            self.dataset_var.set(value)
        elif value:
            self.dataset_var.set(value)
        self.dataset_entry.destroy()
        self.dataset_entry = None
        self.dataset_menu.grid()

    def on_nodes_select(self, value):
        """
        If user selects '+Add own', show a text entry for custom node count.
        Otherwise, set the selected node count and restore dropdown.
        """
        if value == "+Add own":
            if self.nodes_entry:
                self.nodes_entry.destroy()
                self.nodes_entry = None
            self.nodes_menu.grid_remove()
            self.nodes_entry = ctk.CTkEntry(self.nodes_menu.master, placeholder_text="Type nodes, e.g. 12")
            self.nodes_entry.grid(row=0, column=3, padx=8)
            self.nodes_entry.focus_set()
            self.nodes_entry.delete(0, "end")
            self.nodes_entry.bind("<Return>", self.add_custom_nodes)
            self.nodes_entry.bind("<FocusOut>", self.add_custom_nodes)
            self.nodes_var.set("")
        elif value != "":
            if self.nodes_entry:
                self.nodes_entry.destroy()
                self.nodes_entry = None
            self.nodes_var.set(value)
            self.nodes_menu.grid()

    def add_custom_nodes(self, event):
        """
        Add user-typed custom node count to the dropdown and select it.
        """
        if not self.nodes_entry:
            return
        value = self.nodes_entry.get().strip()
        if value and value not in self.nodes_options:
            self.nodes_options.insert(-1, value)
            self.nodes_menu.configure(values=self.nodes_options)
            self.nodes_var.set(value)
        elif value:
            self.nodes_var.set(value)
        self.nodes_entry.destroy()
        self.nodes_entry = None
        self.nodes_menu.grid()
    # -------------------------------------------------------------------------

    def on_resize(self, event):
        """
        Redraw the heatmap when the window size changes.
        """
        if self.canvas and self.heatmap:
            self.canvas.draw()

    def generate_heatmap(self):
        """
        Generate a heatmap of query response times for the selected dataset size,
        node count, and metric (Average/Total). Plots HDFS and MinIO as rows,
        and queries as columns.
        """
        # Remove old plot and recreate Figure/canvas
        self.canvas.get_tk_widget().pack_forget()
        plt.close(self.fig)
        self.fig = plt.Figure(figsize=(10, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Fetch user selections
        dataset_size = self.dataset_var.get()
        nodes = self.nodes_var.get()
        metric = self.metric_var.get()

        # Excel file: .benchmark_data/DATASET/tpc_h-DATASET-W-NODES-node(s).xlsx
        base_path = os.path.join(os.path.dirname(__file__), ".benchmark_data")
        dataset_folder = dataset_size.replace("GB", "Gb")
        excel_file = os.path.join(base_path, dataset_folder, f"tpc_h-{dataset_folder}-W-{nodes}-node(s).xlsx")

        if not os.path.exists(excel_file):
            messagebox.showerror("Error", f"File not found:\n{excel_file}\n\nTry another node count (available only for those with data).")
            return

        try:
            data = pd.read_excel(excel_file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data:\n{e}")
            return

        # Column names depend on selected metric
        if metric == "Average Time":
            hdfs_col = "HDFS_Average"
            minio_col = "MINIO_Average"
        else:
            hdfs_col = "HDFS_Total"
            minio_col = "MINIO_Total"

        queries = range(1, 23)
        servers = ['HDFS', 'MINIO']

        try:
            hdfs_data = data[hdfs_col].values[:22]
            minio_data = data[minio_col].values[:22]
        except Exception as e:
            messagebox.showerror("Error", f"Column error:\n{e}")
            return

        # Prepare 2D array: servers (rows) x queries (columns)
        heatmap_data = np.array([hdfs_data, minio_data])

        # Draw heatmap
        self.heatmap = self.ax.imshow(heatmap_data, cmap='YlOrRd', interpolation='nearest', aspect='auto')
        self.fig.colorbar(self.heatmap, ax=self.ax, label='Response Time (s)')
        self.ax.set_xticks(range(len(queries)))
        self.ax.set_xticklabels(queries, rotation=45)
        self.ax.set_yticks(range(len(servers)))
        self.ax.set_yticklabels(servers)
        self.ax.set_title(f'{metric} Heatmap ({dataset_size}, {nodes} node(s))')
        self.ax.set_xlabel('Query Number')
        self.ax.set_ylabel('Server Type')
        self.fig.tight_layout()
        self.canvas.draw()

    def save_heatmap(self):
        """
        Save the current heatmap as a PNG file in .generated_files/heatmap_files.
        """
        if self.heatmap is None:
            messagebox.showerror("Error", "Generate a heatmap first!")
            return

        metric = self.metric_var.get().replace(" ", "_").lower()
        size = self.dataset_var.get()
        nodes = self.nodes_var.get()
        filename = f"heatmap_{metric}_{size}_{nodes}nodes.png"
        output_dir = os.path.join(os.path.dirname(__file__), ".generated_files", "heatmap_files")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        try:
            self.fig.savefig(filepath)
            messagebox.showinfo("Success", f"Heatmap saved as:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save heatmap:\n{e}")

    def show_help_popup(self):
        """
        Display a help popup window with detailed user instructions and FAQ.
        Only one help window can be open at a time.
        """
        if self.help_popup_window is not None and self.help_popup_window.winfo_exists():
            self.help_popup_window.lift()
            return

        self.help_popup_window = ctk.CTkToplevel(self)
        self.help_popup_window.title("Help")
        self.help_popup_window.geometry("650x400")
        self.help_popup_window.attributes("-topmost", True)

        def on_close():
            self.help_popup_window.destroy()
            self.help_popup_window = None

        self.help_popup_window.protocol("WM_DELETE_WINDOW", on_close)

        help_text = """User Guide — Heatmap Module (with Nodes & Custom Input)

        This module enables you to generate heatmaps that compare performance across different dataset sizes, node counts, and metrics using benchmark Excel data. You can also add your own \ncustom dataset size or node count for even more flexible analysis.

        How to use:

        1. **Choose the dataset size:**
        - Select from available options (e.g., 1GB, 10GB, 20GB), or select “+Add own” to enter a custom dataset size (such as 50GB).
        - When you select “+Add own”, a text field will appear. Type your desired dataset size and press Enter.

        2. **Choose the number of nodes:**
        - Select from available node counts (e.g., 1–10, 15), or select “+Add own” to enter your own number of nodes.
        - When you select “+Add own”, a text field will appear. Type the number of nodes and press Enter.

        3. **Choose the performance metric to analyze:**
        - Available metrics: Average Time and Total Time.

        4. **Click “Generate Heatmap”** to display the chart for the selected configuration.

        5. **Click “Save Heatmap”** to save the generated heatmap as a PNG file.

        6. You can click the “Help” button at any time to reopen this guide.
        - Use 'Go Back' to return to the main menu.

        Notes:
        - If you add a custom dataset size or node count, the program will look for a matching Excel file in the .benchmark_data folder.
        - The heatmap visualizes response times for 22 queries on two environments: HDFS (serverful) and MinIO (serverless).
        - Make sure the required Excel files are present and correctly named in the .benchmark_data subfolders.
        - If you select a dataset size/nodes combination with no file, you'll get a clear error message.

        Frequently Asked Questions:
        - **Q:** What does the heatmap represent?  
        **A:** It shows how query response times vary by dataset size, node count, and environment (HDFS/MinIO).
        - **Q:** How do I add a custom dataset size or node count?  
        **A:** Select “+Add own” in the dropdown, enter your value in the field that appears, and press Enter.
        - **Q:** What if the file is missing?  
        **A:** Try a different node count or dataset size with available data, or ensure the Excel file for your custom input is in the right folder.

        Module version: Heatmap with Nodes (Custom Input) v1.1.0
        """

        scroll_frame = ctk.CTkScrollableFrame(self.help_popup_window, width=680, height=460)
        scroll_frame.pack(padx=24, pady=16, fill="both", expand=True)

        help_label = ctk.CTkLabel(
            scroll_frame,
            text=help_text,
            justify="left",
            anchor="nw",
            wraplength=640
        )
        help_label.pack(anchor="nw", pady=5, expand=True, fill="both")

        # Responsiveness for help text
        def on_resize(event):
            w = scroll_frame.winfo_width() - 32
            if w > 200:
                help_label.configure(wraplength=w)
        self.help_popup_window.bind("<Configure>", on_resize)
