# -*- coding: utf-8 -*-

from service import jsonrpc
from config import logger
from utils import eth_utils
from utils import btc_utils
from utils import etp_utils
from service import models
from service import db
from utils import error_utils
from bson import json_util
from bson import ObjectId
import pymongo
import time
import json
from datetime import datetime


@jsonrpc.method('Zchain.Transaction.Withdraw.History(chainId=str, trxId=str)')
def zchain_transaction_withdraw_history(chainId, trxId):
    logger.info('Zchain.Transaction.Withdraw.History')
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')
    if type(trxId) != unicode:
        return error_utils.mismatched_parameter_type('trxId', 'STRING')

    withdrawTrxs = db.b_withdraw_transaction.find({"TransactionId": trxId, "chainId": chainId}, {"_id": 0})

    return {
        'chainId': chainId,
        'data': list(withdrawTrxs)
    }


@jsonrpc.method('Zchain.Transaction.Deposit.History(chainId=str, blockNum=int)')
def zchain_transaction_deposit_history(chainId, blockNum):
    logger.info('Zchain.Transaction.Deposit.History')
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')
    if type(blockNum) != int:
        return error_utils.mismatched_parameter_type('blockNum', 'INTEGER')

    depositTrxs = db.b_deposit_transaction.find({"chainId": chainId, "blockNum": {"$gte": blockNum}}, {"_id": 0}).sort(
        "blockNum", pymongo.DESCENDING)
    trxs = list(depositTrxs)
    if len(trxs) == 0:
        blockNum = 0
    else:
        blockNum = trxs[0]['blockNum']

    return {
        'chainId': chainId,
        'blockNum': blockNum,
        'data': trxs
    }


@jsonrpc.method('Zchain.Configuration.Set(chainId=str, key=str, value=str)')
def zchain_configuration_set(chainId, key, value):
    logger.info('Zchain.Configure')
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')
    if type(key) != unicode:
        return error_utils.mismatched_parameter_type('key', 'STRING')
    if type(value) != unicode:
        return error_utils.mismatched_parameter_type('value', 'STRING')

    data = {"chainId": chainId, "key": key, "value": value}
    result = True
    try:
        db.b_config.insert_one(data)
    except Exception as e:
        logger.error(str(e))
        result = False
    finally:
        return {
            "result": result
        }


@jsonrpc.method('Zchain.Address.Setup(chainId=str, data=list)')
def zchain_address_setup(chainId, data):
    logger.info('Zchain.Address.Setup')
    addresses = db.b_chain_account
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')
    if type(data) != list:
        return error_utils.mismatched_parameter_type('data', 'ARRAY')

    num = 0
    for addr in data:
        if type(addr) == dict and 'address' in addr:
            addr["chainId"] = chainId
            try:
                addresses.insert_one(addr)
                num += 1
            except Exception as e:
                logger.error(str(e))
        else:
            logger.warn("Invalid chain address: " + str(addr))
    return {
        "valid_num": num
    }


@jsonrpc.method('Zchain.Deposit.Address.List(chainId=str)')
def zchain_deposit_address_list(chainId):
    logger.info('Zchain.Address.List')
    addresses = db.b_chain_account
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')

    addresses = addresses.find({"chainId": chainId}, {'_id': 0, 'address': 1})
    json_addrs = json_util.dumps(list(addresses))

    return {"addresses": json.loads(json_addrs)}


@jsonrpc.method('Zchain.Deposit.Address.Balance(chainId=str, address=str)')
def zchain_deposit_address_balance(chainId, address):
    logger.info('Zchain.Address.Balance')
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')
    if type(address) != unicode:
        return error_utils.mismatched_parameter_type('address', 'STRING')

    address = db.b_chain_account.find_one({"chainId": chainId, "address": address})
    if address is None:
        return error_utils.invalid_deposit_address(address)

    if chainId == "eth":
        balance = eth_utils.eth_get_base_balance(address)
    elif chainId == "btc":
        balance = btc_utils.btc_get_deposit_balance()
        address = "btc_deposit_address"
    elif chainId == "etp":
        balance = etp_utils.etp_get_addr_balance(address)
    else:
        return error_utils.invalid_chainid_type(chainId)

    return {
        "chainId": chainId,
        "address": address,
        "balance": balance
    }


# TODO, 备份私钥功能暂时注释，正式上线要加回来
@jsonrpc.method('Zchain.Address.Create(chainId=String)')
def zchain_address_create(chainId):
    logger.info('Create_address coin: %s' % (chainId))
    if chainId == 'eth':
        address = eth_utils.eth_create_address()
        print 1
    elif chainId == 'btc':
        address = btc_utils.btc_create_address()
    elif chainId == 'etp' :
        address = etp_utils.etp_create_address()
    else:
        return error_utils.invalid_chainid_type(chainId)
    if address != "":
        if chainId == 'eth':
            pass
            # eth_utils.eth_backup()
        else:
            pass
            # btc_utils.btc_backup_wallet()
        data = db.b_chain_account.find_one({"chainId": chainId, "address": address})
        if data != None:
            return {'chainId': chainId, 'error': '创建地址失败'}
        print 2
        d = {"chainId": chainId, "address": address, "name": "", "pubKey": "", "securedPrivateKey": "",
             "creatorUserId": "", "balance": {}, "memo": "", "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        db.b_chain_account.insert(d)
        return {'chainId': chainId, 'address': address}
    else:
        return {'chainId': chainId, 'error': '创建地址失败'}


@jsonrpc.method('Zchain.CashSweep(chainId=String)')
def zchain_collection_amount(chainId):
    logger.info('CashSweep chainId: %s' % (chainId))
    addressList = []
    chain_account = db.b_chain_account
    resultData = chain_account.find({"chainId": chainId})
    cash_sweep_account = ''
    for one_data in resultData:
        addressList.append(one_data["address"])
    cash_sweep_data = db.b_config.find_one({"key": "cash_sweep_address"})
    if cash_sweep_data is None:
        return error_utils.mis_cash_sweep_config()
    for data in cash_sweep_data["value"]:
        if data["chainId"] == chainId:
            cash_sweep_account = data["address"]
            break
    if chainId == 'eth':
        safeblock = db.b_config.find_one({"key": "safeblock"})["value"]
        resp, err = eth_utils.eth_collect_money(cash_sweep_account, addressList, safeblock)
        if resp is None:
            return error_utils.unexcept_error(err)
    elif chainId == 'btc':
        safeblock = db.b_config.find_one({"key": "btcsafeblock"})["value"]
        resp, err = btc_utils.btc_collect_money(cash_sweep_account, int(safeblock))
        if resp is None:
            return error_utils.unexcept_error(err)
    elif chainId == 'etp' :
        resp,err = etp_utils.etp_collect_money(cash_sweep_account)
        if resp is None:
            return error_utils.unexcept_error(err)
    else:
        return error_utils.invalid_chainid_type(chainId)
    print resp,1
    cash_sweep_op = {"operatorUserId": "1", "chainId": chainId, "sweepAddress": cash_sweep_account,
                     "status": 0, "memo": "", "errorMessage": resp["errdata"], "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if len(resp["data"]) == 0 and len(resp["errdata"]) == 0:
        return error_utils.unexcept_error("no balance to cash sweep!")
    opId = db.b_cash_sweep.insert(cash_sweep_op)

    for one_data in resp["data"]:
        op_data = {"cash_sweep_id": ObjectId(opId), "chainId": chainId, "fromAddress": one_data["from_addr"],
                   "sweepAddress": cash_sweep_account,
                   "successCoinAmount": one_data["amount"], "status": 0, "trxId": one_data["trx_id"],
                   "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        db.b_cash_sweep_plan_detail.insert(op_data)
    for one_data in resp["errdata"]:
        op_data = {"cash_sweep_id": ObjectId(opId), "chainId": chainId, "fromAddress": one_data["from_addr"],
                   "sweepAddress": cash_sweep_account,
                   "successCoinAmount": one_data["amount"], "status": -1, "errorMessage": one_data["error_reason"],
                   "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        db.b_cash_sweep_plan_detail.insert(op_data)
    logger.info(opId)
    return {'opId': str(opId), 'chainId': chainId}


@jsonrpc.method('Zchain.CashSweep.History(chainId=str, opId=str)')
def zchain_cashsweep_history(chainId, opId):
    """
    查询归账历史
    :param chainId:
    :return:
    """
    logger.info('Zchain.CashSweep.History')
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')
    if type(opId) != unicode:
        return error_utils.mismatched_parameter_type('opId', 'STRING')

    if opId == "":
        return error_utils.empty_cash_sweep_id()
    else:
        trxs = db.b_cash_sweep_plan_detail.find(
            {"chainId": chainId, "cash_sweep_id": ObjectId(opId)},
            {"chainId": 1, "trxTime": 1, "trxId": 1, "fromAddress": 1, "sweepAddress": 1, "successCoinAmount": 1,
             "status": 1, "_id": 0})

    return {
        'transactions': json.loads(json_util.dumps(trxs))
    }


@jsonrpc.method('Zchain.Withdraw.GetInfo(chainId=str)')
def zchain_withdraw_getinfo(chainId):
    """
    查询提现账户的信息
    :param chainId:
    :return:
    """
    logger.info('Zchain.Withdraw.GetInfo')
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')

    records = db.b_config.find_one({'key': 'withdrawaddress'}, {'_id': 0})
    address = ""
    if records == None:
        db.b_config.insert_one({"key": "withdrawaddress", "value": []})
        records = db.b_config.find_one({'key': 'withdrawaddress'}, {'_id': 0})
    for r in records["value"]:
        if r['chainId'] == chainId:
            address = r['address']

    if address == "":
        if chainId == "eth":
            address = eth_utils.eth_create_address()
            # eth_utils.eth_backup()
            records["value"].append({"chainId": "eth", "address": address})
        elif chainId == "btc":
            address = btc_utils.btc_create_withdraw_address()
            btc_utils.btc_backup_wallet()
            records["value"].append({"chainId": "btc", "address": address})
        elif chainId == "etp" :
            address = etp_utils.etp_create_withdraw_address()
            records["value"].append({"chainId": "etp", "address": address})
    db.b_config.update({"key": "withdrawaddress"}, {"$set": {"value": records["value"]}})
    balance = 0.0
    if chainId == "eth":
        balance = eth_utils.eth_get_base_balance(address)
    elif chainId == "btc":
        balance = btc_utils.btc_get_withdraw_balance()
    elif chainId == "etp" :
        balance = etp_utils.etp_get_addr_balance(address)
    else:
        return error_utils.invalid_chainid_type(chainId)

    return {
        'chainId': chainId,
        'address': address,
        'balance': balance
    }


@jsonrpc.method('Zchain.Withdraw.Execute(chainId=str, address=str, amount=float)')
def zchain_withdraw_execute(chainId, address, amount):
    """
    执行提现操作
    :param chainId:
    :return:
    """
    logger.info('Zchain.Withdraw.Execute')
    if type(chainId) != unicode:
        return error_utils.mismatched_parameter_type('chainId', 'STRING')
    if type(address) != unicode:
        return error_utils.mismatched_parameter_type('address', 'STRING')
    if type(amount) != float and type(amount) != int:
        return error_utils.mismatched_parameter_type('amount', 'FLOAT/INTEGER')

    records = db.b_config.find_one({'key': 'withdrawaddress'}, {'_id': 0})
    withdrawaddress = ""
    if records == None:
        return error_utils.unexcept_error("withdrawaddress is None")
    for r in records["value"]:
        if r['chainId'] == chainId:
            withdrawaddress = r['address']
    if address == "":
        return error_utils.unexcept_error("withdrawaddress is None")

    if chainId == "eth":
        if not address.startswith("0x", 0):
            return error_utils.invaild_eth_address(address)
        trxid = eth_utils.eth_send_transaction(withdrawaddress, address, amount)
    elif chainId == "btc":
        trxid = btc_utils.btc_withdraw_to_address(address, amount)
    elif chainId == "etp" :
        trxid = etp_utils.etp_withdraw_address(address,amount)
    else:
        return error_utils.invalid_chainid_type(chainId)
    if trxid == "":
        return error_utils.unexcept_error("create trx error")
    trxdata = db.b_withdraw_transaction.find_one({"chainId": chainId, "TransactionId": trxid})
    if trxdata == None:
        db.b_withdraw_transaction.insert(
            {'chainId': chainId, "toAddress": address, "TransactionId": trxid, "assetName": chainId, "amount": amount,
             "fromAccount": withdrawaddress, "status": 1, "trxTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    else:
        return error_utils.unexcept_error("trx exist error")
    return {
        'amount': amount,
        'chainId': chainId,
        'trxId': trxid
    }
