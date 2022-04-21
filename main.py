from compounder import Compounder
from helpers import utils
import argparse
import configparser
import logging
import os


def main(args, config):

    compounder = Compounder(
        args.private_key,
        args.wallet_address,
        config["default"]["contract_address"],
        "./miners/{}/abi.json".format(args.compounder),
        config.getint('default', 'max_tries'),
        config.getfloat('default', 'crypto_to_compound'),
    )

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
        help="Autocompound drip garden. Can use env var COMPOUND_GARDEN",
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
