#!/usr/bin/env python 
# encoding: utf-8

__author__ = 'hasee'

import logging

class CollectorConfig(object):
    # DB configure
    DB_POOL_SIZE = 10
    CONNECT_TIMEOUT = 50
    MONGO_HOST = '192.168.1.123'
    MONGO_PORT = 27017
    MONGO_NAME = 'chaindb'
    MONGO_USER = 'chaindb_user'
    MONGO_PASS = 'yqr.1010'

    # LOG configure
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)-15s %(levelname)s %(funcName)s %(message)s'
    LOG_FILENAME = "btc_data_collector.log"

    # SYNC configure
    SYNC_BLOCK_PER_ROUND = 10000

class BKCollectorConfig(CollectorConfig):
    ASSET_SYMBOL = "BK"
    RPC_HOST = '192.168.1.195'
    RPC_PORT = 8093
    SYNC_STATE_FIELD = "bksyncstate"
    SYNC_BLOCK_NUM = "bksyncblocknum"
    SAFE_BLOCK_FIELD = "bksafeblock"
    CONTRACT_CALLER = "test115258982860"

class BTCCollectorConfig(CollectorConfig):
    ASSET_SYMBOL = "BTC"
    RPC_HOST = '192.168.1.121'
    RPC_PORT = 60011
    SYNC_STATE_FIELD = "btcsyncstate"
    SYNC_BLOCK_NUM = "btcsyncblocknum"
    SAFE_BLOCK_FIELD = "btcsafeblock"
    MULTISIG_VERSION = 196
class LTCCollectorConfig(CollectorConfig):
    ASSET_SYMBOL = "LTC"
    RPC_HOST = '192.168.1.123'
    RPC_PORT = 50001
    SYNC_STATE_FIELD = "ltcsyncstate"
    SYNC_BLOCK_NUM = "ltcsyncblocknum"
    SAFE_BLOCK_FIELD = "ltcsafeblock"
    MULTISIG_VERSION = 196
class UBCollectorConfig(CollectorConfig):
    ASSET_SYMBOL = "UB"
    RPC_HOST = '192.168.1.124'
    RPC_PORT = 60011
    SYNC_STATE_FIELD = "ubsyncstate"
    SYNC_BLOCK_NUM = "ubsyncblocknum"
    SAFE_BLOCK_FIELD = "ubsafeblock"
class HCCollectorConfig(CollectorConfig):
    ASSET_SYMBOL = "HC"
    RPC_HOST = '127.0.0.1'
    RPC_PORT = 19020
    SYNC_STATE_FIELD = "hcsyncstate"
    SYNC_BLOCK_NUM = "hcsyncblocknum"
    SAFE_BLOCK_FIELD = "hcsafeblock"
    MULTISIG_VERSION = 196





