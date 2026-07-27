# --- Step 8: Train the Multi-Output Model with Validation and Early Stopping ---
# Hyperparameters for spread/commission awareness
SPREAD_POINTS = 0.0001  # Typical EURUSD spread (~1 pip)
COMMISSION_RATE = 0.00002  # 0.002% commission

optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
best_val_loss = float('inf')
patience_counter = 0

for epoch in trange(EPOCHS, desc="Epoch"):
    # --- Training Phase ---
    model.train()
    train_loss_total = 0
    progress_bar_train = tqdm(train_dataloader, desc=f"Training Epoch {epoch+1}", leave=False)
    for batch in progress_bar_train:
        optimizer.zero_grad()
        past_values = batch['past_values'].to(device)  # [batch, context_len] - Close only
        future_values = batch['future_values'].to(device)  # [batch, pred_len, 4] - O,H,L,C
        past_time_features = batch['past_time_features'].to(device)
        future_time_features = batch['future_time_features'].to(device)
        past_observed_mask = torch.ones_like(past_values).to(device)
        future_observed_mask = torch.ones_like(future_values[:, :, 0]).to(device)  # Mask for Close

        outputs = model(
            past_values=past_values,
            past_time_features=past_time_features,
            past_observed_mask=past_observed_mask,
            future_values=future_values,
            future_time_features=future_time_features,
            future_observed_mask=future_observed_mask,
        )
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        train_loss_total += loss.item()
        progress_bar_train.set_postfix({"loss": f"{loss.item():.8f}"})

    avg_train_loss = train_loss_total / len(train_dataloader)

    # --- Validation Phase ---
    model.eval()
    val_loss_total = 0
    with torch.no_grad():
        for batch in tqdm(val_dataloader, desc=f"Validating Epoch {epoch+1}", leave=False):
            past_values = batch['past_values'].to(device)
            future_values = batch['future_values'].to(device)
            past_time_features = batch['past_time_features'].to(device)
            future_time_features = batch['future_time_features'].to(device)
            past_observed_mask = torch.ones_like(past_values).to(device)
            future_observed_mask = torch.ones_like(future_values[:, :, 0]).to(device)

            outputs = model(
                past_values=past_values,
                past_time_features=past_time_features,
                past_observed_mask=past_observed_mask,
                future_values=future_values,
                future_time_features=future_time_features,
                future_observed_mask=future_observed_mask,
            )
            val_loss_total += outputs.loss.item()

    avg_val_loss = val_loss_total / len(val_dataloader)

    print(f"\nEpoch {epoch+1}/{EPOCHS} - Train Loss: {avg_train_loss:.8f}, Val Loss: {avg_val_loss:.8f}")

    # Early stopping check
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        patience_counter = 0
        # Save best model
        torch.save(model.state_dict(), 'best_model_multi_output.pth')
        print(f"New best model saved! Val Loss: {best_val_loss:.8f}")
    else:
        patience_counter += 1
        if patience_counter >= PATIENCE:
            print(f"Early stopping triggered at epoch {epoch+1}")
            break

print("Training completed!")
