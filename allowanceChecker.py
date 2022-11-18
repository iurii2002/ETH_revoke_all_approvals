from etherscan_scripts import print_transactions, get_destination_tx, \
    parse_approval_tx_input_data, get_allowance_from_token_contract, get_all_out_transactions

approval_methods = {"Approve": "0x095ea7b3", "SetApprovalForAll": "0xa22cb465"}

address = '0xd2C2e84501C63b7B9897Df063288D67060119C99'


class AllowanceChecker:
    def __init__(self, address):
        self.address = address
        self.all_out_transactions = get_all_out_transactions(self.address)
        self.allowances = {}

    def filter_all_token_approve_transaction(self):
        # Filters only transaction with methodID "Approve" from the list of transactions. Typical for erc20 token approval
        # Returns: list of transaction - [tx1, tx2]
        approve_txs = [tx for tx in self.all_out_transactions if tx['methodId'] == approval_methods["Approve"]]
        return approve_txs

    def get_token_allowances_of_the_address(self):
        # Creates dictionary with allowances in format {token contract: {spender address: amount}}
        # Input: list of transactions with "approve" method
        # Returns: dictionary of allowances, {token contract: {spender address: amount}}
        for tx in self.filter_all_token_approve_transaction():
            method, approved_address, amount = parse_approval_tx_input_data(tx)
            token_contract = get_destination_tx(tx)
            if token_contract not in self.allowances:
                self.allowances[token_contract] = {approved_address: amount}
        self.update_allowances_from_contract()

    def update_allowances_from_contract(self):
        # Updates dictionary of allowances with the latest data from contract
        # Input: dictionary of allowances, {token contract: {spender address: amount}}
        # Returns: dictionary of allowances, {token contract: {spender address: amount}}
        for (contract, allowance) in self.allowances.items():
            for (spender, amount) in allowance.items():
                current_allowance = get_allowance_from_token_contract(address, contract, spender)
                if current_allowance != amount:
                    self.allowances[contract][spender] = current_allowance
                if current_allowance > 1e+58:
                    self.allowances[contract][spender] = "unlimited"

    def filter_all_nft_approve_transaction(self):
        # Filters only transaction with methodID "SetApprovalForAll" from the list of transactions. Typical for erc721 token approval
        # Returns: list of transaction - [tx1, tx2]
        approve_txs = [tx for tx in self.all_out_transactions if tx['methodId'] == approval_methods["SetApprovalForAll"]]
        return approve_txs
    # todo add checker for NFT

    def print_allowances(self):
        # Loop through allowance dictionary and prints every element
        for (contract, allowance) in self.allowances.items():
            print(contract, allowance)


if __name__ == "__main__":
    allowances = AllowanceChecker(address)
    allowances.get_token_allowances_of_the_address()
    allowances.print_allowances()
