import requests
import datetime
from web3 import Web3
from sensitive_data import ETHERSCAN_API_KEY, WEB3_PROVIDER

ENDPOINT = 'https://api.etherscan.io/'
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))


def get_latest_block_number():
    # Gets the latest block number of the Ethereum blockchain
    # Returns string of the latest block number
    current_time = int(datetime.datetime.now().timestamp())
    get_latest_block_url = f'{ENDPOINT}api?module=block&action=getblocknobytime&timestamp={current_time}&' \
                           f'closest=before&apikey={ETHERSCAN_API_KEY}'
    latest_block_details = requests.get(get_latest_block_url)
    latest_block_number = latest_block_details.json()['result']
    return latest_block_number


def print_transactions(list_of_transaction):
    # Prints transaction from the list
    # Input: list of transaction - [tx1, tx2, tx3]
    for tx in list_of_transaction:
        print(tx)


def get_destination_tx(tx):
    # Returns destination address from the transaction
    # Input: ethereum transaction
    # Returns: address, e.g. 0x00000000219ab540356cBB839Cbe05303d7705Fa
    return tx['to']


def parse_approval_tx_input_data(tx):
    # Gets main data from tx input
    # Input: ethereum transaction
    # Returns: (tx method, tx approval address, approved amount)
    tx = tx['input']
    method = tx[:10]
    approval_address_long = tx[10:10 + 64]
    approval_address = '0x' + approval_address_long[24:]
    amount_hex = tx[74:74 + 64]
    amount_dec = int(amount_hex, 16)
    amount_dec = "unlimited" if len(str(amount_dec)) > 75 else amount_dec
    return method, approval_address, amount_dec


def _get_contract_abi(contract_address):
    # Returns contract ABI using Etherscan API
    # Input: contract address
    # Returns: Contract ABI
    get_contract_abi_url = f'{ENDPOINT}api?module=contract&action=getabi&address={contract_address}&' \
                           f'apikey={ETHERSCAN_API_KEY}'
    contract_abi = requests.get(get_contract_abi_url).json()['result']
    return contract_abi


def get_allowance_from_token_contract(owner, contract_address, spender):
    # Gets the latest allowance info from the token contract
    # Input: address of the wallet, token contract address, spender address
    # Returns: amount of allowance
    contract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address),
                               abi=_get_contract_abi(contract_address))
    allowance = contract.functions.allowance(Web3.toChecksumAddress(owner), Web3.toChecksumAddress(spender)).call()
    allowance = allowance / (10 ** contract.functions.decimals().call())
    return allowance


def get_all_out_transactions(address):
    # Gets all output transaction of the eth wallet up-to-date
    # Returns: list of transaction - [tx1, tx2, tx3]
    latest_block = get_latest_block_number()
    end_block = int(latest_block)
    start_block = 0
    api_request_get_all_approval_transactions_url = f"{ENDPOINT}api?module=account&action=txlist&address={address}" \
                                                    f"&startblock={start_block}&endblock={end_block}&page=1&offset=10000&sort=asc" \
                                                    f"&apikey={ETHERSCAN_API_KEY}"
    all_out_transactions = requests.request("get", api_request_get_all_approval_transactions_url).json()["result"]
    return all_out_transactions