import allure
from typing import Optional, Dict, Any, List
from web3 import Web3
from eth_account import Account
from collections import namedtuple


class EthereumClient:

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

    @allure.step("Check node connectivity")
    def is_connected(self) -> bool:
        try:
            return self.w3.is_connected()
        except Exception as e:
            allure.attach(str(e), "Connection Error", allure.attachment_type.TEXT)
            return False

    @allure.step("Get client version")
    def get_client_version(self) -> str:
        version = self.w3.client_version
        allure.attach(version, "Client Version", allure.attachment_type.TEXT)
        return version

    @allure.step("Get network version")
    def get_network_version(self) -> str:
        version = self.w3.net.version
        allure.attach(version, "Network Version", allure.attachment_type.TEXT)
        return version

    @allure.step("Get chain ID")
    def get_chain_id(self) -> int:
        chain_id = self.w3.eth.chain_id
        allure.attach(str(chain_id), "Chain ID", allure.attachment_type.TEXT)
        return chain_id

    @allure.step("Check sync status")
    def get_sync_status(self) -> Any:
        sync_status = self.w3.eth.syncing
        allure.attach(str(sync_status), "Sync Status", allure.attachment_type.TEXT)
        return sync_status

    @allure.step("Get current block number")
    def get_block_number(self) -> int:
        block_num = self.w3.eth.block_number
        allure.attach(str(block_num), "Block Number", allure.attachment_type.TEXT)
        return block_num

    @allure.step("Get block by number")
    def get_block(self, block_identifier: str = 'latest', full_transactions: bool = False) -> Dict:
        block = self.w3.eth.get_block(block_identifier, full_transactions)
        allure.attach(str(dict(block)), "Block Data", allure.attachment_type.JSON)
        return dict(block)

    @allure.step("Get balance for address {address}")
    def get_balance(self, address: str) -> int:
        balance = self.w3.eth.get_balance(address)
        allure.attach(f"{balance} wei ({self.w3.from_wei(balance, 'ether')} ETH)", 
                     "Balance", allure.attachment_type.TEXT)
        return balance

    @allure.step("Get gas price")
    def get_gas_price(self) -> int:
        gas_price = self.w3.eth.gas_price
        allure.attach(f"{gas_price} wei ({self.w3.from_wei(gas_price, 'gwei')} gwei)", 
                     "Gas Price", allure.attachment_type.TEXT)
        return gas_price

    @allure.step("Get fee history")
    def get_fee_history(self, block_count: int = 1, newest_block: str = 'latest', 
                       reward_percentiles: Optional[List[float]] = None) -> Dict:
        fee_history = self.w3.eth.fee_history(block_count, newest_block, reward_percentiles)
        allure.attach(str(fee_history), "Fee History", allure.attachment_type.JSON)
        return fee_history

    @allure.step("Estimate gas for transaction")
    def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        gas_estimate = self.w3.eth.estimate_gas(transaction)
        allure.attach(str(gas_estimate), "Gas Estimate", allure.attachment_type.TEXT)
        return gas_estimate

    @allure.step("Send raw transaction")
    def send_raw_transaction(self, signed_tx: bytes) -> str:
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx)
        tx_hash_hex = tx_hash.hex()
        allure.attach(tx_hash_hex, "Transaction Hash", allure.attachment_type.TEXT)
        return tx_hash_hex

    @allure.step("Get transaction receipt for {tx_hash}")
    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict]:
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        if receipt:
            allure.attach(str(dict(receipt)), "Transaction Receipt", allure.attachment_type.JSON)
            return dict(receipt)
        return None

    @allure.step("Wait for transaction receipt")
    def wait_for_transaction_receipt(self, tx_hash: str, timeout: int = 120) -> Dict:
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        allure.attach(str(dict(receipt)), "Transaction Receipt", allure.attachment_type.JSON)
        return dict(receipt)

    @allure.step("Get logs")
    def get_logs(self, filter_params: Dict[str, Any]) -> List[Dict]:
        logs = self.w3.eth.get_logs(filter_params)
        allure.attach(str([dict(log) for log in logs]), "Logs", allure.attachment_type.JSON)
        return [dict(log) for log in logs]

    @allure.step("Deploy SC")
    def deploy_contract(self, abi: List, bytecode: str, private_key: str, 
                       constructor_args: Optional[tuple] = None, gas_limit: int = 2000000) -> Dict[str, Any]:
        account = Account.from_key(private_key)
        
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        
        constructor = contract.constructor(*constructor_args) if constructor_args else contract.constructor()
        
        transaction = constructor.build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': gas_limit,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.send_raw_transaction(signed_tx.rawTransaction)
        
        receipt = self.wait_for_transaction_receipt(tx_hash)
        
        tx_receipt = namedtuple('TransactionReceipt', ['tx_hash', 'contract_address', 'receipt'])
        
        return tx_receipt(tx_hash, receipt['contractAddress'], receipt)

    @allure.step("Send ETH transaction")
    def send_eth(self, from_private_key: str, to_address: str, value_wei: int, gas_limit: int = 21000, gas_price: int = None, nonce: int = None, chain_id: int = None) -> str:
        account = Account.from_key(from_private_key)
        
        transaction = {
            'to': to_address,
            'value': value_wei,
            'gas': gas_limit,
            'gasPrice': gas_price or self.w3.eth.gas_price,
            'nonce': nonce or self.w3.eth.get_transaction_count(account.address),
            'chainId': chain_id or self.w3.eth.chain_id
        }
        
        signed_tx = self.w3.eth.account.sign_transaction(transaction, from_private_key)
        tx_hash = self.send_raw_transaction(signed_tx.rawTransaction)
        
        return tx_hash
