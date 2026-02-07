# Mining Wallet Integration Guide

## Overview

The GhostShell Mining System now includes a complete wallet management system with USD exchange integration and withdrawal capabilities. This guide covers all features and operations.

---

## System Components

### 1. **Wallet Manager** (`wallet_manager.py`)
- Core wallet functionality
- Mining reward deposits
- Withdrawal management
- USD exchange rate integration
- Transaction history tracking

### 2. **Mining Control** (`mining_control`)
- Start/stop mining operations
- Interactive control center
- Wallet balance queries
- Manual fund deposits/withdrawals

### 3. **Wallet API Server** (`wallet_api_server.py`)
- REST API for wallet operations
- Real-time dashboard
- JSON endpoints for integration
- USD exchange rate tracking

---

## Quick Start

### Start the Mining System with Wallet

```bash
# Interactive control center
./mining_control

# Or use commands directly
./mining_control start          # Start mining
./mining_control balance        # Check balance
./mining_control stop           # Stop mining
```

### Start the Wallet API Server

```bash
# Run on localhost:9004
python3 wallet_api_server.py

# Or specify custom host/port
python3 wallet_api_server.py --host 0.0.0.0 --port 9004
```

Access the wallet dashboard at: `http://localhost:9004`

---

## Mining Control Commands

### Start/Stop Operations

```bash
# Start mining with wallet
./mining_control start

# Check mining status
./mining_control status

# Stop mining gracefully
./mining_control stop
```

### Wallet Operations

```bash
# View wallet balance with USD conversion
./mining_control balance

# Deposit mining rewards manually
./mining_control deposit 0.5

# Request withdrawal
./mining_control withdraw 0.1 0x1234567890abcdef ethereum

# Confirm withdrawal with TX hash
./mining_control confirm <withdrawal_id> 0xabcd1234...

# View transaction history
./mining_control history 20
```

### Exchange Rates

```bash
# Get current Bitcoin to USD rate
./mining_control exchange bitcoin

# Get Ethereum to USD rate
./mining_control exchange ethereum
```

---

## Wallet API Endpoints

### GET Endpoints

#### Get Wallet Status
```bash
curl http://localhost:9004/api/wallet/status
```

Response:
```json
{
  "status": "success",
  "data": {
    "wallet_id": "abc123def456",
    "status": "active",
    "balances": {
      "total_mined": 2.5,
      "pooled_balance": 2.3,
      "available_balance": 2.3,
      "withdrawn_total": 0.2,
      "pending_withdrawals": 0
    },
    "usd_values": {
      "total_mined_usd": 95000.00,
      "pooled_balance_usd": 87400.00,
      "available_balance_usd": 87400.00,
      "withdrawn_total_usd": 7600.00,
      "btc_exchange_rate": 38000.00
    },
    "transactions_count": 5,
    "last_updated": "2026-02-07T16:30:00Z"
  }
}
```

#### Get Current Balance
```bash
curl http://localhost:9004/api/wallet/balance
```

#### Get Transaction History
```bash
curl http://localhost:9004/api/wallet/transactions?limit=50
```

#### Get USD Exchange Rate
```bash
# Bitcoin rate
curl http://localhost:9004/api/exchange/rate?crypto=bitcoin

# Ethereum rate
curl http://localhost:9004/api/exchange/rate?crypto=ethereum
```

Response:
```json
{
  "status": "success",
  "data": {
    "crypto": "bitcoin",
    "rate_usd": 38000.00,
    "timestamp": "2026-02-07T16:30:00Z"
  }
}
```

### POST Endpoints

#### Deposit Mining Rewards
```bash
curl -X POST http://localhost:9004/api/wallet/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 0.5,
    "source": "mining_cycle_45"
  }'
```

#### Request Withdrawal
```bash
curl -X POST http://localhost:9004/api/wallet/withdraw \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 0.1,
    "address": "0x1234567890abcdef",
    "address_type": "ethereum"
  }'
```

Response:
```json
{
  "status": "pending",
  "withdrawal": {
    "id": "w123456789",
    "timestamp": "2026-02-07T16:30:00Z",
    "amount": 0.1,
    "address": "0x1234567890abcdef",
    "address_type": "ethereum",
    "status": "pending",
    "confirmations": 0
  },
  "message": "Withdrawal requested. Please confirm the transaction."
}
```

#### Confirm Withdrawal
```bash
curl -X POST http://localhost:9004/api/wallet/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "withdrawal_id": "w123456789",
    "tx_hash": "0xabcd1234efgh5678ijkl"
  }'
```

---

## Wallet Data Structure

### Wallet File (`wallets/mining_wallet.json`)

```json
{
  "wallet_id": "abc123def456",
  "created_at": "2026-02-07T10:00:00Z",
  "total_mined": 2.5,
  "pooled_balance": 2.3,
  "available_balance": 2.3,
  "withdrawn_total": 0.2,
  "pending_withdrawals": [],
  "transactions": [
    {
      "timestamp": "2026-02-07T10:00:01Z",
      "type": "WALLET_CREATED",
      "amount": 0.0,
      "source": "system"
    },
    {
      "timestamp": "2026-02-07T10:05:00Z",
      "type": "DEPOSIT",
      "amount": 0.5,
      "source": "mining_cycle_1"
    }
  ],
  "currency": "USD",
  "status": "active"
}
```

### Transaction Types

- `WALLET_CREATED` - Wallet initialization
- `DEPOSIT` - Mining rewards deposited
- `WITHDRAWAL_REQUEST` - Withdrawal requested
- `WITHDRAWAL_CONFIRMED` - Withdrawal confirmed with TX
- `WITHDRAWAL_FAILED` - Withdrawal failed

---

## USD Exchange Integration

### Supported Cryptocurrencies

- `bitcoin` - BTC
- `ethereum` - ETH
- `litecoin` - LTC
- `ripple` - XRP
- `cardano` - ADA

### Exchange Rate API

The system uses the **CoinGecko API** (free, no key required) for real-time USD exchange rates.

**Features:**
- Automatic caching (5-minute cache)
- Fallback to cached rates if API unavailable
- No rate limiting
- Real-time updates

### Getting Exchange Rates

```bash
# Via CLI
./mining_control exchange bitcoin

# Via API
curl http://localhost:9004/api/exchange/rate?crypto=ethereum

# Via Python
from wallet_manager import WalletManager
manager = WalletManager()
rate = manager.get_usd_exchange_rate("bitcoin")
usd_value = manager.calculate_usd_value(1.5, "bitcoin")
```

---

## Withdrawal Process

### Step 1: Request Withdrawal

```bash
./mining_control withdraw 0.1 0x1234567890abcdef ethereum
```

This will:
1. Deduct from available balance
2. Create pending withdrawal record
3. Return withdrawal ID

### Step 2: Send to Blockchain

Use your wallet software to send the crypto to the requested address.

Example output:
```
Status: pending
Withdrawal ID: w123456789
Amount: 0.1 BTC
Address: 0x1234567890abcdef
```

### Step 3: Confirm Withdrawal

Once blockchain confirms, confirm the withdrawal:

```bash
./mining_control confirm w123456789 0xabcd1234efgh5678ijkl
```

This will:
1. Mark withdrawal as confirmed
2. Update transaction history
3. Record blockchain TX hash
4. Complete the withdrawal

---

## Mining Integration

### Automatic Wallet Deposits

When mining is running, the system automatically deposits rewards:

```bash
# Mining starts
./mining_control start

# Rewards are automatically deposited to wallet
# View with:
./mining_control balance
```

### Manual Deposits

For testing or manual deposits:

```bash
./mining_control deposit 0.05 --source "manual_test"
```

---

## Dashboard Features

### Web Dashboard (`http://localhost:9004`)

**Displays:**
- Total mined BTC and USD value
- Current available balance
- Withdrawn total
- Pending withdrawals count
- Real-time BTC/USD exchange rate
- Transaction count
- All API endpoints

**Auto-refreshes every 30 seconds**

### Features:
- Real-time balance updates
- USD value conversion
- Exchange rate display
- Transaction tracking
- API documentation

---

## Security Considerations

### Wallet Storage

```
wallets/
├── mining_wallet.json     # Main wallet file (encrypted recommended)
├── transactions.log       # Transaction history
└── .exchange_cache.json   # Exchange rate cache
```

### Best Practices

1. **Backup Regularly**
   ```bash
   cp -r wallets/ wallets_backup_$(date +%Y%m%d)
   ```

2. **Verify Addresses**
   - Always double-check withdrawal addresses
   - Use address verification before confirming
   - Test with small amounts first

3. **Monitor Transactions**
   ```bash
   ./mining_control history 100  # View detailed history
   ```

4. **Secure API Access**
   - Run wallet API on internal network only
   - Use firewall rules to restrict access
   - Consider adding authentication for production

---

## Troubleshooting

### Exchange Rate Not Updating

```bash
# Check exchange cache
cat wallets/.exchange_cache.json

# Force refresh by deleting cache
rm wallets/.exchange_cache.json

# Re-check rate
./mining_control exchange bitcoin
```

### Wallet File Corrupted

```bash
# Restore from backup
cp wallets_backup_YYYYMMDD/mining_wallet.json wallets/mining_wallet.json

# Or reinitialize
rm wallets/mining_wallet.json
./mining_control init
```

### API Server Issues

```bash
# Check if port 9004 is in use
lsof -i :9004

# Use different port
python3 wallet_api_server.py --port 9005
```

### Failed Withdrawal

```bash
# Check pending withdrawals
./mining_control balance

# View all transactions
./mining_control history 50

# Resubmit withdrawal if blockchain not confirmed
./mining_control withdraw <amount> <address>
```

---

## Performance Metrics

### System Specifications

- **Wallet Size**: ~1 KB per transaction
- **Exchange Rate Cache**: <10 KB
- **API Response Time**: <500ms
- **Database Operations**: <100ms

### Scaling

- Supports unlimited transactions
- Multiple wallet support (future)
- High-frequency API access

---

## Integration Examples

### Python Integration

```python
from wallet_manager import WalletManager

# Initialize manager
manager = WalletManager()

# Get balance
summary = manager.get_wallet_summary()
print(f"Available: {summary['balances']['available_balance']} BTC")
print(f"USD Value: ${summary['usd_values']['available_balance_usd']:.2f}")

# Deposit reward
result = manager.deposit_mining_reward(0.01, "mining_cycle_100")
print(f"Deposited: {result['transaction']['amount']} BTC")

# Request withdrawal
withdrawal = manager.request_withdrawal(0.01, "0xaddress", "ethereum")
print(f"Withdrawal ID: {withdrawal['withdrawal']['id']}")

# Confirm withdrawal
confirmed = manager.confirm_withdrawal(withdrawal_id, tx_hash)
print(f"Status: {confirmed['status']}")
```

### Bash Integration

```bash
#!/bin/bash

# Get balance programmatically
balance=$(./mining_control balance 2>/dev/null | grep "Available Balance" | awk '{print $NF}')

# Check if balance exceeds threshold
if (( $(echo "$balance > 0.5" | bc -l) )); then
    echo "Balance threshold reached! Initiating withdrawal..."
    ./mining_control withdraw 0.5 $WITHDRAWAL_ADDRESS ethereum
fi
```

### API Integration

```bash
#!/bin/bash

# Check wallet status via API
status=$(curl -s http://localhost:9004/api/wallet/status | jq '.data.balances.available_balance')

# Auto-withdrawal when balance exceeds 1 BTC
if (( $(echo "$status > 1.0" | bc -l) )); then
    curl -X POST http://localhost:9004/api/wallet/withdraw \
      -H "Content-Type: application/json" \
      -d "{\"amount\": 1.0, \"address\": \"$ADDR\", \"address_type\": \"ethereum\"}"
fi
```

---

## File Structure

```
Anti4/
├── wallet_manager.py              # Core wallet system
├── wallet_api_server.py           # REST API server
├── mining_control                 # CLI control interface
├── mine.sh                        # Mining orchestrator
├── wallets/
│   ├── mining_wallet.json        # Wallet data
│   ├── transactions.log          # Transaction log
│   └── .exchange_cache.json      # Exchange rate cache
└── logs/
    ├── mining_active.log         # Mining logs
    ├── mining.log               # Mining details
    └── wallet_api.log           # API logs (optional)
```

---

## Support & Documentation

### Quick Links

- **Dashboard**: http://localhost:9004
- **Control Center**: `./mining_control help`
- **CLI Help**: `./mining_control --help`
- **API Docs**: View at dashboard

### Commands Reference

```bash
./mining_control start                              # Start mining
./mining_control stop                               # Stop mining
./mining_control status                             # Check status
./mining_control balance                            # View balance
./mining_control deposit 0.1                        # Deposit funds
./mining_control withdraw 0.1 <addr> ethereum       # Request withdrawal
./mining_control confirm <id> <tx_hash>             # Confirm withdrawal
./mining_control history 20                         # View transactions
./mining_control exchange bitcoin                   # Get exchange rate
```

---

**Version**: 2.0  
**Status**: Production Ready  
**Last Updated**: February 7, 2026
