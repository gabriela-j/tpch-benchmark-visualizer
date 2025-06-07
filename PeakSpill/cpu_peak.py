import pandas as pd
import plotly.graph_objects as go
import os
import argparse

# --- Parse command-line arguments (dataset size is required) ---
parser = argparse.ArgumentParser()
parser.add_argument('--dataset_size', required=True)
args = parser.parse_args()

# --- Set paths and read input data file ---
dataset_size = args.dataset_size
base_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the correct Excel input file with CPU Peak data
data_file = os.path.join(base_dir, ".benchmark_data", dataset_size, f"cpu_peak_{dataset_size}.xlsx")

# --- Read the Excel data into a pandas DataFrame ---
df = pd.read_excel(data_file)

# --- Prepare axis labels for the chart ---
query_labels = df['Query'].tolist()
labels_short = [f"Q{i+1}" for i in range(len(query_labels))]

# --- Create a grouped bar chart for CPU Peak (HDFS vs MinIO) ---
fig = go.Figure()
fig.add_trace(go.Bar(
    x=labels_short,
    y=df['CPU_Peak_HDFS(%)'],
    name='CPU Peak HDFS (%)',
    marker_color='red',
    hovertext=df['Query'],
    hovertemplate='Query %{hovertext}<br> HDFS: %{y:.2f}%<extra></extra>'
))
fig.add_trace(go.Bar(
    x=labels_short,
    y=df['CPU_Peak_MinIO(%)'],
    name='CPU Peak MinIO (%)',
    marker_color='purple',
    hovertext=df['Query'],
    hovertemplate='Query %{hovertext}<br> MinIO: %{y:.2f}%<extra></extra>'
))

# --- Set chart layout and appearance ---
fig.update_layout(
    title="CPU Peak (%) HDFS vs MinIO",
    xaxis=dict(tickvals=labels_short, ticktext=labels_short),
    yaxis_title="CPU Peak (%)",
    barmode='group',
    legend=dict(x=1, y=1)
)

# --- Output: save chart as HTML file in .generated_files/cpu_peak_files/ ---
output_dir = os.path.join(base_dir, ".generated_files", "cpu_peak_files")
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, "cpu_peak.html")
fig.write_html(filepath)
