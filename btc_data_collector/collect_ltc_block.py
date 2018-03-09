#!/usr/bin/env python
# encoding=utf8

import logging
import sys
import traceback

from collector_conf import LTCCollectorConfig
from wallet_api import WalletApi
# import time
# from block_btc import BlockInfoBtc
# from datetime import datetime
from collect_btc_block import BTCCoinTxCollecter


class LTCCoinTxCollecter(BTCCoinTxCollecter):
    def __init__(self, db):
        super(LTCCoinTxCollecter, self).__init__(db)
        self.t_multisig_address = self.db.b_ltc_multisig_address
        self.config = LTCCollectorConfig()
        conf = {"host": self.config.RPC_HOST, "port": self.config.RPC_PORT}
        self.wallet_api = WalletApi(self.config.ASSET_SYMBOL, conf)