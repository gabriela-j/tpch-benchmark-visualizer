import customtkinter as ctk
import os
import webbrowser
import time
import pandas as pd
import plotly.graph_objects as go

class BarChartApp(ctk.CTkFrame):
    """
    Main frame for generating bar charts comparing TPC-H benchmark query times
    between different environments (HDFS vs MinIO), for any dataset size, node count,
    and chosen queries. Supports both average and total execution times.
    """

    def __init__(self, parent, go_back):
        """
        Build and display the Bar Chart GUI.
        Args:
            parent: Parent Tkinter widget.
            go_back: Callback to return to the previous menu.
        """
        super().__init__(parent)
        self.parent = parent
        self.go_back = go_back
        self.help_popup_window = None

        # --- Options for datasets, nodes, and time types ---
        self.datasets = ["1GB", "10GB", "20GB", "+Add own"]
        self.nodes_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "15", "+Add own"]
        self.time_types = ["Average Time", "Total Time"]

        # --- Query selection checkboxes ---
        self.query_vars = []       # [(label, BooleanVar)]
        self.query_checkboxes = [] # [CheckBox]
        self.total_var = ctk.BooleanVar()  # 'Total' summary

        # --- Default variable values ---
        self.dataset_var = ctk.StringVar(value=self.datasets[0])
        self.nodes_var = ctk.StringVar(value="1")
        self.time_type_var = ctk.StringVar(value=self.time_types[0])

        # --- Layout: main frame for all widgets ---
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Header with 'Select/Deselect all' ---
        header_frame = ctk.CTkFrame(frame)
        header_frame.pack(pady=5)
        header_frame.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(header_frame, text="Choose queries:").grid(row=0, column=0, padx=10)

        # Button to toggle all query checkboxes at once
        def toggle_all_queries():
            all_selected = all(var.get() for _, var in self.query_vars)
            for _, var in self.query_vars:
                var.set(not all_selected)
        ctk.CTkButton(header_frame, text="Select / Deselect All", command=toggle_all_queries).grid(row=0, column=1, padx=10)

        # --- Query selection (scrollable) ---
        self.query_frame = ctk.CTkScrollableFrame(frame, height=100)
        self.query_frame.pack(pady=5, padx=80, fill="x")
        for i in range(1, 23):
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(self.query_frame, text=f"Query {i}", variable=var, command=self.on_query_toggle)
            checkbox.pack(anchor="w", padx=10)
            self.query_vars.append((f"Query {i}", var))
            self.query_checkboxes.append(checkbox)
        # 'Total' checkbox (disables query checkboxes if selected)
        self.total_checkbox = ctk.CTkCheckBox(self.query_frame, text="Total", variable=self.total_var, command=self.on_total_toggle)
        self.total_checkbox.pack(anchor="w", padx=10)

        # --- Dataset, Nodes, Time Type selection row ---
        selection_row_frame = ctk.CTkFrame(frame, fg_color="transparent")
        selection_row_frame.pack(pady=(20, 5))

        # Dataset selector (optionmenu + custom)
        dataset_frame = ctk.CTkFrame(selection_row_frame, fg_color="transparent")
        dataset_frame.pack(side="left", padx=10)
        ctk.CTkLabel(dataset_frame, text="Dataset Size:", font=ctk.CTkFont(size=14)).pack()
        self.dataset_optionmenu = ctk.CTkOptionMenu(dataset_frame, variable=self.dataset_var, values=self.datasets, command=self.on_dataset_select)
        self.dataset_optionmenu.pack()
        self.dataset_entry = None

        # Nodes selector (optionmenu + custom)
        nodes_frame = ctk.CTkFrame(selection_row_frame, fg_color="transparent")
        nodes_frame.pack(side="left", padx=10)
        ctk.CTkLabel(nodes_frame, text="Number of Nodes:", font=ctk.CTkFont(size=14)).pack()
        self.nodes_optionmenu = ctk.CTkOptionMenu(nodes_frame, variable=self.nodes_var, values=self.nodes_options, command=self.on_nodes_select)
        self.nodes_optionmenu.pack()
        self.nodes_entry = None

        # Time type selector
        time_frame = ctk.CTkFrame(selection_row_frame, fg_color="transparent")
        time_frame.pack(side="left", padx=10)
        ctk.CTkLabel(time_frame, text="Time Type:", font=ctk.CTkFont(size=14)).pack()
        ctk.CTkOptionMenu(time_frame, variable=self.time_type_var, values=self.time_types).pack()

        # --- Action buttons: generate/open chart ---
        button_row_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_row_frame.pack(pady=15)
        ctk.CTkButton(
            button_row_frame, text="Generate Charts",
            command=self.on_generate_button_click,
            fg_color="#3B82F6", hover_color="#2563EB", width=160
        ).pack(side="left", padx=10)
        self.browser_button = ctk.CTkButton(
            button_row_frame, text="Open in Browser",
            command=self.on_browser_button_click,
            fg_color="#10B981", hover_color="#059669", width=160
        )
        self.browser_button.pack(side="left", padx=10)
        self.browser_button.html_paths = []

        # --- Status label for feedback/errors ---
        self.status_label = ctk.CTkLabel(frame, text="", wraplength=650, justify="center", text_color="white")
        self.status_label.pack(pady=15)

        # --- Bottom navigation: Go Back / Help ---
        bottom_btn_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_btn_row.pack(pady=10)
        ctk.CTkButton(
            bottom_btn_row, text="Go Back", command=self.go_back,
            fg_color="#6B7280", hover_color="#4B5563", width=150
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            bottom_btn_row, text="Help", command=self.show_help_popup,
            fg_color="#F59E0B", hover_color="#D97706", width=150
        ).pack(side="left", padx=10)

    # --------------- Custom dataset entry ---------------
    def on_dataset_select(self, value):
        """
        Show a text entry for custom dataset size if '+Add own' is chosen,
        or set selection to a predefined option.
        """
        if value == "+Add own":
            self.dataset_var.set("")
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

    # --------------- Custom nodes entry ---------------
    def on_nodes_select(self, value):
        """
        Show a text entry for custom node count if '+Add own' is chosen,
        or set selection to a predefined option.
        """
        if value == "+Add own":
            self.nodes_var.set("")
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

    # --------------- Query and Total logic ---------------
    def on_total_toggle(self):
        """
        If 'Total' is checked, disable individual query checkboxes and deselect them.
        If 'Total' is unchecked, enable individual query checkboxes.
        """
        total_selected = self.total_var.get()
        for _, var in self.query_vars:
            var.set(False)
        for checkbox in self.query_checkboxes:
            checkbox.configure(state="disabled" if total_selected else "normal")

    def on_query_toggle(self):
        """
        If any individual query is checked, uncheck 'Total' and enable its checkbox.
        """
        if any(var.get() for _, var in self.query_vars):
            self.total_var.set(False)
            self.total_checkbox.configure(state="normal")

    # --------------- Generate and open charts ---------------
    def on_generate_button_click(self):
        """
        Collect all selections and generate the requested chart(s).
        Display status and set browser button paths.
        """
        selected_queries = [name for name, var in self.query_vars if var.get()]
        if self.total_var.get():
            selected_queries = ["Total"]
        selected_dataset = self.dataset_var.get()
        selected_nodes = self.nodes_var.get()
        if not selected_dataset or not selected_nodes:
            self.status_label.configure(text="Please choose data size and number of nodes!", text_color="orange")
            return
        selected_time_type = self.time_type_var.get()
        self.status_label.configure(text="Generating charts...", text_color="white")
        html_paths = self.generate_charts(selected_queries, selected_dataset, selected_nodes, selected_time_type)
        self.browser_button.html_paths = html_paths

    def on_browser_button_click(self):
        """
        Open the last generated chart in the system default browser.
        """
        if not hasattr(self.browser_button, 'html_paths') or not self.browser_button.html_paths:
            self.status_label.configure(text="No chart to show in a browser!", text_color="orange")
            return
        try:
            webbrowser.open(f"file://{self.browser_button.html_paths[0]}")
            self.status_label.configure(text=f"Chart opened in browser:\n{self.browser_button.html_paths[0]}", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Error opening chart: {e}", text_color="red")

    def generate_charts(self, selected_queries, dataset_choice, nodes_choice, time_type):
        """
        Core logic for creating a bar chart: loads benchmark Excel file, extracts data
        for selected queries and environments, builds plotly figure, saves as HTML/PNG.
        Returns list of paths to generated HTML files.
        """
        output_dir = os.path.join(os.path.dirname(__file__), ".generated_files", "bar_chart_files")
        os.makedirs(output_dir, exist_ok=True)
        status_messages = []

        # Map dataset display names to folder names (e.g., 1GB -> 1Gb)
        dataset_folders = {ds: ds.replace("GB", "Gb") for ds in self.datasets if ds != "+Add own"}
        dataset_folder = dataset_folders.get(dataset_choice, dataset_choice.replace("GB", "Gb"))

        base_path = os.path.join(os.path.dirname(__file__), ".benchmark_data")
        excel_file = os.path.join(base_path, dataset_folder, f"tpc_h-{dataset_folder}-W-{nodes_choice}-node(s).xlsx")

        if not os.path.exists(excel_file):
            status_messages.append(f"Error: No data for this dataset and nodes!\nFile not found:\n{excel_file}")
            self.status_label.configure(text="\n".join(status_messages), text_color="red")
            return []

        # Determine column indices for HDFS/MinIO times depending on user selection
        if time_type == "Average Time":
            title_prefix = "Average"
            hdfs_col_index = -6
            minio_col_index = -5
        else:
            title_prefix = "Total"
            hdfs_col_index = -2
            minio_col_index = -1

        html_paths = []
        try:
            data = pd.read_excel(excel_file)
            if "Total" in selected_queries:
                # Use the entire file for total summary
                data = data
            else:
                # Drop the 'Total' row for per-query selection
                data = data.iloc[:-1]
        except Exception as e:
            status_messages.append(f"Error loading file {excel_file}: {e}")
            self.status_label.configure(text="\n".join(status_messages), text_color="red")
            return []

        # Prepare plot data
        all_data = []
        hover_texts = {}
        for query in selected_queries:
            if query == "Total":
                query_idx = len(data) - 1
                label = "Total"
            else:
                query_idx = int(query.split()[-1]) - 1
                label = f"Q{query_idx + 1}"
            if query_idx < 0 or query_idx >= len(data):
                status_messages.append(f"Error: Query {query} does not exist!")
                continue
            query_data = data.iloc[query_idx]
            hdfs_value = float(query_data.iloc[hdfs_col_index]) if not pd.isna(query_data.iloc[hdfs_col_index]) else 0
            minio_value = float(query_data.iloc[minio_col_index]) if not pd.isna(query_data.iloc[minio_col_index]) else 0
            y_axis_title = f"{title_prefix} Response Time (seconds)"
            # Calculate percentage difference
            if hdfs_value != 0:
                difference = ((hdfs_value - minio_value) / hdfs_value) * 100
            else:
                difference = 0
            # Custom hover texts for each bar
            if difference > 0:
                text_percentage = f"MinIO {difference:.2f}% faster than HDFS"
            elif difference < 0:
                text_percentage = f"HDFS {-difference:.2f}% faster than MinIO"
            else:
                text_percentage = "Both environments have the same response time"
            hover_text_hdfs = f"{label}<br>Serverful (HDFS): {hdfs_value:.6f} s<br>{'HDFS is {:.2f}% slower than MinIO'.format(abs(difference)) if difference > 0 else 'Same time' if difference == 0 else 'HDFS is {:.2f}% faster than MinIO'.format(abs(difference))}"
            hover_text_minio = f"{label}<br>Serverless (MinIO): {minio_value:.6f} s<br>{'MinIO is {:.2f}% faster than HDFS'.format(abs(difference)) if difference > 0 else 'Same time' if difference == 0 else 'MinIO is {:.2f}% slower than HDFS'.format(abs(difference))}"
            hover_texts[(label, "HDFS")] = hover_text_hdfs
            hover_texts[(label, "MinIO")] = hover_text_minio
            all_data.append({"Query": label, "Response Time (s)": hdfs_value, "Environment": "Serverful (HDFS)"})
            all_data.append({"Query": label, "Response Time (s)": minio_value, "Environment": "Serverless (MinIO)"})

        if not all_data:
            status_messages.append("No valid queries chosen!")
            self.status_label.configure(text="\n".join(status_messages), text_color="red")
            return []

        # --- Build the plotly bar chart ---
        bar_data = pd.DataFrame(all_data)
        hdfs_data = bar_data[bar_data["Environment"] == "Serverful (HDFS)"]
        minio_data = bar_data[bar_data["Environment"] == "Serverless (MinIO)"]

        fig_bar = go.Figure()
        fig_bar.add_trace(
            go.Bar(
                x=hdfs_data["Query"],
                y=hdfs_data["Response Time (s)"],
                name="Serverful (HDFS)",
                marker=dict(color="#00C853", line=dict(color="#006600", width=1)),
                hovertext=[hover_texts[(q, "HDFS")] for q in hdfs_data["Query"]],
                hoverinfo="text"
            )
        )
        fig_bar.add_trace(
            go.Bar(
                x=minio_data["Query"],
                y=minio_data["Response Time (s)"],
                name="Serverless (MinIO)",
                marker=dict(color="#0288D1", line=dict(color="#01579B", width=1)),
                hovertext=[hover_texts[(q, "MinIO")] for q in minio_data["Query"]],
                hoverinfo="text"
            )
        )
        y_max = bar_data["Response Time (s)"].max() * 1.2
        y_min = max(0, bar_data["Response Time (s)"].min() * 0.9)
        dtick = max(1, (y_max-y_min)/10)

        fig_bar.update_layout(
            yaxis_title=y_axis_title,
            xaxis_title="Query",
            barmode="group",
            showlegend=True,
            legend_title="Environment",
            plot_bgcolor="#1C2526",
            paper_bgcolor="#1C2526",
            font=dict(family="Helvetica", size=12, color="#FFFFFF"),
            yaxis=dict(
                range=[y_min, y_max],
                tickmode="linear",
                dtick=dtick,
                showline=True,
                linecolor="#FFFFFF",
                linewidth=1,
                showgrid=False,
                zeroline=False,
                tickfont=dict(color="#FFFFFF")
            ),
            xaxis=dict(
                showline=True,
                linecolor="#FFFFFF",
                linewidth=1,
                showgrid=False,
                tickfont=dict(color="#FFFFFF")
            ),
            title=dict(
                text=f"{title_prefix} Response Time per Query ({dataset_choice}, {nodes_choice} Node(s))",
                x=0.5,
                font=dict(family="Helvetica", size=16, color="#FFFFFF")
            ),
            legend=dict(
                font=dict(color="#FFFFFF"),
                bgcolor="#2E3B3C",
                bordercolor="#FFFFFF",
                borderwidth=1
            ),
            margin=dict(l=50, r=50, t=50, b=50),
            hovermode="closest",
            hoverlabel=dict(
                bgcolor="#333333",
                font=dict(color="#FFFFFF")
            )
        )
        # --- Save the chart as PNG and HTML ---
        bar_filename = f"bar_{title_prefix.lower()}_{dataset_choice.lower()}_{nodes_choice}nodes.png"
        bar_path = os.path.join(output_dir, bar_filename)
        try:
            fig_bar.write_image(bar_path, width=1200, height=800, scale=2)
            status_messages.append(f"Chart PNG saved as: {os.path.abspath(bar_path)}")
        except Exception as e:
            status_messages.append(f"Error during PNG file saving for {dataset_choice}, {nodes_choice} nodes: {e}")

        html_filename = f"bar_{title_prefix.lower()}_{dataset_choice.lower()}_{nodes_choice}nodes.html"
        html_path = os.path.join(output_dir, html_filename)
        try:
            fig_bar.write_html(html_path, include_plotlyjs='cdn')
            time.sleep(0.5)
            if os.path.exists(html_path):
                html_paths.append(os.path.abspath(html_path))
                status_messages.append(f"HTML saved as: {os.path.abspath(html_path)}")
            else:
                status_messages.append(f"Error: HTML file {html_path} has not been created.")
        except Exception as e:
            status_messages.append(f"Error during saving HTML file for {dataset_choice}, {nodes_choice} nodes: {e}")

        if any("saved as" in msg for msg in status_messages):
            self.status_label.configure(text="Wykresy wygenerowane pomyślnie!", text_color="green")
        else:
            self.status_label.configure(text="Wystąpił błąd", text_color="red")
        self.status_label.configure(text="\n".join(status_messages))
        return html_paths

    # --------------- Help popup ---------------
    def show_help_popup(self):
        """
        Display a help popup window with instructions for this module.
        Only one help window can be open at a time.
        """
        if self.help_popup_window is not None and self.help_popup_window.winfo_exists():
            self.help_popup_window.lift()
            return

        self.help_popup_window = ctk.CTkToplevel(self)
        self.help_popup_window.title("Help")
        self.help_popup_window.geometry("750x560")
        self.help_popup_window.attributes("-topmost", True)

        def on_close():
            self.help_popup_window.destroy()
            self.help_popup_window = None
        self.help_popup_window.protocol("WM_DELETE_WINDOW", on_close)

        help_text = """User Guide — Bar Chart Module

        This application allows you to generate interactive bar charts from TPC-H benchmark Excel files, comparing response times for different queries, node counts, dataset sizes, and environments \n(HDFS vs. MinIO).

        How to use:

        1. **Select the queries** you want to visualize:
        - You can select one or multiple queries (Query 1, Query 2, etc.).
        - Alternatively, choose 'Total' to generate a chart for the overall summary.
        - *Note*: Selecting 'Total' disables the other checkboxes, and vice versa.

        2. **Choose the dataset size** to analyze (1GB, 10GB, 20GB), or click '+Add own' to enter a custom size.

        3. **Choose the number of nodes** you want to compare (1, 2, 3, ..., 15), or click '+Add own' to enter a custom value.

        4. **Select the time type:**
        - *Average Time* — shows average response times.
        - *Total Time* — shows total execution times.

        5. Click **"Generate Charts"** to create the chart.

        6. After generation, the application will inform you where the `.html` chart file has been saved.

        7. Click **"Open in Browser"** to instantly preview the interactive chart in your default web browser.

        **Interactive features of the HTML chart:**
        - **Zoom in**: Click and drag to select and zoom into any region of the chart.
        - **Export to PNG**: Click the camera icon in the chart’s toolbar to save the current view as a PNG image.
        - **Detailed tooltips**: Hover your mouse over any bar to see detailed benchmark data and percentage differences between environments for each query.

        **Notes:**
        - Only properly formatted Excel files placed in the correct `.benchmark_data` subdirectories are supported.
        - If you select 'Total', you cannot select individual queries at the same time.
        - The application will report all errors (missing files, invalid data) below the buttons.
        - Click “Help” at any time to view this guide again.

        **Frequently Asked Questions:**
        - **Q:** Why can't I select both queries and 'Total'?
        **A:** The chart displays either results for selected queries or the overall 'Total' summary, not both at once.
        - **Q:** Where are the generated files saved?
        **A:** File paths are shown after generation. Charts are saved in the `.generated_files/bar_chart_files` directory.

        Module version: Bar Chart (all datasets & nodes) v1.0.0
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
