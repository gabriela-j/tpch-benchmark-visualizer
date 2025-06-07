import customtkinter as ctk
from ResponseTime.bar_chart import BarChartApp
from ResponseTime.boxplot import BoxplotApp as BoxplotApp
from ResponseTime.heatmap import HeatmapApp

class ResponseTimeApp(ctk.CTkFrame):
    """
    Main frame for the 'ResponseTime' module.
    Allows the user to select and launch different chart types (Bar Chart, Boxplot, Heatmap)
    for analyzing query execution times from TPC-H benchmark data.
    """

    def __init__(self, master, go_back):
        """
        Initialize the ResponseTime module menu UI.
        Args:
            master: The parent widget (main window or application).
            go_back: Callback to return to the main menu.
        """
        super().__init__(master)
        self.go_back = go_back
        self.active_view = None  # Holds current subview (e.g. chart app)
        self.help_popup_window = None  # Holds reference to the help popup

        # --- Main menu frame ---
        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.pack(fill="both", expand=True)

        # --- Menu label/title ---
        label = ctk.CTkLabel(
            self.menu_frame,
            text="Choose the type of chart:",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        label.pack(pady=20)

        # --- Chart selection buttons ---
        ctk.CTkButton(self.menu_frame, text="Bar Chart", command=self.show_bar_chart).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Boxplot", command=self.show_boxplot).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Heatmap", command=self.show_heatmap).pack(pady=10)

        # --- Bottom row: Go Back and Help buttons ---
        bottom_btn_row = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        bottom_btn_row.pack(pady=10, side="bottom")

        ctk.CTkButton(
            bottom_btn_row, text="Go Back", command=self.go_back,
            fg_color="#6B7280", hover_color="#4B5563", width=160
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom_btn_row, text="Help", command=self.show_help_popup,
            fg_color="#F59E0B", hover_color="#D97706", width=160
        ).pack(side="left", padx=10)

    def clear_active_view(self):
        """
        Remove and destroy the currently active subview (if any).
        Ensures only one chart window is visible at a time.
        """
        if self.active_view:
            self.active_view.pack_forget()
            self.active_view.destroy()
            self.active_view = None

    def show_menu(self):
        """
        Return to the main chart selection menu.
        """
        self.clear_active_view()
        self.menu_frame.pack(fill="both", expand=True)

    def show_bar_chart(self):
        """
        Switch to the Bar Chart analysis submodule.
        """
        self.menu_frame.pack_forget()
        self.active_view = BarChartApp(self, go_back=self.show_menu)
        self.active_view.pack(fill="both", expand=True)

    def show_boxplot(self):
        """
        Switch to the Boxplot analysis submodule.
        """
        self.menu_frame.pack_forget()
        self.active_view = BoxplotApp(self, go_back=self.show_menu)
        self.active_view.pack(fill="both", expand=True)

    def show_heatmap(self):
        """
        Switch to the Heatmap analysis submodule.
        """
        self.menu_frame.pack_forget()
        self.active_view = HeatmapApp(self, go_back=self.show_menu)
        self.active_view.pack(fill="both", expand=True)

    def show_help_popup(self):
        """
        Display a popup window with detailed instructions for this module.
        Only one help window can be open at a time.
        """
        if self.help_popup_window is not None and self.help_popup_window.winfo_exists():
            self.help_popup_window.lift()
            return

        self.help_popup_window = ctk.CTkToplevel(self)
        self.help_popup_window.title("Help")
        self.help_popup_window.geometry("600x550")
        self.help_popup_window.attributes("-topmost", True)

        def on_close():
            self.help_popup_window.destroy()
            self.help_popup_window = None

        self.help_popup_window.protocol("WM_DELETE_WINDOW", on_close)

        # User guide text for the popup help window
        help_text = """User Guide — ResponseTime Module

            This module allows you to analyze and visualize execution times for individual queries from TPC-H benchmark datasets.

            How to use:

            1. Select the chart type you want to generate:
            - **Bar Chart:** Compare average/total times for one or more queries between different environments (e.g., HDFS and MinIO).
            - **Boxplot:** See the distribution and stability of execution times for a single selected query (or the 'Total' summary), based on multiple test repetitions.
            - **Heatmap:** Visualize response times for different queries and environments in a color-coded grid.

            2. After selecting the chart type, customize your analysis by choosing:
            - Specific queries or 'Total' summary (depending on chart type).
            - Dataset size (1GB, 10GB, 20GB).
            - Time metric (Average Time or Total Time).

            3. Click the appropriate button (e.g., “Generate Charts” or “Generate Boxplots”) to create the visualization.

            4. The application will inform you where the output file has been saved (if applicable), and you can open it directly in your browser or viewer.

            5. You can click the “Help” button at any time to reopen this guide. Use “Go Back” to return to the main menu.

            Notes:
            - All required Excel benchmark files must be placed in the '.benchmark_data' folder for the module to function correctly.
            - If a file is missing or the data is invalid, an error message will be shown below the buttons.
            - The boxplot feature is designed to analyze the stability of one selected query — it visualizes the spread of results across many test repetitions.

            How to Prepare Input Files:

            To ensure correct processing of your benchmark data, input Excel files **must** follow these rules:

            1. **Location and Naming:**
            - All Excel files should be placed in the `.benchmark_data` folder, **organized by dataset size** (for example: `1Gb`, `10Gb`, `20Gb`).
            - Each file must be named in the format:  
                `tpc_h-{dataset_folder}-W-{nodes}-node(s).xlsx`
                Where:
                - `{dataset_folder}` is the subfolder name indicating the dataset size (e.g., `1Gb`)
                - `{nodes}` is the number of nodes used (e.g., `1` or `3`)
            - Example full path:  
                `.benchmark_data/1Gb/tpc_h-1Gb-W-1-node(s).xlsx`

            2. **Excel File Structure:**
            - The **first row** must contain the column headers.
            - The **first column** should be `"Query"`, containing numbers `"1"` through `"22"` for individual TPC-H queries and `"Total"` for the summary row.
            - The **next columns** should contain response times for HDFS and MinIO (there may be results from multiple test repetitions or just the final/important columns).
            - The following columns are **required at the end** (in this exact order):  
                - `HDFS_Average`
                - `MinIO_Average`
                - `Difference`
                - `Difference(%)`
                - `HDFS_Total`
                - `MinIO_Total`

            Example column order (can include additional repetition columns between "Query" and the summary columns):
            ```
            Query | HDFS_Set1 | MinIO_Set1 | HDFS_Set2 | MinIO_Set2 | ... | HDFS_Average | MinIO_Average | Difference | Difference(%) | HDFS_Total | MinIO_Total
            ```

            **Important:**
            - The application requires the columns listed above to be present and in the correct order to function properly.
            - If any files or columns are missing, you will see an error message below the chart buttons.
            - See the provided sample files for reference.

            Frequently Asked Questions:
            - **Q:** Can I analyze all queries at once?
            **A:** For detailed analysis of all queries together, use the “ResponseTime_withNodes” module instead.
            - **Q:** What if I select both a query and 'Total'?
            **A:** You must choose either a specific query or the 'Total' summary, not both.

            Module version: ResponseTime v1.0.0
            """

        # --- Scrollable help text in popup window ---
        scroll_frame = ctk.CTkScrollableFrame(self.help_popup_window, width=560, height=260)
        scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)
        help_label = ctk.CTkLabel(
            scroll_frame,
            text=help_text,
            wraplength=1100,
            justify="left",
            anchor="nw"
        )
        help_label.pack(anchor="nw", pady=5, expand=True)
