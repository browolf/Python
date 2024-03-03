import csv
from web3 import Web3
import requests
import sys
import os
import time

#the input file is downloaded from https://bscscan.com/address/0x7d2067399145788ed52c0820e8f53b21bf006f8d for the period 01/01/2023 t0 03/03/2024
#remove non airdrop rows and all the columns except transaction id and date(utc) 
input_file = "all_airdrops.csv"
output_file = "recipients.csv"
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Deleted {output_file}")

#apikey of bscscan
apikey = "xxxx"  
#w3 provider
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))



#input the transaction id csv file into an array of tuples
transaction_ids=[]
with open(input_file,'r', newline="") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        transaction_ids.append(tuple(row))

#remove the column names that came from the csv
transaction_ids = transaction_ids[1:]

def get_transaction_input_data(tx_hash):
    url = f"https://api.bscscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={apikey}"
    response = requests.get(url)
    transaction = response.json().get('result', {})   
    return transaction.get('input', '')    


def process_input_data(data):
    recipients = []
    amounts = []
    #this function find the recipient addresses and the amounts airdropped
    #cut off the first 10 characters
    data = data[10:]
    #split data into 64bit sections
    sections = [data[i:i+64] for i in range(0, len(data), 64)]
    #extract number of recipients
    number_of_recipients = int(sections[2],16)
    #cut off the first 3 items
    sections = sections[3:]
    #cut out the separator between recipients and amounts
    del sections[number_of_recipients]

    recipients = sections[:number_of_recipients]
    for i in range(number_of_recipients):
        recipients[i] = recipients[i][24:].lstrip("0")
    amounts = sections[number_of_recipients:]

    #appends 0x to the addresses to create wallet addresses
    recipients_with_ox = ["0x" + code for code in recipients]
    #converts 16bit hexadecimal to integer, divide by the individual units of the chain. 
    amounts_decimal = [(int(item,16)) / 10 ** 18 for item in amounts]

    return list(zip(recipients_with_ox, amounts_decimal))

def write_to_csv(data):
    with open(output_file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in data:
            csvwriter.writerow(row)

#initialise csv columns
write_to_csv([('Recipient','Amount','Date')])

#for each row in the array
for transaction in transaction_ids:   
    id = transaction[0]
    datestamp = transaction[1]

    print(f">>{id}  {datestamp}")

    input_data = get_transaction_input_data(id)
    paired_array = process_input_data(input_data)


    #print(paired_array)

    for pair in paired_array:
        write_to_csv([(pair[0],pair[1],datestamp)])
        print(pair)
    
    time.sleep(1)


print(len(transaction_ids))
