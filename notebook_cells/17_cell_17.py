# --- Step 9: Evaluation ---
def get_predictions(loader):
    model.eval()
    all_p, all_a = [], []
    with torch.no_grad():
        for batch in loader:
            out = model(
                past_values=batch['past_values'].to(device),
                past_time_features=batch['past_time_features'].to(device),
                past_observed_mask=torch.ones(batch['past_values'].shape).to(device),
                future_values=batch['future_values'].to(device),
                future_time_features=batch['future_time_features'].to(device),
                future_observed_mask=torch.ones(batch['future_values'].shape).to(device),
                future_ohlc=batch['future_ohlc'].to(device),
            )
            all_p.append(out.ohlc.cpu().numpy())
            all_a.append(batch['future_ohlc'].cpu().numpy())
    return np.concatenate(all_p, axis=0).reshape(-1, 4), np.concatenate(all_a, axis=0).reshape(-1, 4)
def scale_back(p, a):
    p, a = p.copy(), a.copy()
    for i in range(4):
        p[:, i:i+1] = scaler_close.inverse_transform(p[:, i:i+1])
        a[:, i:i+1] = scaler_close.inverse_transform(a[:, i:i+1])
    return p, a
print('Getting predictions...')
ps, ac = get_predictions(test_dataloader)
p, a = scale_back(ps, ac)
cp, ca = p[:, 3], a[:, 3]
print(f'=== Test (Close) ===')
print(f'RMSE: {np.sqrt(np.mean((cp-ca)**2)):.6f}')
print(f'MAE: {np.mean(np.abs(cp-ca)):.6f}')
print(f'MAPE: {np.mean(np.abs((ca-cp)/(ca+1e-8)))*100:.2f}%')
print(f'Direction Acc: {np.mean(np.sign(np.diff(cp))==np.sign(np.diff(ca)))*100:.1f}%')
print(f'\nOHLC RMSE:')
for i,n in enumerate(['Open','High','Low','Close']):
    print(f'  {n}: {np.sqrt(np.mean((p[:,i]-a[:,i])**2)):.6f}')
print('Done.')
