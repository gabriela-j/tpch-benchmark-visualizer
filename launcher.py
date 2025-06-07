import customtkinter as ctk
import sys
import os

# --- Add project subfolders to sys.path to allow for cross-module imports ---
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE, "Peak&Spill"))
sys.path.append(os.path.join(BASE, "ResponseTime"))

# --- Import the main app classes from analysis modules ---
from PeakSpill.PeakSpillApp import PeakSpillApp
from ResponseTime.ResponseTimeApp import ResponseTimeApp

class MainLauncherApp(ctk.CTk):
    """
    Main launcher window for the Benchmark Visualization Tool.
    Lets the user choose which analysis module to run.
    """
    def __init__(self):
        super().__init__()
        # Set appearance and basic window properties
        ctk.set_appearance_mode("System")  # Respect system theme
        ctk.set_default_color_theme("blue")
        self.title("Benchmark Visualization Tool")
        self.geometry("450x380")

        # Internal state for active view and help popup
        self.active_view = None
        self.help_popup_window = None

        self.show_main_menu()  # Display the main menu on startup

    def clear_active_view(self):
        """
        Remove and destroy the currently active view/frame if it exists.
        Ensures there is never more than one main frame displayed.
        """
        if self.active_view:
            self.active_view.pack_forget()
            self.active_view.destroy()
            self.active_view = None

    def show_main_menu(self):
        """
        Display the main menu for module selection and help.
        """
        self.clear_active_view()
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True)

        # Menu label/title
        label = ctk.CTkLabel(
            frame,
            text="Select program to run:",
            font=ctk.CTkFont(size=22, weight="bold"),
            wraplength=460,
        )
        label.pack(pady=30)

        # Module selection buttons
        ctk.CTkButton(
            frame, text="Peak & Spill", width=250, height=60,
            command=lambda: self.launch_app("peakspill")
        ).pack(pady=8)
        ctk.CTkButton(
            frame, text="ResponseTime", width=250, height=60,
            command=lambda: self.launch_app("responsetime")
        ).pack(pady=8)

        # Help button at the bottom of the menu
        ctk.CTkButton(
            frame, text="Help", width=120,
            command=self.show_help_popup,
            fg_color="#F59E0B", hover_color="#D97706"
        ).pack(pady=(66,0))

        self.active_view = frame

    def launch_app(self, which):
        """
        Launch the selected analysis module.
        Switches the view to the selected module's app window.
        """
        self.clear_active_view()
        if which == "peakspill":
            # Launch Peak & Spill module
            self.active_view = PeakSpillApp(self, go_back=self.show_main_menu)
        elif which == "responsetime":
            # Launch ResponseTime module
            self.active_view = ResponseTimeApp(self, go_back=self.show_main_menu)
        else:
            # If unknown selection, go back to main menu
            self.show_main_menu()
            return
        self.active_view.pack(fill="both", expand=True)

    def show_help_popup(self):
        """
        Show a popup window with a user guide/help for the application.
        Only one help window can be open at a time.
        """
        # Bring help window to front if already open
        if self.help_popup_window is not None and self.help_popup_window.winfo_exists():
            self.help_popup_window.lift()
            return

        # Create help popup as a top-level window
        self.help_popup_window = ctk.CTkToplevel(self)
        self.help_popup_window.title("Help – Program Overview")
        self.help_popup_window.geometry("750x590")
        self.help_popup_window.attributes("-topmost", True)

        def on_close():
            self.help_popup_window.destroy()
            self.help_popup_window = None

        self.help_popup_window.protocol("WM_DELETE_WINDOW", on_close)

        # Detailed program description and user instructions
        help_text = """User Guide — Benchmark Visualization Tool

    Welcome to the Benchmark Suite! This application lets you explore and visualize results from TPC-H benchmark experiments using two specialized analysis modules:

    ▶  **Peak & Spill**
    - Generate interactive reports showing CPU peak, memory peak, and data spill (amount written to disk due to memory overflow).
    - Useful for quickly identifying resource bottlenecks and spotting potential issues with memory or CPU saturation.
    - Input: Excel files with summary metrics for each test case.
    - Output: HTML report files for easy viewing and sharing.

    ▶  **ResponseTime**
    - Analyze the execution times of TPC-H queries across different cluster configurations and environments (HDFS, MinIO), with flexible support for both detailed and high-level analyses.
    - **Two main analysis modes:**
        1. **Single Query — Stability Analysis:**  
        Explore the stability and repeatability of execution times for a selected query, using data from multiple test repetitions. Visualize distributions, check for outliers, and compare \nenvironments.
        2. **All Queries — Overview Analysis:**  
        Compare the distribution of execution times for all 22 TPC-H queries for a chosen dataset size and number of nodes. Useful for identifying broad performance trends and \ncomparing overall efficiency.
    - Both modes are available within a single, unified module. Simply select your preferred analysis mode in the program window.
    - Input: Excel files either with repeated executions per query (for stability analysis), or files grouped by dataset size and node count (for overview analysis).
    - Output: Interactive charts (boxplots, bar charts, heatmaps) for both focused and cross-sectional insights.

    **When to use which mode?**
    - Use the **All Queries — Overview Analysis** to get a high-level view of overall performance for all queries and configurations.
    - Use the **Single Query — Stability Analysis** if you want to deep-dive into a specific query, check for instability, or explore outlier behavior across multiple test runs.
    - Use **Peak & Spill** for practical insights into system-level bottlenecks (CPU, RAM, disk spill).

    **General Notes:**
    - All modules require properly formatted Excel files placed in their respective `.benchmark_data` directories.
    - You can always return to this menu and re-run any analysis you need.
    - Click the “Help” button in any module for a detailed guide on its usage and options.

    Module version: Benchmark Suite v1.0.0
    """

        # Add a scrollable frame for long help text
        scroll_frame = ctk.CTkScrollableFrame(self.help_popup_window, width=700, height=480)
        scroll_frame.pack(padx=24, pady=16, fill="both", expand=True)

        help_label = ctk.CTkLabel(
            scroll_frame,
            text=help_text,
            justify="left",
            anchor="nw",
            wraplength=400,
            font=ctk.CTkFont(size=15)
        )
        help_label.pack(anchor="nw", pady=5, padx=(0,20), expand=True, fill="both")

        # Make the help text responsive to window resizing
        def on_resize(event):
            margin=40
            w = scroll_frame.winfo_width() - margin
            if w > 200:
                help_label.configure(wraplength=w)
        self.help_popup_window.bind("<Configure>", on_resize)


if __name__ == "__main__":
    # Run the main application loop
    app = MainLauncherApp()
    app.mainloop()
