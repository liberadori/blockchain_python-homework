# import libraries
from web3 import Web3
import os
from eth_account import Account
from pathlib import Path
from getpass import getpass
from constants import *
from pprint import pprint

import subprocess
import json

from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

from bit import wif_to_key, PrivateKeyTestnet
from bit.network import NetworkAPI
from eth_account import Account

from dotenv import load_dotenv


# loads environment variables without the need to reload jupyter lab
load_dotenv()

# Importing mnemonic from .env
mnemonic = os.getenv('MNEMONIC')

# Connecting to localhost network ETH/Geth
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

def derive_wallets(mnemonic, coin, numderive):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey,pubkeyhash,xprv,xpub --coin="{coin}" --numderive="{numderive}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

# testing derive_wallets function
derive_wallets(mnemonic, ETH, 3)

# Create an object
coins = {'BTC': derive_wallets(mnemonic, BTC, 3), 'ETH': derive_wallets(mnemonic, ETH, 3), 'BTCTEST': derive_wallets(mnemonic, BTCTEST, 3)}

# Testing the object
pprint(coins)

def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
priv_key_to_account(ETH, derive_wallets(mnemonic, ETH, 3)[0]['privkey'])

eth_acc = priv_key_to_account(ETH, derive_wallets(mnemonic, ETH, 5)[0]['privkey'])

btc_acc = priv_key_to_account(BTCTEST, derive_wallets(mnemonic, BTCTEST, 5)[0]['privkey'])


def create_tx(coin, account, recipient, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas({"from": eth_acc.address, "to": recipient, "value": amount})
        return {
            "from": eth_acc.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(eth_acc.address)
        }
    
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(btc_acc.address, [(recipient, amount, BTC)])

    
def send_tx(coin, account, recipient, amount):
    txn = create_tx(coin, account, recipient, amount)
    
    if coin == ETH:
        signed_txn = eth_acc.sign_transaction(txn)
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        signed_txn = btc_acc.sign_transaction(txn)
        result = NetworkAPI.broadcast_tx_testnet(signed_txn)
        #print(result.hex())
        #return result.hex()
        

# checking balance
btctest_key_sender = wif_to_key("cUAbbJPPBkzokbkrikQJkpoKCNEoEoopDD2pS7q9eAMbCWimWZe5")
print(btctest_key_sender = wif_to_key("cUAbbJPPBkzokbkrikQJkpoKCNEoEoopDD2pS7q9eAMbCWimWZe5"))

btctest_key_recipient = wif_to_key("cSxEKHxs3A25g8J6zTN9jEJTpXKAuNUU4jPbKoQEZWxC7w3WoRej")
print(btctest_key_recipient.get_balance('btc'))



# Sending Transactions

# Ethereum Transaction
print(w3.eth.blockNumber)

node1_balance = w3.eth.getBalance("0x66588F330cF4741C8E05a9d8c45FB2810ecffff2")
print(node1_balance)

node2_balance = w3.eth.getBalance("0xFa596082d245FB5cc8A76715E599462d180116dA")
print(node2_balance)

create_tx(ETH, eth_acc, '0x66588F330cF4741C8E05a9d8c45FB2810ecffff2', 10000)
send_tx(ETH, eth_acc, '0x527775c4b25b14721ad1dB9D190dA5a5d5aF3a91', 10000)

# Bitcoin TestNet Transaction
send_tx(BTCTEST, btc_acc, 'ms4mjqE7mghTeL2nrmLq9LaxzcP3KZHvE4', .005)