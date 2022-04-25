from web3 import Web3
from helpers import utils
import logging
import time
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
        ratio_allowed,
        ignore_ratio,
        txn_timeout,
        gas_price,
        gas,
        rpc_host,
        rewards_function,
        compound_function,
        claim_function
    ):
        self.private_key = private_key
        self.wallet_address = wallet_address
        self.contract_address = contract_address
        self.abi_file = abi_file
        self.max_tries = max_tries
        self.amount_to_action = amount_to_action
        self.ratio_allowed = ratio_allowed
        self.ignore_ratio = ignore_ratio
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
        self.compound_function = compound_function
        self.claim_function = claim_function

    def get_miner_rewards(self):
        response = None
        for i in range(self.max_tries):
            try:
                f = "self.contract.functions.{}('{}').call()".format(
                    self.rewards_function,
                    self.wallet_address
                )
                response = eval(f)
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

    def check_new_batch(self, ready_batch, new_batch):
        if ready_batch > new_batch:
            message = ("Ready batch: {} which is greater than {}".
                       format(ready_batch, new_batch))
            logging.debug(message)
            print(message)
            return True
        else:
            message = ("Ready batch: {} should be greater than {}".
                       format(ready_batch, new_batch))
            logging.debug(message)
            print(message)
            return False

    def check_ratio(self, ratio):
        passed = False
        if self.ignore_ratio:
            passed = True
        else:
            passed = ratio > self.ratio_allowed
        if passed:
            logging.info("Current amount above ratio or ratio ignored")
        else:
            message = ("Ratio is {}. ".format(ratio) +
                       "should be above {}".format(
                        self.ratio_allowed
                        )
                       )
            logging.debug(message)
            print(message)
        return passed

    def nonce(self):
        return self.w3.eth.getTransactionCount(self.wallet_address)

    def get_transaction_data(self):
        return {
            "from": self.wallet_address,
            "gasPrice": utils.eth2wei(self.gas_price, "gwei"),
            "gas": self.gas,
            "nonce": self.nonce()
        }

    def compound_batch(self, ready_batch):

        for i in range(self.max_tries):
            try:
                f = "self.contract.functions.{}('{}').buildTransaction({})".format(
                    self.compound_function,
                    self.wallet_address,
                    self.get_transaction_data()
                )
                txn = eval(f)
                signed_txn = self.w3.eth.account.sign_transaction(
                    txn,
                    self.private_key
                )
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt and "status" in txn_receipt and \
                        txn_receipt["status"] == 1:
                    logging.info("Compound function successful")
                    ready_batch = 0
                    break
                else:
                    logging.info("Compound function unsuccessful")
                    logging.debug(txn_receipt)
                    time.sleep(10)
            except Exception:
                logging.debug(
                    "Attempt {}: {}".format(i, traceback.format_exc())
                )
                time.sleep(10)
        return ready_batch

    def claim_batch(self, ready_batch):

        for i in range(self.max_tries):
            try:
                f = "self.contract.functions.{}().buildTransaction({})".format(
                    self.claim_function,
                    self.get_transaction_data()
                )
                txn = eval(f)
                signed_txn = self.w3.eth.account.sign_transaction(
                    txn,
                    self.private_key
                )
                txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                if txn_receipt and "status" in txn_receipt and \
                        txn_receipt["status"] == 1:
                    logging.info("Claim function successful")
                    ready_batch = 0
                    break
                else:
                    logging.info("Claim function unsuccessful")
                    logging.debug(txn_receipt)
                    time.sleep(10)
            except Exception:
                logging.debug(
                    "Attempt {}: {}".format(i, traceback.format_exc())
                )
                time.sleep(10)
        return ready_batch
