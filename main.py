from compounder import Compounder
from itertools import cycle
from helpers import utils
import argparse
import configparser
import json
import logging
import os
import time


def handle_miner(compounder, strategy_pool, new_batch):
    miner_rewards = compounder.get_miner_rewards()
    amount_to_action = compounder.get_amount_to_action()
    reward_remainder = compounder.get_remainder(
        miner_rewards, amount_to_action
    )
    ratio = compounder.get_ratio(reward_remainder, amount_to_action)
    message = json.dumps(
        {
            'miner':
                {
                    'miner_rewards': miner_rewards,
                    'amount_to_action': amount_to_action,
                    'reward_remainder': reward_remainder,
                    'ratio': ratio

                }
        },
        indent=4
    )
    logging.debug(message)
    print(message)
    if miner_rewards >= amount_to_action:
        ready_batch = compounder.get_batch(
            miner_rewards, amount_to_action
        )
        if compounder.check_new_batch(ready_batch, new_batch) and \
                compounder.check_ratio(ratio):
            new_batch = ready_batch
            action = next(strategy_pool)
            if action == 'compound':
                new_batch = compounder.compound_batch(ready_batch)
            elif action == 'claim':
                new_batch = compounder.claim_batch(ready_batch)
    return new_batch


def main(args, config):

    compounder = Compounder(
        args.private_key,
        args.wallet_address,
        config["default"]["contract_address"],
        "./miners/{}/abi.json".format(args.compounder),
        config.getint('default', 'max_tries'),
        config.getint('default', 'amount_to_action'),
        config.getfloat('default', 'ratio_allowed'),
        config.getboolean('default', 'ignore_ratio'),
        config.getint('default', 'txn_timeout'),
        config.getint('default', 'gas_price'),
        config.getint('default', 'gas'),
        config["default"]["rpc_host"],
        config["default"]["rewards_function"],
        config["default"]["compound_function"],
        config["default"]["claim_function"]
    )

    strategy = utils.strategy(config["default"]["strategy"])
    strategy_pool = cycle(strategy)
    new_batch = 0
    while True:
        new_batch = handle_miner(compounder, strategy_pool, new_batch)
        time.sleep(5)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Miner Compounder')
    parser.add_argument(
        "-w", "--wallet-address",
        help="Your wallet address. Can use env var WALLET_ADDRESS",
        type=str, dest='wallet_address',
        default=os.environ.get('WALLET_ADDRESS')
    )
    parser.add_argument(
        "-k", "--private-key",
        help="Your private key. Can use env var PRIVATE_KEY",
        type=str, dest='private_key',
        default=os.environ.get('PRIVATE_KEY')
    )
    parser.add_argument(
        "-c", "--compounder",
        help="Autocompound miner. Can use env var COMPOUNDER",
        type=str, dest='compounder',
        default=os.environ.get('COMPOUNDER')
    )
    args = parser.parse_args()
    if not (args.wallet_address and args.private_key):
        exit(parser.print_help())

    config = configparser.ConfigParser()
    config.read("./miners/{}/config.ini".format(args.compounder))

    logging.basicConfig(
        level=utils.get_log_level(config.get('default', 'log_level')),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("compounder.log"),
            logging.StreamHandler()
        ]
    )

    main(args, config)
