import customtkinter as ctk
import pandas as pd
import plotly.express as px
import numpy as np
import os
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_column_case_insensitive(df, target_name):
    """
    Find a DataFrame column by name, ignoring case.
    Useful if Excel columns may have different capitalization.
    """
    target_name_lower = target_name.lower()
    for col in df.columns:
        if col.lower() == target_name_lower:
            return col
    return None

class BoxplotApp(ctk.CTkFrame):
    """
    Tkinter Frame for visualizing TPC-H benchmark execution times
    as boxplots, with support for repeated runs and two chart modes.
    """

    def __init__(self, parent, go_back):
        """
        Build the Boxplot GUI, including dynamic selectors and action buttons.
        Args:
            parent: Parent Tkinter widget.
            go_back: Callback to return to the previous menu.
        """
        super().__init__(parent)
        self.go_back = go_back
        self.last_boxplot_path = None
        self.help_popup_window = None

        # --- GUI options ---
        self.datasets = ["1GB", "10GB", "20GB", "+Add own"]
        self.nodes_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "15", "+Add own"]
        time_types = ["Average Time", "Total Time"]

        self.dataset_var = ctk.StringVar(value=self.datasets[0])
        self.nodes_var = ctk.StringVar(value=self.nodes_options[0])
        self.time_type_var = ctk.StringVar(value=time_types[0])
        self.mode_var = ctk.StringVar(value="by_repeats")  # Chart mode selector
        self.query_var = ctk.StringVar(value="Query 1")

        self.dataset_entry = None
        self.nodes_entry = None

        # --- Layout setup ---
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Dataset/Nodes/Time selectors row ---
        selection_row_frame = ctk.CTkFrame(frame, fg_color="transparent")
        selection_row_frame.pack(pady=(10, 5))

        # Dataset selector (+ custom)
        dataset_frame = ctk.CTkFrame(selection_row_frame, fg_color="transparent")
        dataset_frame.pack(side="left", padx=10)
        ctk.CTkLabel(dataset_frame, text="Dataset Size:", font=ctk.CTkFont(size=14)).pack()
        self.dataset_optionmenu = ctk.CTkOptionMenu(
            dataset_frame, variable=self.dataset_var, values=self.datasets, command=self.on_dataset_select
        )
        self.dataset_optionmenu.pack()

        # Nodes selector (+ custom)
        nodes_frame = ctk.CTkFrame(selection_row_frame, fg_color="transparent")
        nodes_frame.pack(side="left", padx=10)
        ctk.CTkLabel(nodes_frame, text="Number of Nodes:", font=ctk.CTkFont(size=14)).pack()
        self.nodes_optionmenu = ctk.CTkOptionMenu(
            nodes_frame, variable=self.nodes_var, values=self.nodes_options, command=self.on_nodes_select
        )
        self.nodes_optionmenu.pack()

        # Time type selector
        time_frame = ctk.CTkFrame(selection_row_frame, fg_color="transparent")
        time_frame.pack(side="left", padx=10)
        ctk.CTkLabel(time_frame, text="Time Type:", font=ctk.CTkFont(size=14)).pack()
        ctk.CTkOptionMenu(time_frame, variable=self.time_type_var, values=time_types).pack()

        # --- Chart mode selection: by repeats or by queries ---
        mode_frame = ctk.CTkFrame(frame, fg_color="transparent")
        mode_frame.pack(pady=10)
        ctk.CTkLabel(mode_frame, text="Chart Mode:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=2)
        ctk.CTkRadioButton(
            mode_frame, text="Distribution of repetitions for the query", variable=self.mode_var, value="by_repeats", command=self.update_query_visibility
        ).pack(anchor="w", padx=10, pady=(0,2))
        ctk.CTkRadioButton(
            mode_frame, text="Distribution of times for all queries", variable=self.mode_var, value="by_queries", command=self.update_query_visibility
        ).pack(anchor="w", padx=10)

        # Query dropdown (only for 'by_repeats' mode)
        self.query_frame = ctk.CTkFrame(frame, fg_color="transparent")
        queries = [f"Query {i}" for i in range(1, 23)] + ["Total"]
        self.query_menu = ctk.CTkOptionMenu(self.query_frame, variable=self.query_var, values=queries)
        self.query_menu.pack(side="left")
        # --- Action buttons: generate/show plot ---
        self.button_row_frame = ctk.CTkFrame(frame, fg_color="transparent")  # <- NA self.
        self.button_row_frame.pack(pady=15)
        ctk.CTkButton(
            self.button_row_frame, text="Generate Boxplot",
            command=self.on_generate_button_click,
            fg_color="#3B82F6", hover_color="#2563EB", width=160
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            self.button_row_frame, text="Show Generated Boxplot",
            command=self.open_last_boxplot,
            fg_color="#10B981", hover_color="#059669", width=160
        ).pack(side="left", padx=10)

        # --- Status label for feedback/errors ---
        self.status_label = ctk.CTkLabel(frame, text="", wraplength=500, justify="center")
        self.status_label.pack(pady=10)

        # --- Bottom nav: Go Back / Help ---
        self.bottom_btn_row = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_btn_row.pack(pady=10, side="bottom")
        ctk.CTkButton(
            self.bottom_btn_row, text="Go Back", command=self.go_back,
            fg_color="#6B7280", hover_color="#4B5563", width=150
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            self.bottom_btn_row, text="Help", command=self.show_help_popup,
            fg_color="#F59E0B", hover_color="#D97706", width=150
        ).pack(side="left", padx=10)

        self.update_query_visibility()

    # ---------- Dynamic selectors for custom values ----------
    def on_dataset_select(self, value):
        """
        Show a text entry for custom dataset size if '+Add own' is chosen,
        or set selection to a predefined value.
        """
        if value == "+Add own":
            if self.dataset_entry:
                self.dataset_entry.destroy()
                self.dataset_entry = None
            self.dataset_optionmenu.pack_forget()
            self.dataset_entry = ctk.CTkEntry(self.dataset_optionmenu.master, placeholder_text="Type size, e.g. 50GB")
            self.dataset_entry.pack()
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

    def add_custom_dataset(self, event):
        """
        Add a user-typed custom dataset size to the dropdown and select it.
        """
        if not self.dataset_entry:
            return
        value = self.dataset_entry.get().strip()
        if value and value not in self.datasets:
            self.datasets.insert(-1, value)
            self.dataset_optionmenu.configure(values=self.datasets)
            self.dataset_var.set(value)
        elif value:
            self.dataset_var.set(value)
        self.dataset_entry.destroy()
        self.dataset_entry = None
        self.dataset_optionmenu.pack()

    def on_nodes_select(self, value):
        """
        Show a text entry for custom node count if '+Add own' is chosen,
        or set selection to a predefined value.
        """
        if value == "+Add own":
            if self.nodes_entry:
                self.nodes_entry.destroy()
                self.nodes_entry = None
            self.nodes_optionmenu.pack_forget()
            self.nodes_entry = ctk.CTkEntry(self.nodes_optionmenu.master, placeholder_text="Type nodes, e.g. 12")
            self.nodes_entry.pack()
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

    def add_custom_nodes(self, event):
        """
        Add a user-typed custom node count to the dropdown and select it.
        """
        if not self.nodes_entry:
            return
        value = self.nodes_entry.get().strip()
        if value and value not in self.nodes_options:
            self.nodes_options.insert(-1, value)
            self.nodes_optionmenu.configure(values=self.nodes_options)
            self.nodes_var.set(value)
        elif value:
            self.nodes_var.set(value)
        self.nodes_entry.destroy()
        self.nodes_entry = None
        self.nodes_optionmenu.pack()

    # ---------- End of dynamic selectors ----------

    def update_query_visibility(self):
        """
        Show/hide the query dropdown depending on the selected chart mode.
        Only show it for 'by_repeats' mode.
        """
        if self.mode_var.get() == "by_repeats":
            self.query_frame.pack(pady=4, before=self.button_row_frame)
        else:
            self.query_frame.pack_forget()

    def on_generate_button_click(self):
        """
        Handler for 'Generate Boxplot' button. Loads data, checks user selection,
        and calls the appropriate plotting method for selected mode.
        """
        dataset = self.dataset_var.get()
        nodes = self.nodes_var.get()
        time_type = self.time_type_var.get()
        mode = self.mode_var.get()

        if not dataset or not nodes or not time_type:
            self.status_label.configure(text="Fill all necessary fields!", text_color="orange")
            return

        # Dynamic folder mapping for custom datasets/nodes
        dataset_folder = dataset.replace("GB", "Gb")
        excel_file = os.path.join(BASE_DIR, ".benchmark_data", dataset_folder, f"tpc_h-{dataset_folder}-W-{nodes}-node(s).xlsx")
        if not os.path.exists(excel_file):
            self.status_label.configure(text=f"File does not exist:\n{excel_file}", text_color="red")
            return

        try:
            data = pd.read_excel(excel_file)
        except Exception as e:
            self.status_label.configure(text=f"Error loading file:\n{e}", text_color="red")
            return

        if mode == "by_repeats":
            selected_query = self.query_var.get()
            self.generate_boxplot_repeats(data, dataset, nodes, time_type, selected_query)
        else:
            self.generate_boxplot_queries(data, dataset, nodes, time_type)

    def generate_boxplot_repeats(self, data, dataset, nodes, time_type, selected_query):
        """
        Chart mode: Distribution of all repeated executions for a single query.
        Requires columns HDFS_SetX and MINIO_SetX.
        """
        hdfs_cols = [col for col in data.columns if col.lower().startswith("hdfs_set")]
        minio_cols = [col for col in data.columns if col.lower().startswith("minio_set")]
        if not hdfs_cols or not minio_cols:
            self.status_label.configure(
                text="File does not have repetitions (no HDFS_Set... or MINIO_Set... columns).\nChoose other mode or file.",
                text_color="red"
            )
            return

        if selected_query == "Total":
            query_idx = len(data) - 1
            query_label = "Total"
        else:
            query_idx = int(selected_query.split()[-1]) - 1
            query_label = selected_query

        if query_idx < 0 or query_idx >= len(data):
            self.status_label.configure(text=f"Wrong query number: {selected_query}", text_color="red")
            return

        row = data.iloc[query_idx]
        hdfs_times = row[hdfs_cols].values.astype(float)
        minio_times = row[minio_cols].values.astype(float)

        if not hdfs_times.size or not minio_times.size:
            self.status_label.configure(
                text="Lack of repetitions to show for chosen query.",
                text_color="red"
            )
            return

        boxplot_data = pd.DataFrame({
            "Environment": ["Serverful (HDFS)"] * len(hdfs_times) + ["Serverless (MinIO)"] * len(minio_times),
            "Response Time (s)": list(hdfs_times) + list(minio_times)
        })

        title = f"Time distribution for {query_label} ({dataset}, {nodes} nodes)"
        self.plot_and_save_boxplot(boxplot_data, dataset, nodes, title, f"query_{query_label.replace(' ', '').lower()}")

    def generate_boxplot_queries(self, data, dataset, nodes, time_type):
        """
        Chart mode: Distribution of times for all queries (one execution per query).
        Uses summary columns for HDFS/MinIO (Average or Total, case-insensitive).
        """
        if time_type == "Average Time":
            hdfs_col = find_column_case_insensitive(data, "hdfs_average")
            minio_col = find_column_case_insensitive(data, "minio_average")
            title_prefix = "Average"
        else:
            hdfs_col = find_column_case_insensitive(data, "hdfs_total")
            minio_col = find_column_case_insensitive(data, "minio_total")
            title_prefix = "Total"

        if not hdfs_col or not minio_col:
            self.status_label.configure(
                text=f"File does not have required columns (e.g. HDFS_Average / MinIO_Average):\n{data.columns.tolist()}",
                text_color="red"
            )
            return

        # Only first 22 rows are queries, last row often is 'Total'
        hdfs_times = data[hdfs_col].values[:22].astype(float)
        minio_times = data[minio_col].values[:22].astype(float)

        if not hdfs_times.size or not minio_times.size:
            self.status_label.configure(
                text="No data to show for chosen mode.",
                text_color="red"
            )
            return

        boxplot_data = pd.DataFrame({
            "Environment": ["Serverful (HDFS)"] * len(hdfs_times) + ["Serverless (MinIO)"] * len(minio_times),
            "Response Time (s)": list(hdfs_times) + list(minio_times)
        })

        title = f"Distribution of response time for all queries ({dataset}, {nodes} nodes)"
        self.plot_and_save_boxplot(boxplot_data, dataset, nodes, title, "all_queries")

    def plot_and_save_boxplot(self, boxplot_data, dataset, nodes, title, label_part):
        """
        Core method for plotting a boxplot using Plotly and saving as PNG.
        Adds summary stats for each environment as annotation.
        """
        output_dir = os.path.join(BASE_DIR, ".generated_files", "boxplot_files")
        os.makedirs(output_dir, exist_ok=True)
        boxplot_path = os.path.join(
            output_dir, f"boxplot_{label_part}_{dataset.lower()}_{nodes}nodes.png"
        )

        # Calculate key statistics for annotation
        hdfs_times = boxplot_data[boxplot_data["Environment"] == "Serverful (HDFS)"]["Response Time (s)"].values
        minio_times = boxplot_data[boxplot_data["Environment"] == "Serverless (MinIO)"]["Response Time (s)"].values
        hdfs_stats = {
            "median": np.median(hdfs_times),
            "q1": np.percentile(hdfs_times, 25),
            "q3": np.percentile(hdfs_times, 75),
            "min": np.min(hdfs_times),
            "max": np.max(hdfs_times),
            "iqr": np.percentile(hdfs_times, 75) - np.percentile(hdfs_times, 25)
        }
        minio_stats = {
            "median": np.median(minio_times),
            "q1": np.percentile(minio_times, 25),
            "q3": np.percentile(minio_times, 75),
            "min": np.min(minio_times),
            "max": np.max(minio_times),
            "iqr": np.percentile(minio_times, 75) - np.percentile(minio_times, 25)
        }

        stats_text = (
            "HDFS Stats:<br>"
            f"Median: {hdfs_stats['median']:.2f} s<br>"
            f"Lower Quartile: {hdfs_stats['q1']:.2f} s<br>"
            f"Upper Quartile: {hdfs_stats['q3']:.2f} s<br>"
            f"Interquartile Range: {hdfs_stats['iqr']:.2f} s<br>"
            f"Min: {hdfs_stats['min']:.2f} s<br>"
            f"Max: {hdfs_stats['max']:.2f} s<br><br>"
            "MinIO Stats:<br>"
            f"Median: {minio_stats['median']:.2f} s<br>"
            f"Lower Quartile: {minio_stats['q1']:.2f} s<br>"
            f"Upper Quartile: {minio_stats['q3']:.2f} s<br>"
            f"Interquartile Range: {minio_stats['iqr']:.2f} s<br>"
            f"Min: {minio_stats['min']:.2f} s<br>"
            f"Max: {minio_stats['max']:.2f} s"
        )

        fig_box = px.box(
            boxplot_data,
            x="Environment",
            y="Response Time (s)",
            color="Environment",
            title=title,
            color_discrete_map={"Serverful (HDFS)": "#00C853", "Serverless (MinIO)": "#0288D1"}
        )
        fig_box.update_layout(
            yaxis_title="Response Time (seconds)",
            xaxis_title="Environment",
            showlegend=True,
            legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top", title=None),
            margin=dict(r=250)
        )
        # Add summary stats to the chart as an annotation
        fig_box.add_annotation(
            text=stats_text,
            x=1.02,
            y=0.8,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="left",
            xanchor="left",
            yanchor="top",
            font=dict(size=10),
            bgcolor="white"
        )

        try:
            fig_box.write_image(boxplot_path)
            self.last_boxplot_path = boxplot_path
            self.status_label.configure(text=f"Boxplot saved as:\n{os.path.abspath(boxplot_path)}", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Error saving boxplot:\n{e}", text_color="red")

    def open_last_boxplot(self):
        """
        Opens the most recently generated boxplot PNG in the default system viewer.
        """
        if self.last_boxplot_path and os.path.exists(self.last_boxplot_path):
            webbrowser.open(f'file://{os.path.abspath(self.last_boxplot_path)}')
        else:
            self.status_label.configure(text="No boxplot to show yet.", text_color="orange")

    def show_help_popup(self):
        """
        Display a help popup window with user instructions and FAQ.
        Only one help window can be open at a time.
        """
        if self.help_popup_window is not None and self.help_popup_window.winfo_exists():
            self.help_popup_window.lift()
            return
        self.help_popup_window = ctk.CTkToplevel(self)
        self.help_popup_window.title("Help / Instructions")
        self.help_popup_window.geometry("540x470")
        self.help_popup_window.attributes("-topmost", True)

        def on_close():
            self.help_popup_window.destroy()
            self.help_popup_window = None
        self.help_popup_window.protocol("WM_DELETE_WINDOW", on_close)

        help_text = """User Guide — Boxplot Module (supports queries, repetitions & custom input)

        This application enables you to generate statistical boxplots from TPC-H benchmark Excel files, providing insights into the distribution of response times for different queries, \nenvironments (HDFS vs. MinIO), dataset sizes, and node counts. You can also enter your own custom dataset size or node count for more flexible analysis.

        How to use:

        1. **Select the dataset size** you want to analyze:
        - Choose from the available options (e.g., 1GB, 10GB, 20GB), or select “+Add own” to enter a custom dataset size (e.g., 50GB).
        - After selecting “+Add own”, a text field will appear. Enter your desired dataset size and press Enter.

        2. **Choose the number of nodes** used in the benchmark:
        - Pick from the available options (1, 2, ..., 10, 15), or select “+Add own” to enter a custom node count.
        - After selecting “+Add own”, a text field will appear. Enter the number of nodes and press Enter.

        - The selected values must match the available data files.
        - If a file is missing for the selected configuration, an error message will appear.

        3. **Choose the time type** for analysis:
        - *Average Time* — displays average response times per query or repetition.
        - *Total Time* — displays the total execution times.

        4. **Select the chart mode** (how data will be visualized):
        - **Repetition Distribution for a Query**:  
            - Shows the distribution of all measured repetitions for a single query (e.g., Query 5) in both environments.
            - Use the dropdown to select which query to analyze (Query 1–22 or 'Total' for the summary row).
            - Only works with files containing repeated runs (columns named HDFS_Set1, MINIO_Set1, etc.).
            - If such columns are missing, please select the other mode or a different file.
        - **Response Time Distribution for All Queries**:  
            - Shows the distribution of response times across all queries (each query counted once).
            - Useful for files that do **not** include repeated runs, but only one value per query.

        5. Click **"Generate Boxplot"** to create the visualization.

        6. After the plot is generated, the application will display the file path where the PNG chart has been saved.

        7. Click **"Show Generated Boxplot"** to instantly open the most recent chart in your default image viewer.

        **Chart Features:**
        - For every generated boxplot, key statistics are shown on the image: median, quartiles, interquartile range, min, and max for each environment.
        - Boxplots visually compare the spread and distribution of execution times for both HDFS and MinIO.

        **Notes:**
        - If you enter a custom dataset size or node count, the program will look for a matching Excel file in the .benchmark_data folder.
        - The module automatically recognizes Excel columns, regardless of case (e.g., MINIO_Average, MinIO_Average, etc.).
        - Only properly formatted Excel files in the .benchmark_data folder are supported.
        - If a required column or file is missing, a detailed error will appear under the buttons.
        - All generated plots are saved in the .generated_files/boxplot_files directory.

        **Frequently Asked Questions:**
        - **Q:** What is the difference between the two chart modes?  
        **A:**  
        - *Repetition Distribution for a Query* shows the variation across all repeated runs for a single query, helping you spot outliers or stability issues for that query.
        - *Response Time Distribution for All Queries* summarizes the variability across all queries, providing an overall performance picture for the chosen dataset and environment.

        - **Q:** How do I add my own dataset size or node count?  
        **A:** Select “+Add own” in the dropdown, type your value in the field that appears, and press Enter.

        - **Q:** Why can’t I select the 'Repetition Distribution' mode for some files?  
        **A:** Some files may not contain repeated runs for each query. In that case, only 'Response Time Distribution for All Queries' is available.

        - **Q:** Where are the generated boxplots saved?  
        **A:** File paths are shown after generation. All boxplots are saved in the .generated_files/boxplot_files directory.

        - **Q:** What if my data file uses a different case for column names?  
        **A:** The app recognizes column names regardless of case (e.g., MinIO_Average and MINIO_Average are both valid).

        Click **"Help"** at any time to view this guide again.

        Module version: Boxplot Module (Custom Input) v1.1.0
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
