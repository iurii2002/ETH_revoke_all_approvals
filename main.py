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
    # Gets the latest block number of the Ethereum blockchain
    # Returns string of the latest block number
    current_time = int(datetime.datetime.now().timestamp())
    get_latest_block_URL = f'{ENDPOINT}api?module=block&action=getblocknobytime&timestamp={current_time}&' \
                           f'closest=before&apikey={ETHERSCAN_API_KEY}'
    latest_block_details = requests.get(get_latest_block_URL)
    latest_block_number = latest_block_details.json()['result']
    return latest_block_number


def get_all_out_transactions(eth_address):
    # Gets all output transaction of the eth wallet up-to-date
    # Input: Ethereum wallet, e.g. 0x00000000219ab540356cBB839Cbe05303d7705Fa
    # Returns: list of transaction - [tx1, tx2, tx3]
    latest_block = get_latest_block_number()
    end_block = int(latest_block)
    start_block = 0
    api_request_get_all_approval_transactions_url = f"{ENDPOINT}api?module=account&action=txlist&address={eth_address}" \
                                                    f"&startblock={start_block}&endblock={end_block}&page=1&offset=10000&sort=asc" \
                                                    f"&apikey={ETHERSCAN_API_KEY}"
    all_out_transactions = requests.request("get", api_request_get_all_approval_transactions_url).json()["result"]
    return all_out_transactions


def filter_all_token_approve_transaction(list_of_transactions):
    # Filters only transaction with methodID "Approve" from the list of transactions. Typical for erc20 token approval
    # Input: list of transaction - [tx1, tx2, tx3]
    # Returns: list of transaction - [tx1, tx2]
    approve_txs = [tx for tx in list_of_transactions if tx['methodId'] == approval_methods["Approve"]]
    return approve_txs


def filter_all_nft_approve_transaction(list_of_transactions):
    # Filters only transaction with methodID "SetApprovalForAll" from the list of transactions. Typical for erc721 token approval
    # Input: list of transaction - [tx1, tx2, tx3]
    # Returns: list of transaction - [tx1, tx2]
    approve_txs = [tx for tx in list_of_transactions if tx['methodId'] == approval_methods["SetApprovalForAll"]]
    return approve_txs


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


def parse_tx_input(tx):
    # Gets main data from tx input
    # Input: ethereum transaction
    # Returns: (tx method, tx approval address, approved amount)
    tx = tx['input']
    method = tx[:10]
    approval_address_long = tx[10:10+64]
    approval_address = '0x' + approval_address_long[24:]
    amount_hex = tx[74:74+64]
    amount_dec = int(amount_hex, 16)
    amount_dec = "unlimited" if len(str(amount_dec)) > 75 else amount_dec
    return method, approval_address, amount_dec


def create_allowance(approved_address, amount):
    return {approved_address: amount}


def paste_allowances_in_dictionary(list_of_transactions):
    allowances = {}
    for tx in list_of_transactions:
        method, approved_address, amount = parse_tx_input(tx)
        token_contract = get_destination_tx(tx)
        if token_contract not in allowances:
            allowances[token_contract] = create_allowance(approved_address, amount)
        else:
            allowances[token_contract][approved_address] = amount
    print_allowances(allowances)


def check_allowance_from_token_contract(owner, contract_address, spender):
    contract = w3.eth.contract(address=contract_address, abi=get_contract_abi(contract_address))
    allowance = contract.functions.allowance(Web3.toChecksumAddress(owner), Web3.toChecksumAddress(spender)).call()
    return allowance
    # return contract.all_functions()

def get_contract_abi(contract_address):
    get_contract_abi_URL = f'{ENDPOINT}api?module=contract&action=getabi&address={contract_address}&' \
                           f'apikey={ETHERSCAN_API_KEY}'
    contract_abi = requests.get(get_contract_abi_URL).json()['result']
    return contract_abi


def print_allowances(allowances):
    for (contract, allowance) in allowances.items():
        print(contract, allowance)


if __name__ == "__main__":
    # get_allowances(filter_all_token_approve_transaction(get_all_out_transactions(address)))
    # print_transactions(filter_all_token_approve_transaction(get_all_out_transactions(address)))
    print(check_allowance_from_token_contract(address, '0x4d224452801ACEd8B2F0aebE155379bb5D594381', '0x34d85c9cdeb23fa97cb08333b511ac86e1c4e258'))
