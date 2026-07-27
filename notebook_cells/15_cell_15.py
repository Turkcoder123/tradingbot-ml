# --- Step 8: Training ---
SPREAD_POINTS = 0.0001
COMMISSION_RATE = 0.00002
optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
ohlc_loss_fn = nn.MSELoss()
best_val_loss = float('inf')
patience_counter = 0
for epoch in range(EPOCHS):
    model.train()
    tr_sum = 0.0; ohlc_sum = 0.0; n = 0
    for batch in train_dataloader:
        optimizer.zero_grad()
        out = model(
            past_values=batch['past_values'].to(device),
            past_time_features=batch['past_time_features'].to(device),
            past_observed_mask=torch.ones(batch['past_values'].shape).to(device),
            future_values=batch['future_values'].to(device),
            future_time_features=batch['future_time_features'].to(device),
            future_observed_mask=torch.ones(batch['future_values'].shape).to(device),
            future_ohlc=batch['future_ohlc'].to(device),
        )
        ohlc_loss = ohlc_loss_fn(out.ohlc, batch['future_ohlc'].to(device))
        (out.loss + ohlc_loss).backward()
        optimizer.step()
        tr_sum += out.loss.item() + ohlc_loss.item()
        ohlc_sum += ohlc_loss.item()
        n += 1
    avg_train = tr_sum / n
    avg_ohlc = ohlc_sum / n
    model.eval()
    val_sum = 0.0; vn = 0
    with torch.no_grad():
        for batch in val_dataloader:
            out = model(
                past_values=batch['past_values'].to(device),
                past_time_features=batch['past_time_features'].to(device),
                past_observed_mask=torch.ones(batch['past_values'].shape).to(device),
                future_values=batch['future_values'].to(device),
                future_time_features=batch['future_time_features'].to(device),
                future_observed_mask=torch.ones(batch['future_values'].shape).to(device),
                future_ohlc=batch['future_ohlc'].to(device),
            )
            val_sum += ohlc_loss_fn(out.ohlc, batch['future_ohlc'].to(device)).item()
            vn += 1
    avg_val = val_sum / vn
    print(f'Epoch {epoch+1}/{EPOCHS} - Train: {avg_train:.6f} (OHLC: {avg_ohlc:.6f}) | Val OHLC: {avg_val:.6f}')
    if avg_val < best_val_loss:
        best_val_loss = avg_val; patience_counter = 0
        torch.save(model.state_dict(), 'best_model_multi_output.pth')
        print(f'  -> Best model! Loss: {best_val_loss:.6f}')
    else:
        patience_counter += 1
        if patience_counter >= PATIENCE:
            print(f'Early stopping at epoch {epoch+1}'); break
print('Training done!')
