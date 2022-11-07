import requests
import datetime
from web3 import Web3
from sensitive_data import ETHERSCAN_API_KEY, WEB3_PROVIDER

ENDPOINT = 'https://api.etherscan.io/'

contracts = []
address = '0xd2C2e84501C63b7B9897Df063288D67060119C99'
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

approval_methods = {"Approve": "0x095ea7b3", "SetApprovalForAll": "0xa22cb465"}


def get_latest_block_number():
    current_time = int(datetime.datetime.now().timestamp())
    get_latest_block_URL = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={current_time}&' \
                           f'closest=before&apikey={ETHERSCAN_API_KEY}'
    latest_block_details = requests.get(get_latest_block_URL)
    latest_block_number = latest_block_details.json()['result']
    return latest_block_number


def get_all_out_transactions(eth_address):
    latest_block = get_latest_block_number()
    end_block = int(latest_block)
    start_block = 0
    api_request_get_all_approval_transactions_url = f"{ENDPOINT}api?module=account&action=txlist&address={eth_address}" \
                                                    f"&startblock={start_block}&endblock={end_block}&page=1&offset=10000&sort=desc" \
                                                    f"&apikey={ETHERSCAN_API_KEY}"
    all_out_transactions = requests.request("get", api_request_get_all_approval_transactions_url).json()["result"]
    return all_out_transactions


def filter_all_token_approve_transaction(list_of_transactions):
    approve_txs = [tx for tx in list_of_transactions if tx['methodId'] == approval_methods["Approve"]]
    return approve_txs


def filter_all_nft_approve_transaction(list_of_transactions):
    approve_txs = [tx for tx in list_of_transactions if tx['methodId'] == approval_methods["SetApprovalForAll"]]
    return approve_txs


def print_transactions(list_of_transaction):
    for tx in list_of_transaction:
        print(tx)

def get_allowance():

    contract = w3.eth.contract(address='0x000000000000000000000000000000000000dEaD', abi=...)