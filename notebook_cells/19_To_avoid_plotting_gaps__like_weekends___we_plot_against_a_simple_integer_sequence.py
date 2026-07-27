# --- Step 10: Visualize Predictions (Corrected for Non-Continuous Time Series) ---
# To avoid plotting gaps (like weekends), we plot against a simple integer sequence
# and then format the x-axis ticks with the corresponding dates. This matches the
# "Gaps Collapsed" approach from the LSTM project.

import matplotlib.dates as mdates

def plot_subset_collapsed(dates, y_true, y_pred, title, subset_size=1000,
                          true_color='royalblue', pred_color='skyblue'):
    """
    Helper function to plot the last N points of a dataset against an integer index,
    collapsing time gaps and adding date labels.
    """
    plt.figure(figsize=(20, 7))

    # Ensure we don't plot more data than we have
    plot_size = min(subset_size, len(dates))

    # Use an integer sequence for the x-axis
    x_axis_index = np.arange(plot_size)

    plt.plot(x_axis_index, y_true[-plot_size:], color=true_color,
             label=f'Actual {title.split(" ")[0]} Price', marker='.', markersize=2, alpha=0.7)
    plt.plot(x_axis_index, y_pred[-plot_size:], color=pred_color,
             label=f'Predicted {title.split(" ")[0]} Price', linestyle='--')

    plt.title(f'{title}: Actual vs. Predicted (Last {plot_size} Points) - Gaps Collapsed', fontsize=16)
    plt.xlabel('Trading Sequence Point (Time Gaps Collapsed)', fontsize=12)
    plt.ylabel('EURUSD Price', fontsize=12)
    plt.legend()
    plt.grid(True)

    # Format the x-axis ticks to show dates
    # We select a few points from our index and label them with the corresponding date
    num_ticks = 7
    tick_indices = np.linspace(0, plot_size - 1, num_ticks, dtype=int)
    tick_labels = [dates[-plot_size:][i].strftime('%Y-%m-%d\n%H:%M') for i in tick_indices]

    plt.xticks(ticks=tick_indices, labels=tick_labels, rotation=30, ha='right')
    plt.tight_layout()
    plt.show()

# --- Plot subsets for clarity ---
plot_subset_collapsed(train_dates, y_true_train, y_pred_train, title='Training Set', true_color='royalblue', pred_color='skyblue')
plot_subset_collapsed(val_dates, y_true_val, y_pred_val, title='Validation Set', true_color='forestgreen', pred_color='lightgreen')
plot_subset_collapsed(test_dates, y_true_test, y_pred_test, title='Test Set', true_color='red', pred_color='darkorange')


# --- Plot 4: Test Set - Scaled (This plot does not need dates, so it's fine as is) ---
# We need to get the scaled true and predicted values for the test set
y_pred_test_scaled = target_scaler.transform(y_pred_test.reshape(-1, 1))
y_true_test_scaled = target_scaler.transform(y_true_test.reshape(-1, 1))

plt.figure(figsize=(20, 7))
plt.plot(y_true_test_scaled, color='blue', label='Actual Test Price (Scaled)')
plt.plot(y_pred_test_scaled, color='lime', label='Predicted Test Price (Scaled)', linestyle='--')
plt.title('Test Set: Actual vs. Predicted EURUSD Price (Scaled)', fontsize=16)
plt.xlabel(f'Time Step (Windowed Test Set)')
plt.ylabel('Scaled Price')
plt.legend()
plt.grid(True)
plt.show()