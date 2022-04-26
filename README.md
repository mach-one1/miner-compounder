# miner-compounder

Autocompound utility for crypto mining dapps. This is designed to work with mining dapps similar to bakedbeans.io. These dapps work in similar ways where you compound and claim crypto with a specific strategy (usually 6:1 compound:claim). This code can enable the compounding/claiming to be done automatically based on your preferred strategy.

## Running this with your dapp

Miners should be stored under the miners directory `miners/<minername>`. Within this directory you will need to place the dapps abi as `abi.json` and configure it for use in `config.ini`. Please see the current miners for what you need to configure here.

## Setup

You will need to install `python3` to run this once this is done install the requirements:

    pip3 install -r requirements.txt

To run this program you will need to pass in your metamask wallet address and private key. Prior to running you should check that the default values in config.ini are correct for what you want to compound.

## Securing your private key

* If running this locally you could use [sops](https://github.com/mozilla/sops) to pass through `PRIVATE_KEY` as an environment variable
  * Download [sops](https://github.com/mozilla/sops)
  * Download something to encrypt this with e.g. [age](https://github.com/FiloSottile/age)
  * Generate key `age-keygen -o key.txt`
  * Move file to correct location for sops
  * Create a file ending .env with the following text.
  ```
  PRIVATE_KEY=<your-private-key>
  ```
  * Other environment variables can be added to the file if desired
  * Encrypt the file
  ```
  sops --encrypt --age <age-public-key> .env > enc.env
  ```
  * Decrypt this at runtime
  ```
  sops exec-env enc.env 'python3 main.py <flags>'
  ```
* If running this via a cloud service you could use inbuilt secrets provide the environment variable to the script

## Running

    $ python3 main.py
    usage: main.py [-h] [-w WALLET_ADDRESS] [-k PRIVATE_KEY] [-c COMPOUNDER]

    Miner Compounder

    optional arguments:
    -h, --help            show this help message and exit
    -w WALLET_ADDRESS, --wallet-address WALLET_ADDRESS
                            Your wallet address. Can use env var WALLET_ADDRESS
    -k PRIVATE_KEY, --private-key PRIVATE_KEY
                            Your private key. Can use env var PRIVATE_KEY
    -c COMPOUNDER, --compounder COMPOUNDER
                            Autocompound miner. Can use env var COMPOUNDER

You will need to pass in the relevant flags. The compounder flag should match a miner that is stored in the `miners` directory.

## Donations

If you have found this useful please consider a donation to wallet address `0x893d850166B9BA1123955916830B97A2C9Ceb2Af`