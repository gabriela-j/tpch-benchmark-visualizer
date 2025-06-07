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

# Path to the correct Excel input file with spill data
data_file = os.path.join(base_dir, ".benchmark_data", dataset_size, f"spill_{dataset_size}.xlsx")
df = pd.read_excel(data_file)

# --- Sort by query number and reset index ---
df = df.sort_values("Query").reset_index(drop=True)

# --- Prepare axis labels for the chart ---
labels_short = [f"Q{i+1}" for i in range(len(df))]
labels_full = df['Query'].tolist()

# --- Create a grouped bar chart for Spill (HDFS vs MinIO) ---
fig = go.Figure()
fig.add_trace(go.Bar(
    x=labels_short,
    y=df['HDFS_Spill(GiB)'],
    name='HDFS Spill (GiB)',
    marker_color='orange',
    hovertext=labels_full,
    hovertemplate='Query %{hovertext}<br>HDFS: %{y:.2f} GiB<extra></extra>'
))
fig.add_trace(go.Bar(
    x=labels_short,
    y=df['MinIO_Spill(GiB)'],
    name='MinIO Spill (GiB)',
    marker_color='green',
    hovertext=labels_full,
    hovertemplate='Query %{hovertext}<br>MinIO: %{y:.2f} GiB<extra></extra>'
))

# --- Set chart layout and appearance ---
fig.update_layout(
    title="Spill (GiB) HDFS vs MinIO",
    xaxis=dict(tickvals=labels_short, ticktext=labels_short),
    yaxis_title="GiB",
    barmode='group',
    legend=dict(x=1, y=1)
)

# --- Output: save chart as HTML file in .generated_files/spill_files/ ---
output_dir = os.path.join(base_dir, ".generated_files", "spill_files")
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, "spill.html")
fig.write_html(filepath)
