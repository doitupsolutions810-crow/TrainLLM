#!/usr/bin/env python3

"""
GhostShell Mining Wallet Manager
Manages mining rewards, pools, balances, and withdrawals with USD conversion
"""

import json
import os
import sys
import ssl
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error
import hashlib
import hmac

class WalletManager:
    """Manage mining wallet, funds, and withdrawals"""
    
    def __init__(self, wallet_dir: str = "wallets"):
        self.wallet_dir = Path(wallet_dir)
        self.wallet_dir.mkdir(exist_ok=True)
        self.wallet_file = self.wallet_dir / "mining_wallet.json"
        self.transactions_file = self.wallet_dir / "transactions.log"
        self.exchange_cache_file = self.wallet_dir / ".exchange_cache.json"
        self.last_exchange_update = 0
        self.exchange_cache = {}
        self.load_exchange_cache()
        
    def initialize_wallet(self, wallet_id: str = None) -> dict:
        """Initialize a new mining wallet"""
        if wallet_id is None:
            wallet_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]
        
        wallet = {
            "wallet_id": wallet_id,
            "created_at": datetime.utcnow().isoformat(),
            "total_mined": 0.0,
            "pooled_balance": 0.0,
            "available_balance": 0.0,
            "withdrawn_total": 0.0,
            "pending_withdrawals": [],
            "transactions": [],
            "currency": "USD",
            "status": "active"
        }
        
        self.save_wallet(wallet)
        self.log_transaction(wallet_id, "WALLET_CREATED", 0, "Wallet initialized")
        return wallet
    
    def load_wallet(self, wallet_id: str = None) -> dict:
        """Load wallet from file"""
        if self.wallet_file.exists():
            with open(self.wallet_file, 'r') as f:
                wallet = json.load(f)
                return wallet
        
        # Create new wallet if doesn't exist
        return self.initialize_wallet(wallet_id)
    
    def save_wallet(self, wallet: dict):
        """Save wallet to file"""
        with open(self.wallet_file, 'w') as f:
            json.dump(wallet, f, indent=2)
    
    def deposit_mining_reward(self, amount: float, source: str = "mining_cycle") -> dict:
        """Deposit mined funds to wallet"""
        wallet = self.load_wallet()
        
        wallet["total_mined"] += amount
        wallet["pooled_balance"] += amount
        wallet["available_balance"] += amount
        
        transaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "DEPOSIT",
            "amount": amount,
            "source": source,
            "balance_after": wallet["available_balance"]
        }
        
        wallet["transactions"].append(transaction)
        self.save_wallet(wallet)
        self.log_transaction(wallet["wallet_id"], "DEPOSIT", amount, source)
        
        return {"status": "success", "transaction": transaction}
    
    def get_usd_exchange_rate(self, crypto: str = "bitcoin") -> float:
        """Get current USD exchange rate for crypto"""
        cache_time = datetime.utcnow().timestamp()
        
        # Return cached value if less than 5 minutes old
        if crypto in self.exchange_cache:
            cache_entry = self.exchange_cache[crypto]
            if cache_time - cache_entry.get("timestamp", 0) < 300:
                return cache_entry.get("rate", 0.0)
        
        try:
            # Try CoinGecko API (free, no key required)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            # Create SSL context that doesn't verify (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
                data = json.loads(response.read().decode())
                rate = data.get(crypto, {}).get("usd", 0.0)
                
                # Cache the result
                self.exchange_cache[crypto] = {
                    "rate": rate,
                    "timestamp": cache_time
                }
                self.save_exchange_cache()
                return rate
        
        except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
            print(f"[ERROR] Failed to fetch exchange rate: {e}")
            # Return last known rate from cache
            if crypto in self.exchange_cache:
                return self.exchange_cache[crypto].get("rate", 0.0)
            return 0.0
    
    def calculate_usd_value(self, amount: float, crypto: str = "bitcoin") -> float:
        """Calculate USD value of mined crypto"""
        rate = self.get_usd_exchange_rate(crypto)
        return amount * rate
    
    def load_exchange_cache(self):
        """Load exchange rate cache from file"""
        if self.exchange_cache_file.exists():
            try:
                with open(self.exchange_cache_file, 'r') as f:
                    self.exchange_cache = json.load(f)
            except:
                self.exchange_cache = {}
    
    def save_exchange_cache(self):
        """Save exchange rate cache to file"""
        with open(self.exchange_cache_file, 'w') as f:
            json.dump(self.exchange_cache, f, indent=2)
    
    def request_withdrawal(self, amount: float, address: str, 
                          address_type: str = "ethereum") -> dict:
        """Request a withdrawal of funds"""
        wallet = self.load_wallet()
        
        # Validate withdrawal amount
        if amount <= 0:
            return {"status": "error", "message": "Amount must be positive"}
        
        if amount > wallet["available_balance"]:
            return {"status": "error", 
                   "message": f"Insufficient balance. Available: {wallet['available_balance']}"}
        
        withdrawal = {
            "id": hashlib.md5(f"{datetime.utcnow()}{amount}{address}".encode()).hexdigest()[:16],
            "timestamp": datetime.utcnow().isoformat(),
            "amount": amount,
            "address": address,
            "address_type": address_type,
            "status": "pending",
            "confirmations": 0
        }
        
        # Deduct from available balance (keep in pooled until confirmed)
        wallet["available_balance"] -= amount
        wallet["pending_withdrawals"].append(withdrawal)
        
        self.save_wallet(wallet)
        self.log_transaction(wallet["wallet_id"], "WITHDRAWAL_REQUEST", amount, 
                            f"To {address_type}: {address}")
        
        return {
            "status": "pending",
            "withdrawal": withdrawal,
            "message": "Withdrawal requested. Please confirm the transaction."
        }
    
    def confirm_withdrawal(self, withdrawal_id: str, tx_hash: str) -> dict:
        """Confirm withdrawal with blockchain transaction hash"""
        wallet = self.load_wallet()
        
        withdrawal = None
        for w in wallet["pending_withdrawals"]:
            if w["id"] == withdrawal_id:
                withdrawal = w
                break
        
        if not withdrawal:
            return {"status": "error", "message": "Withdrawal not found"}
        
        withdrawal["status"] = "confirmed"
        withdrawal["tx_hash"] = tx_hash
        withdrawal["confirmed_at"] = datetime.utcnow().isoformat()
        
        # Move from pending to completed
        wallet["withdrawn_total"] += withdrawal["amount"]
        wallet["pending_withdrawals"].remove(withdrawal)
        
        transaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "WITHDRAWAL_CONFIRMED",
            "amount": withdrawal["amount"],
            "tx_hash": tx_hash,
            "balance_after": wallet["available_balance"]
        }
        wallet["transactions"].append(transaction)
        
        self.save_wallet(wallet)
        self.log_transaction(wallet["wallet_id"], "WITHDRAWAL_CONFIRMED", 
                            withdrawal["amount"], f"TX: {tx_hash}")
        
        return {
            "status": "confirmed",
            "withdrawal": withdrawal,
            "message": "Withdrawal confirmed and recorded"
        }
    
    def get_wallet_summary(self) -> dict:
        """Get wallet summary with USD values"""
        wallet = self.load_wallet()
        
        # Calculate USD values
        btc_rate = self.get_usd_exchange_rate("bitcoin")
        
        summary = {
            "wallet_id": wallet["wallet_id"],
            "status": wallet["status"],
            "balances": {
                "total_mined": wallet["total_mined"],
                "pooled_balance": wallet["pooled_balance"],
                "available_balance": wallet["available_balance"],
                "withdrawn_total": wallet["withdrawn_total"],
                "pending_withdrawals": len(wallet["pending_withdrawals"])
            },
            "usd_values": {
                "total_mined_usd": self.calculate_usd_value(wallet["total_mined"]),
                "pooled_balance_usd": self.calculate_usd_value(wallet["pooled_balance"]),
                "available_balance_usd": self.calculate_usd_value(wallet["available_balance"]),
                "withdrawn_total_usd": self.calculate_usd_value(wallet["withdrawn_total"]),
                "btc_exchange_rate": btc_rate
            },
            "transactions_count": len(wallet["transactions"]),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return summary
    
    def log_transaction(self, wallet_id: str, tx_type: str, amount: float, details: str):
        """Log transaction to file"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "wallet_id": wallet_id,
            "type": tx_type,
            "amount": amount,
            "details": details
        }
        
        with open(self.transactions_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_transaction_history(self, limit: int = 50) -> list:
        """Get transaction history"""
        wallet = self.load_wallet()
        return wallet["transactions"][-limit:]
    
    def display_wallet_info(self):
        """Display wallet information"""
        summary = self.get_wallet_summary()
        
        print("\n" + "="*70)
        print("GHOSTSHELL MINING WALLET")
        print("="*70)
        print(f"Wallet ID: {summary['wallet_id']}")
        print(f"Status: {summary['status']}")
        print(f"\nBALANCES:")
        print(f"  Total Mined: {summary['balances']['total_mined']:.8f} BTC")
        print(f"  Pooled Balance: {summary['balances']['pooled_balance']:.8f} BTC")
        print(f"  Available Balance: {summary['balances']['available_balance']:.8f} BTC")
        print(f"  Withdrawn Total: {summary['balances']['withdrawn_total']:.8f} BTC")
        print(f"  Pending Withdrawals: {summary['balances']['pending_withdrawals']}")
        
        print(f"\nUSD VALUES (Rate: ${summary['usd_values']['btc_exchange_rate']:.2f}/BTC):")
        print(f"  Total Mined: ${summary['usd_values']['total_mined_usd']:.2f}")
        print(f"  Pooled Balance: ${summary['usd_values']['pooled_balance_usd']:.2f}")
        print(f"  Available Balance: ${summary['usd_values']['available_balance_usd']:.2f}")
        print(f"  Withdrawn Total: ${summary['usd_values']['withdrawn_total_usd']:.2f}")
        
        print(f"\nTransactions: {summary['transactions_count']}")
        print(f"Last Updated: {summary['last_updated']}")
        print("="*70 + "\n")


def main():
    """CLI interface for wallet management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GhostShell Mining Wallet Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Initialize wallet
    init_parser = subparsers.add_parser('init', help='Initialize wallet')
    init_parser.add_argument('--id', type=str, help='Wallet ID (auto-generated if not provided)')
    
    # Deposit funds
    deposit_parser = subparsers.add_parser('deposit', help='Deposit mining reward')
    deposit_parser.add_argument('amount', type=float, help='Amount to deposit')
    deposit_parser.add_argument('--source', type=str, default='mining_cycle', help='Deposit source')
    
    # Get balance
    balance_parser = subparsers.add_parser('balance', help='Get wallet balance')
    
    # Request withdrawal
    withdraw_parser = subparsers.add_parser('withdraw', help='Request withdrawal')
    withdraw_parser.add_argument('amount', type=float, help='Amount to withdraw')
    withdraw_parser.add_argument('address', type=str, help='Target address')
    withdraw_parser.add_argument('--type', type=str, default='ethereum', help='Address type')
    
    # Confirm withdrawal
    confirm_parser = subparsers.add_parser('confirm', help='Confirm withdrawal')
    confirm_parser.add_argument('withdrawal_id', type=str, help='Withdrawal ID')
    confirm_parser.add_argument('tx_hash', type=str, help='Transaction hash')
    
    # Get exchange rate
    exchange_parser = subparsers.add_parser('exchange', help='Get USD exchange rate')
    exchange_parser.add_argument('--crypto', type=str, default='bitcoin', help='Cryptocurrency')
    
    # History
    history_parser = subparsers.add_parser('history', help='Get transaction history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of transactions')
    
    args = parser.parse_args()
    
    manager = WalletManager()
    
    if args.command == 'init':
        wallet = manager.initialize_wallet(args.id)
        print(f"✅ Wallet initialized: {wallet['wallet_id']}")
        manager.display_wallet_info()
    
    elif args.command == 'deposit':
        result = manager.deposit_mining_reward(args.amount, args.source)
        print(f"✅ Deposit successful: {args.amount} BTC")
        manager.display_wallet_info()
    
    elif args.command == 'balance':
        manager.display_wallet_info()
    
    elif args.command == 'withdraw':
        result = manager.request_withdrawal(args.amount, args.address, args.type)
        print(f"Status: {result['status']}")
        if 'withdrawal' in result:
            print(f"Withdrawal ID: {result['withdrawal']['id']}")
            print(f"Amount: {result['withdrawal']['amount']} BTC")
            print(f"Address: {result['withdrawal']['address']}")
    
    elif args.command == 'confirm':
        result = manager.confirm_withdrawal(args.withdrawal_id, args.tx_hash)
        print(f"Status: {result['status']}")
        if 'withdrawal' in result:
            print(f"Amount: {result['withdrawal']['amount']} BTC")
            print(f"TX Hash: {result['withdrawal']['tx_hash']}")
    
    elif args.command == 'exchange':
        rate = manager.get_usd_exchange_rate(args.crypto)
        print(f"Current {args.crypto.upper()} rate: ${rate:.2f} USD")
    
    elif args.command == 'history':
        history = manager.get_transaction_history(args.limit)
        print(f"\nLast {len(history)} transactions:")
        print("-" * 80)
        for tx in history:
            print(f"{tx['timestamp']}: {tx['type']:20} {tx.get('amount', 0):>12.8f} - {tx.get('details', '')}")
        print("-" * 80)
    
    else:
        manager.display_wallet_info()


if __name__ == '__main__':
    main()
