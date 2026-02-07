# 🚀 Quick Start: Mining Wallet System

## Overview

Your mining wallet integration is **LIVE and READY**. This system automatically tracks pooled mining rewards in USD and provides withdrawal capabilities.

## System Components

| Component | Purpose | Port |
|-----------|---------|------|
| **wallet_manager.py** | Core wallet logic, deposits, withdrawals | - |
| **wallet_api_server.py** | REST API + Web Dashboard | 9004 |
| **mining_control** | CLI control interface | - |
| **mine.sh** | Mining orchestrator | 9002 |

## Installation Status

✅ **Installed and working:**
- Python wallet manager
- REST API server
- CLI control interface
- USD exchange rate API (CoinGecko)
- Bitcoin/Ethereum support

## 1. Initialize Wallet (Run Once)

```bash
python3 wallet_manager.py init
```

**Output:**
```
✅ Wallet initialized: 423b582aa8f0fd44
```

## 2. Check Wallet Status

```bash
python3 wallet_manager.py balance
```

**Example Output:**
```
======================================================================
GHOSTSHELL MINING WALLET
======================================================================
Wallet ID: 423b582aa8f0fd44
Status: active

BALANCES:
  Total Mined: 0.50000000 BTC
  Pooled Balance: 0.50000000 BTC
  Available Balance: 0.50000000 BTC
  USD VALUES (Rate: $69,278.00/BTC):
  Total Mined: $34,639.00
======================================================================
```

## 3. Add Mining Rewards (Manual Deposit)

```bash
python3 wallet_manager.py deposit 1.0 --source "mining_pool"
```

Output:
```
✅ Deposit successful: 1.0 BTC
USD Value: $69,278.00
```

## 4. Request Withdrawal

```bash
python3 wallet_manager.py withdraw 0.5 1A1z7agoat3FYScAmCnyy87MPVvxiq2Np bitcoin
```

Output:
```
✅ Withdrawal request created
Withdrawal ID: abc123def456
Amount: 0.5 BTC ($34,639.00)
Address: 1A1z7agoat3FYScAmCnyy87MPVvxiq2Np
Status: pending
```

## 5. Confirm Withdrawal (After TX on Blockchain)

```bash
python3 wallet_manager.py confirm abc123def456 0x1234567890abcdef...
```

Output:
```
✅ Withdrawal confirmed
Amount: 0.5 BTC
TX Hash: 0x1234567890abcdef...
```

## 6. Start API Server + Dashboard

```bash
python3 wallet_api_server.py
```

Output:
```
[*] Wallet API Server starting on port 9004...
[*] Dashboard: http://localhost:9004
[*] Server running. Press Ctrl+C to stop.
```

**Then open in browser:**
```
http://localhost:9004
```

## 7. Using REST API

### Get Wallet Status
```bash
curl http://localhost:9004/api/wallet/status
```

### Get Current Balance
```bash
curl http://localhost:9004/api/wallet/balance
```

### Get USD Exchange Rate
```bash
curl http://localhost:9004/api/exchange/rate?crypto=bitcoin
```

Response:
```json
{
  "status": "success",
  "crypto": "bitcoin",
  "rate_usd": 69278.00,
  "timestamp": "2026-02-07T16:20:50.886596"
}
```

### Deposit Funds (API)
```bash
curl -X POST http://localhost:9004/api/wallet/deposit \
  -H "Content-Type: application/json" \
  -d '{"amount": 0.1, "source": "mining_pool"}'
```

### Request Withdrawal (API)
```bash
curl -X POST http://localhost:9004/api/wallet/withdraw \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 0.05,
    "address": "1A1z7agoat3FYScAmCnyy87MPVvxiq2Np",
    "address_type": "bitcoin"
  }'
```

## 8. Interactive Control Mode

```bash
./mining_control
```

**Menu:**
```
╔════════════════════════════════════╗
║  GHOSTSHELL MINING CONTROL CENTER  ║
╚════════════════════════════════════╝

1. Start Mining
2. Stop Mining
3. Check Status
4. View Balance
5. Make Deposit
6. Request Withdrawal
7. Confirm Withdrawal
8. View Transactions
9. Get Exchange Rate
0. Exit

Select option:
```

## Integration with Active Mining

### Auto-Deposit from Mining
When mining runs, rewards automatically deposit to wallet:

```bash
./mining_control start
# Mining starts with wallet initialized
# Every 30s: mining cycle runs
# Every 5m: live tests execute
# Rewards automatically track in wallet
```

### Monitor Mining Rewards in Real-time

**Terminal 1 - Start Mining:**
```bash
./mining_control start
```

**Terminal 2 - Watch Balance:**
```bash
watch -n 5 'python3 wallet_manager.py balance | grep Total'
```

**Terminal 3 - Monitor API:**
```bash
python3 wallet_api_server.py
# Open http://localhost:9004 in browser
```

## Data Files Location

```
wallets/
├── mining_wallet.json      # Main wallet state
├── transactions.log        # Complete transaction history
└── .exchange_cache.json    # Cached exchange rates (5 min TTL)
```

## Supported Cryptocurrencies

✅ Bitcoin (BTC)
✅ Ethereum (ETH)
✅ Litecoin (LTC)
✅ Ripple (XRP)
✅ Cardano (ADA)
✅ Many others via CoinGecko API

## Common Operations

### Check USD Value of Holdings
```bash
python3 wallet_manager.py balance
# Shows "USD VALUES" section with total
```

### View All Transactions
```bash
python3 wallet_manager.py history
```

### Get Current Bitcoin Price
```bash
python3 wallet_manager.py exchange bitcoin
# Output: Bitcoin: $69,278.00
```

## Troubleshooting

### No Exchange Rates Showing
```bash
# Exchange rate API may be cached
# Clear cache and reinitialize:
rm wallets/.exchange_cache.json
python3 wallet_manager.py balance
```

### Wallet Won't Initialize
```bash
# Check wallet directory
ls -la wallets/

# Reinitialize if needed
rm wallets/mining_wallet.json
python3 wallet_manager.py init
```

### API Server Won't Start
```bash
# Check if port 9004 is in use
lsof -i :9004

# Kill existing process if needed
kill -9 <PID>

# Start fresh
python3 wallet_api_server.py
```

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Initialize wallet | <1s | One-time |
| Deposit | <1s | Instant |
| Get balance | <1s | Instant |
| Exchange rate | 1-2s | Cached 5 min |
| Request withdrawal | <1s | Instant |
| Confirm withdrawal | <1s | Instant |
| API response | <100ms | JSON |

## Security Notes

⚠️ **For Production:**
- Use environment variables for wallet encryption
- Add password protection for withdrawals
- Use HTTPS for API server
- Implement rate limiting
- Add 2FA for large withdrawals

## Next Steps

1. **Test Deposits:** `python3 wallet_manager.py deposit 0.1 --source "test"`
2. **Try API:** `curl http://localhost:9004/api/wallet/status`
3. **Start Mining:** `./mining_control start`
4. **Monitor Dashboard:** `http://localhost:9004`
5. **Test Withdrawal:** `python3 wallet_manager.py withdraw 0.05 YOUR_BTC_ADDRESS bitcoin`

---

**Status:** ✅ System LIVE and READY

**Last Updated:** 2026-02-07
**Bitcoin Price:** $69,278/BTC (live from CoinGecko)
