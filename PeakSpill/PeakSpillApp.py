import customtkinter as ctk
import subprocess
import os
import webbrowser

class PeakSpillApp(ctk.CTkFrame):
    """
    The main frame for the 'Peak & Spill' module.
    Lets the user generate and view CPU peak, memory peak, and spill reports
    for selected dataset sizes.
    """

    def __init__(self, master, go_back):
        """
        Initialize the Peak & Spill module UI.
        Args:
            master: The parent widget (root window or main app).
            go_back: Callback to return to main menu.
        """
        super().__init__(master)
        self.go_back = go_back
        self.help_popup_window = None

        # Map between metric names, their script files, and output HTML locations
        self.paths = {
            "Memory Peak": ("memory_peak.py", ".generated_files/memory_peak_files/peak_memory.html"),
            "CPU Peak": ("cpu_peak.py", ".generated_files/cpu_peak_files/cpu_peak.html"),
            "Spill": ("spill.py", ".generated_files/spill_files/spill.html"),
        }

        # --- UI: Metric selection ---
        label = ctk.CTkLabel(self, text="Select performance metric:", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=20)

        self.chart_option = ctk.CTkOptionMenu(self, values=list(self.paths.keys()))
        self.chart_option.pack(pady=10)

        # --- UI: Dataset size selection with dynamic entry ---
        self.size_row = ctk.CTkFrame(self, fg_color="transparent")
        self.size_row.pack(pady=5)

        size_label = ctk.CTkLabel(self.size_row, text="Dataset Size:", font=ctk.CTkFont(size=15))
        size_label.pack()

        self.sizes = ["1Gb", "10Gb", "20Gb", "+Add own"]
        self.size_var = ctk.StringVar(value=self.sizes[0])
        self.size_entry = None
        self.size_option = ctk.CTkOptionMenu(self.size_row, variable=self.size_var, values=self.sizes, command=self.on_size_change)
        self.size_option.pack()

        # --- UI: Open-in-browser option ---
        self.open_in_browser = ctk.CTkCheckBox(self, text="Open in a browser")
        self.open_in_browser.pack(pady=5)

        # --- UI: Generate chart button ---
        ctk.CTkButton(self, text="Generate", command=self.generate_chart).pack(pady=15)

        # --- UI: Status label for displaying info/errors ---
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13), wraplength=500, justify="center")
        self.status_label.pack(pady=10)

        # --- UI: Bottom row (Go Back / Help buttons) ---
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

    # ----------------------------------------------------------
    # ------- Custom Dataset Size Handling (+Add own) ----------
    # ----------------------------------------------------------
    def on_size_change(self, value):
        """
        Called when the user selects a dataset size.
        Handles the '+Add own' option by showing an entry field.
        """
        if value == "+Add own":
            # Replace option menu with an entry field for custom input
            if self.size_entry:
                self.size_entry.destroy()
                self.size_entry = None
            self.size_option.pack_forget()
            self.size_entry = ctk.CTkEntry(self.size_row, placeholder_text="Type size, e.g. 32Gb")
            self.size_entry.pack()
            self.size_entry.focus_set()
            self.size_entry.delete(0, "end")
            self.size_entry.bind("<Return>", self.add_custom_size)
            self.size_entry.bind("<FocusOut>", self.add_custom_size)
            self.size_var.set("")
        elif value != "":
            # Restore normal option menu when not adding custom
            if self.size_entry:
                self.size_entry.destroy()
                self.size_entry = None
            self.size_var.set(value)
            self.size_option.pack()

    def add_custom_size(self, event):
        """
        Called when the user enters a custom dataset size and confirms.
        Adds the value to the sizes list and switches back to the option menu.
        """
        if not self.size_entry:
            return
        value = self.size_entry.get().strip()
        if value and value not in self.sizes:
            self.sizes.insert(-1, value)
            self.size_option.configure(values=self.sizes)
            self.size_var.set(value)
        elif value:
            self.size_var.set(value)
        self.size_entry.destroy()
        self.size_entry = None
        self.size_option.pack()

    # ----------------------------------------------------------
    def get_dataset_size(self):
        """
        Get the currently selected or entered dataset size.
        Returns None if nothing is selected.
        """
        selected = self.size_var.get()
        if not selected:
            return None
        return selected

    def generate_chart(self):
        """
        Launch the selected analysis script as a subprocess.
        Shows status/errors and opens the resulting HTML chart if requested.
        """
        chart_type = self.chart_option.get()
        script, html_file = self.paths[chart_type]
        dataset_size = self.get_dataset_size()
        if not dataset_size:
            self.status_label.configure(text="Please select or enter a dataset size.", text_color="red")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, script)
        html_file_path = os.path.join(base_dir, html_file)

        try:
            # Call the analysis script with subprocess
            subprocess.run(
                ["python", script_path, "--dataset_size", dataset_size],
                check=True
            )
            # After successful script execution, check if output HTML exists
            if os.path.exists(html_file_path):
                if self.open_in_browser.get() == 1:
                    webbrowser.open(f"file://{os.path.abspath(html_file_path)}")
                self.status_label.configure(
                    text=f"Chart saved:\n{os.path.abspath(html_file_path)}",
                    text_color="green"
                )
            else:
                self.status_label.configure(text="The final file does not exist.", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="red")

    def show_help_popup(self):
        """
        Display a popup window with detailed instructions for this module.
        Only one help window can be open at a time.
        """
        if self.help_popup_window is not None and self.help_popup_window.winfo_exists():
            self.help_popup_window.lift()
            return

        self.help_popup_window = ctk.CTkToplevel(self)
        self.help_popup_window.title("Help — Peak & Spill Module")
        self.help_popup_window.geometry("750x590")
        self.help_popup_window.attributes("-topmost", True)

        def on_close():
            self.help_popup_window.destroy()
            self.help_popup_window = None

        self.help_popup_window.protocol("WM_DELETE_WINDOW", on_close)

        # User guide text for the popup help window
        help_text = """User Guide — Peak & Spill Module

        This module allows you to quickly visualize key performance metrics — CPU Peak, Memory Peak, and Spill — from your benchmark Excel data.

        How to use:

        1. Select the performance metric you wish to analyze:
        - Choose between Memory Peak (maximum memory usage), CPU Peak (maximum CPU usage), or Spill (amount of data written to disk due to memory overflow).

        2. Select the dataset size from the list or use “+Add own” to enter a custom size (e.g., 32Gb).

        3. Click the “Generate” button to process the Excel data and generate the appropriate chart.
        - The application will run the relevant analysis script, read the necessary Excel files, and produce a report as an interactive HTML file.

        4. (Optional) If you check “Open in a browser,” the generated report will open automatically in your default web browser after generation.

        5. The generated file will be saved in the corresponding subfolder inside the `.generated_files` directory (e.g., `.generated_files/memory_peak_files/peak_memory.html`).

        6. Any errors (such as missing or improperly named files) will be displayed in the status bar below the button area.

        7. Use “Help” to reopen this guide at any time. Click “Go Back” to return to the main menu.

        Notes:
        - Make sure all required benchmark Excel files are present and correctly named in the `.benchmark_data` directory, organized by dataset size.
        - Each time you generate a chart, the output HTML file is overwritten with the latest results.

        Frequently Asked Questions:
        - **Q:** What does each metric mean?
        **A:** 
        - Memory Peak: Highest memory usage recorded during the test.
        - CPU Peak: Highest CPU usage recorded.
        - Spill: Total amount of data written to disk due to memory overflow.
        - **Q:** Where are the generated reports saved?
        **A:** Each report is saved as an HTML file in its respective folder within `.generated_files`.

        **How to Prepare Input Files (Peak & Spill):**

        To ensure correct analysis, all input Excel files **must** be saved in the `.benchmark_data` folder, sorted into subfolders by dataset size, and named with the correct format for each metric.  
        Each file must also follow a specific column layout. See below for details.

        Folder Structure:
            .benchmark_data/
                1Gb/
                    memory_peak_1Gb.xlsx
                    cpu_peak_1Gb.xlsx
                    spill_1Gb.xlsx
                10Gb/
                    memory_peak_10Gb.xlsx
                    cpu_peak_10Gb.xlsx
                    spill_10Gb.xlsx
                20Gb/
                    memory_peak_20Gb.xlsx
                    cpu_peak_20Gb.xlsx
                    spill_20Gb.xlsx
                ...and so on

        File Naming Conventions:
        - **Memory Peak:**  
            memory_peak_{dataset_size}.xlsx   (e.g. memory_peak_20Gb.xlsx)
        - **CPU Peak:**  
            cpu_peak_{dataset_size}.xlsx      (e.g. cpu_peak_20Gb.xlsx)
        - **Spill:**  
            spill_{dataset_size}.xlsx         (e.g. spill_20Gb.xlsx)

        Important:  
        {dataset_size} must match the name of the subfolder (e.g. 1Gb, 10Gb, 20Gb, etc.).

        Excel File Structure (columns):

        Memory Peak:  
            | Query | Peak Memory (GiB) |
            - Query: Numbers 1–22 (for each TPC-H query).
            - Peak Memory (GiB): Peak memory usage for each query, in GiB.

        CPU Peak:  
            | Query | CPU Peak HDFS (%) | CPU Peak MinIO (%) |
            - Query: Numbers 1–22.
            - CPU Peak HDFS (%): Maximum CPU usage (percent) for HDFS for each query.
            - CPU Peak MinIO (%): Maximum CPU usage (percent) for MinIO for each query.

        Spill:  
            | Query | HDFS Spill (GiB) | MinIO Spill (GiB) |
            - Query: Numbers 1–22.
            - HDFS Spill (GiB): Total spill to disk (GiB) for HDFS.
            - MinIO Spill (GiB): Total spill to disk (GiB) for MinIO.

        Summary & Hints:
        - All three input files **must be placed in the subfolder matching the dataset size**, e.g. 10Gb/, 20Gb/.
        - The application will show an error if the required file is missing or its columns are not as expected.
        - Each file should contain one row per query (Query 1–22).
        - No extra columns are required; extra columns will be ignored.
        - Use provided sample files as a reference for structure and naming.

        Module version: Peak & Spill v1.0.0
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