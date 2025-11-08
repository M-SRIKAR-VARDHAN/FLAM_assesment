"""
Diagnostic script to visualize the raw (x, y) data points
and check the implicit assumption of sequential ordering in 't'.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuration ---
T_MIN = 6
T_MAX = 60

# Load data
try:
    # Attempt to load the actual data file
    data = pd.read_csv('xy_data.csv')
    x_data = data['x'].values
    y_data = data['y'].values
    print("Successfully loaded 'xy_data.csv'.")
except FileNotFoundError:
    print("Error: 'xy_data.csv' not found. Generating placeholder data for demonstration.")
    # Placeholder: Generate ordered data (Index should map smoothly to position)
    t_test = np.linspace(T_MIN, T_MAX, 500)
    theta_true = 25
    M_true = 0.015
    X_true = 50
    x_data, y_data = (
        t_test * np.cos(np.deg2rad(theta_true)) + X_true,
        42 + t_test * np.sin(np.deg2rad(theta_true))
    )
    x_data += np.random.normal(0, 0.5, size=t_test.shape)
    y_data += np.random.normal(0, 0.5, size=t_test.shape)
    data_loaded = False
else:
    data_loaded = True

N = len(x_data)
indices = np.arange(N)

# Create the plot
plt.figure(figsize=(10, 8))

# Scatter plot where color indicates the index/order of the point
# Points start as deep blue (low index) and fade to yellow/red (high index)
scatter = plt.scatter(
    x_data, 
    y_data, 
    c=indices, 
    cmap='viridis', 
    s=20, 
    alpha=0.8
)
plt.title(f'Raw Data Scatter Plot (N={N} points)\nColor indicates index (order in CSV)', fontsize=14)
plt.xlabel('X Coordinate', fontsize=12)
plt.ylabel('Y Coordinate', fontsize=12)
plt.axis('equal') # Keep aspect ratio for spatial analysis

# Add color bar to show index mapping
cbar = plt.colorbar(scatter, label='Data Index (i)')

# If the data is small, optionally label every N/10th point to check continuity
if N < 200:
    for i in range(0, N, max(1, N//10)):
        plt.annotate(str(i), (x_data[i], y_data[i]), fontsize=8, alpha=0.7, ha='center')

plt.grid(True, linestyle='--', alpha=0.5)

# Save the visualization
try:
    plt.savefig('data_visualization.png', dpi=300, bbox_inches='tight')
    print("✓ Visualization saved to data_visualization.png.")
except Exception:
    print("Warning: Could not save visualization file. Skipping save.")

print("\n" + "="*60)
print("VISUALIZATION GENERATED!")
print("="*60)
print("NEXT STEP: Analyze the 'data_visualization.png' image.")