# Visualization and Analysis Tool for Benchmark Data in Serverless and Serverful Environments

## Overview

This repository contains a **modular Python application** for **visualizing and analyzing TPC-H benchmark results** collected from both serverful (HDFS) and serverless (MinIO) computing environments. The tool was designed to address the challenges of working with static snapshot performance data (e.g., single-result Excel files) which cannot be effectively visualized using traditional monitoring dashboards such as Grafana.

The application allows users to flexibly explore and compare CPU usage, memory peaks, disk spills, and query response times across different cluster configurations, environments, and dataset sizes.

---

## Key Features

- **Interactive Visualizations:** Generate bar charts, boxplots, and heatmaps to compare performance metrics across environments.
- **Support for Custom Input:** Easily add your own dataset sizes or node counts through the GUI without modifying code.
- **Modular Design:** Independent submodules for different analysis types (Peak/Spill metrics and Response Times).
- **User-friendly GUI:** Built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for a modern look and ease of use.
- **Comprehensive Help:** Each module provides an integrated help window.
- **Automatic File Handling:** Input and output files are organized in clear, separate folders.
- **Robust Error Handling:** The app provides meaningful messages if files or columns are missing.

---

## Table of Contents

- Overview
- Key Features
- Screenshots
- Folder Structure
- Requirements
- Installation & Setup
- Usage
- Modules Description
- How to Add Your Own Data
- Troubleshooting
- References

---

## Screenshots
> ![launcher](https://github.com/user-attachments/assets/0f09f070-a518-410d-b5f6-4478f73b6d6f)

>![PeakSpill](https://github.com/user-attachments/assets/7aca6c41-7ae0-4974-bd45-4cd2bfa5fbd6)
>![ResponseTime](https://github.com/user-attachments/assets/bb775fe6-eb9c-46c2-8eb4-43627ce7268b)
>![bar_chart](https://github.com/user-attachments/assets/49566425-5094-4608-803f-473ffd49ecc5)
>![boxplot](https://github.com/user-attachments/assets/3b85f0fa-95bc-4bfb-b2e3-6970571717d8)
>![heatmap (2)](https://github.com/user-attachments/assets/23120ea6-f948-44c4-9287-c0dd45d0a328)
>![boxplot_query 1_1gb_1node](https://github.com/user-attachments/assets/591339e3-981d-4142-90bc-228cec6e8403)
>![bar_average_1gb](https://github.com/user-attachments/assets/5e10316b-e112-4291-be16-ee755b54f50e)
>![memory_peak](https://github.com/user-attachments/assets/beaa0d48-088e-483e-8af1-b388f60bd61d)
>![cpu_peak](https://github.com/user-attachments/assets/0ddfb7f8-6c42-48b0-8b04-e81bf1cf5618)
>![spill](https://github.com/user-attachments/assets/a089ae08-da3c-4242-a37d-18b458495841)










---

## Folder Structure

├── launcher.py    # Main file that launches the application (launcher/main window) 

├── PeakSpill/

│ ├── PeakSpillApp.py   # 'Peak & Spill' module

│ ├── memory_peak.py # Script for generating memory charts

│ ├── cpu_peak.py # Script for generating CPU charts

│ ├── spill.py # Script for generating spill charts

│ ├── **init**.py

│ ├── .benchmark_data/ # Input data (Excel)

│ └── 1Gb/

│ │ └── ...

│ └── ...

│ └── .generated_files/ # Output files (HTML)

│ └── cpu_peak_files/

│ │ └── ...

│ └── memory_files/

│ │ └── ...

│ └── spill_files/

│ └── ...

|

├── ResponseTime/

│ ├── ResponseTimeApp.py # 'ResponseTime' module

│ ├── bar_chart.py # Class for generating bar charts

│ ├── boxplot.py # Class for generating boxplots (for different repetitions or different queries)

│ ├── heatmap.py # Class for generating heatmaps

│ ├── **init**.py

│ ├── .benchmark_data/ # Input data (Excel)

│ └── 1Gb/

│ │ └── ...

│ └── ...

│ └── .generated_files/ # Output files (HTML/PNG)

│ └── bar_chart_files/

│ │ └── ...

│ └── boxplot_files/

│ │ └── ...

│ └── heatmap_files/

│ └── ...

...

│

└── README.md


---

## Requirements

**Python 3.8+**

Install required libraries using pip:

pip install pandas numpy plotly matplotlib customtkinter openpyxl

**Standard Libraries (no extra install):**

- tkinter
- os
- sys
- time
- subprocess
- webbrowser

---

## Installation & Setup

1. Clone the repository:
   git clone https://github.com/gabriela-j/tpch-benchmark-visualizer.git
   cd your-repo

2. Prepare your input data:

   - Place all benchmark Excel files in the `.benchmark_data/` subfolders. See **How to Add Your Own Data** below for details.

3. Install dependencies:
   pip install -r requirements.txt
   (Or use the pip command above if you don't have a requirements.txt)

4. Run the launcher:
   python main_launcher.py

---

## Usage

- Choose a module from the launcher window (Peak & Spill, Response Time)
- Select dataset size, node count, and other parameters
- Add your own dataset size/nodes by selecting "+Add own" and typing your value
- Generate the chart (PNG/HTML files are saved automatically)
- Open in browser or image viewer using the app's buttons

See in-app Help for each module for detailed instructions!

---

## Modules Description

- **Peak & Spill (`cpu_peak.py`, `memory_peak.py`, `spill.py`):**

  - Visualize CPU peak, memory peak, and disk spill for all queries.
  - Output: interactive bar charts (HTML).

- **Bar Chart (`bar_chart.py`):**

  - Compare response times for selected queries or total, across environments.
  - Output: interactive HTML and PNG charts.

- **Boxplot (`boxplot.py`):**

  - Analyze distribution of repetitions for a query or for all queries.
  - Output: PNG boxplot with statistical summary.

- **Heatmap (`heatmap.py`):**

  - See the "big picture" across queries/environments as a color grid.
  - Output: PNG heatmap.

- **main_launcher.py:**
  - The entry point to select between analysis modules.

---

## How to Add Your Own Data

- **Input files:** Place your Excel files in the appropriate `.benchmark_data/<size>/` folder, e.g.:
  - `.benchmark_data/1GB/tpc_h-1Gb-W-1-node(s).xlsx`
  - The filename pattern must match the modules’ expectations (see Help in each module).
- **Custom values:** To analyze new dataset sizes or node counts, just add the corresponding file and select "+Add own" in the GUI!

---

## Troubleshooting

- **Missing file:** Check that your Excel file is in the right folder and follows the expected naming convention.
- **Missing columns:** See the help text in each module for expected column names (case-insensitive, e.g. `HDFS_Average`).
- **No chart generated:** Ensure you’ve selected all required options and that your data is formatted correctly.

---

## References

See the `References` section in the attached project report for full literature and background.

---

## License

This project is for academic purposes. See LICENSE file (add your license).

---

Developed by Gabriela Jung, ISEC — Polytechnic University of Coimbra, 2025

For questions or contributions, open an issue or pull request!
