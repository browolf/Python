import requests
from web3 import Web3
from eth_abi import decode

def get_transaction_input_data(tx_hash):
    apikey = "xxx"
    url = f"https://api.bscscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={apikey}"
    response = requests.get(url)
    transaction = response.json().get('result', {})
    
    return transaction.get('input', '')

input_data = get_transaction_input_data("0xcbf70aa81c21cff3ae91fc95e0ec5b473fbb4d046e898b02cf93830e98fdeb7e")
print(f"Input Data: {input_data}")

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))

types = ['address[]', 'uint256[]']
decoded_data = decode(types, bytes.fromhex(input_data[2:]))

recipients = decoded_data[0]
amounts = decoded_data[1]

print("Recipients: ", recipients)
print("Amounts: ", amounts)
