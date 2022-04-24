from web3 import Web3
from helpers import utils
import logging
import traceback


class Compounder:
    def __init__(
        self,
        private_key,
        wallet_address,
        contract_address,
        abi_file,
        max_tries,
        amount_to_action,
        txn_timeout,
        gas_price,
        gas,
        rpc_host,
        rewards_function
    ):
        self.private_key = private_key
        self.wallet_address = wallet_address
        self.contract_address = contract_address
        self.abi_file = abi_file
        self.max_tries = max_tries
        self.amount_to_action = amount_to_action
        self.txn_timeout = txn_timeout
        self.gas_price = gas_price
        self.gas = gas
        self.rpc_host = rpc_host
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_host))
        self.contract = self.w3.eth.contract(
            self.contract_address,
            abi=utils.read_json_file(self.abi_file)
        )
        self.rewards_function = rewards_function

    def get_miner_rewards(self):
        response = None
        for i in range(self.max_tries):
            try:
                function = "self.contract.functions.{}('{}').call()".format(
                    self.rewards_function,
                    self.wallet_address
                )
                response = eval(function)
            except Exception:
                logging.debug(
                    "Attempt {}: {}".format(i, traceback.format_exc())
                )
                continue
        return response

    def get_amount_to_action(self):
        return self.amount_to_action

    def get_remainder(self, miner_rewards, amount_to_action):
        return miner_rewards % amount_to_action

    def get_ratio(self, reward_remainder, amount_to_action):
        return (1 - reward_remainder / amount_to_action)

    def get_batch(self, miner_rewards, amount_to_action):
        return round(miner_rewards / amount_to_action)