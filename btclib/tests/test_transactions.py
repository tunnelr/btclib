#!/usr/bin/env python3

# Copyright (C) 2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

"Tests for `btclib.tx` module."

import pytest

from btclib import tx, tx_in, tx_out


def test_coinbase_1() -> None:

    block_1_coinbase_bytes = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0704ffff001d0104ffffffff0100f2052a0100000043410496b538e853519c726a2c91e61ec11600ae1390813a627c66fb8be7947be63c52da7589379515d4e0a604f8141781e62294721166bf621e73a82cbf2342c858eeac00000000"
    block_1_coinbase_input_bytes = "0000000000000000000000000000000000000000000000000000000000000000ffffffff0704ffff001d0104ffffffff"
    block_1_coinbase_output_bytes = "00f2052a0100000043410496b538e853519c726a2c91e61ec11600ae1390813a627c66fb8be7947be63c52da7589379515d4e0a604f8141781e62294721166bf621e73a82cbf2342c858eeac"

    transaction_in = tx_in.TxIn.deserialize(block_1_coinbase_input_bytes)
    transaction_out = tx_out.TxOut.deserialize(block_1_coinbase_output_bytes)
    transaction = tx.Tx.deserialize(block_1_coinbase_bytes)

    assert transaction.vin[0].scriptSig == transaction_in.scriptSig
    assert transaction.vout[0].scriptPubKey == transaction_out.scriptPubKey

    assert transaction.serialize().hex() == block_1_coinbase_bytes
    assert transaction_in.serialize().hex() == block_1_coinbase_input_bytes
    assert transaction_out.serialize().hex() == block_1_coinbase_output_bytes

    assert transaction.vin[0].scriptSig == []

    assert (
        transaction.txid
        == "0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098"
    )
    assert transaction.txid == transaction.hash

    assert transaction.size == 134
    assert transaction.weight == 536
    assert transaction.vsize == transaction.size


# https://en.bitcoin.it/wiki/Protocol_documentation#tx
def test_wiki_transaction() -> None:
    tx_bytes = "01000000016dbddb085b1d8af75184f0bc01fad58d1266e9b63b50881990e4b40d6aee3629000000008b483045022100f3581e1972ae8ac7c7367a7a253bc1135223adb9a468bb3a59233f45bc578380022059af01ca17d00e41837a1d58e97aa31bae584edec28d35bd96923690913bae9a0141049c02bfc97ef236ce6d8fe5d94013c721e915982acd2b12b65d9b7d59e20a842005f8fc4e02532e873d37b96f09d6d4511ada8f14042f46614a4c70c0f14beff5ffffffff02404b4c00000000001976a9141aa0cd1cbea6e7458a7abad512a9d9ea1afb225e88ac80fae9c7000000001976a9140eab5bea436a0484cfab12485efda0b78b4ecc5288ac00000000"

    transaction = tx.Tx.deserialize(tx_bytes)
    assert transaction.serialize().hex() == tx_bytes

    assert len(transaction.vin) == 1
    assert len(transaction.vout) == 2
    assert transaction.vout[0].nValue == 5000000
    assert transaction.vout[1].nValue == 3354000000

    assert transaction.txid == transaction.hash

    assert transaction.vsize == transaction.size


# 4e52f7848dab7dd89ef7ba477939574198a170bfcb2fb34355c69f5e0169f63c
def test_single_witness() -> None:
    tx_bytes = "010000000001019bdea7abb2fa14dead47dd14d03cf82212a25b6096a8da6b14feec3658dbcf9d0100000000ffffffff02a02526000000000017a914f987c321394968be164053d352fc49763b2be55c874361610000000000220020701a8d401c84fb13e6baf169d59684e17abd9fa216c8cc5b9fc63d622ff8c58d04004730440220421fbbedf2ee096d6289b99973509809d5e09589040d5e0d453133dd11b2f78a02205686dbdb57e0c44e49421e9400dd4e931f1655332e8d078260c9295ba959e05d014730440220398f141917e4525d3e9e0d1c6482cb19ca3188dc5516a3a5ac29a0f4017212d902204ea405fae3a58b1fc30c5ad8ac70a76ab4f4d876e8af706a6a7b4cd6fa100f44016952210375e00eb72e29da82b89367947f29ef34afb75e8654f6ea368e0acdfd92976b7c2103a1b26313f430c4b15bb1fdce663207659d8cac749a0e53d70eff01874496feff2103c96d495bfdd5ba4145e3e046fee45e84a8a48ad05bd8dbb395c011a32cf9f88053ae00000000"

    transaction = tx.Tx.deserialize(tx_bytes)

    assert transaction.serialize().hex() == tx_bytes

    assert len(transaction.vin) == 1
    assert len(transaction.vout) == 2
    assert transaction.nLockTime == 0

    assert (
        transaction.txid
        == "4e52f7848dab7dd89ef7ba477939574198a170bfcb2fb34355c69f5e0169f63c"
    )
    assert (
        transaction.hash
        == "d39eb3e3954be4bdc0b3be2d980124b1e1e11fb414b886b52939b07d95a58a8f"
    )

    assert transaction.size == 380
    assert transaction.weight == 758
    assert transaction.vsize == 190


# a4b76807519aba5740f7865396bc4c5ca0eb8aa7c3744ca2db88fcc9e345424c
def test_double_witness() -> None:
    tx_bytes = "01000000000102322d4f05c3a4f78e97deda01bd8fc5ff96777b62c8f2daa72b02b70fa1e3e1051600000017160014e123a5263695be634abf3ad3456b4bf15f09cc6afffffffffdfee6e881f12d80cbcd6dc54c3fe390670678ebd26c3ae2dd129f41882e3efc25000000171600145946c8c3def6c79859f01b34ad537e7053cf8e73ffffffff02c763ac050000000017a9145ffd6df9bd06dedb43e7b72675388cbfc883d2098727eb180a000000001976a9145f9e96f739198f65d249ea2a0336e9aa5aa0c7ed88ac024830450221009b364c1074c602b2c5a411f4034573a486847da9c9c2467596efba8db338d33402204ccf4ac0eb7793f93a1b96b599e011fe83b3e91afdc4c7ab82d765ce1da25ace01210334d50996c36638265ad8e3cd127506994100dd7f24a5828155d531ebaf736e160247304402200c6dd55e636a2e4d7e684bf429b7800a091986479d834a8d462fbda28cf6f8010220669d1f6d963079516172f5061f923ef90099136647b38cc4b3be2a80b820bdf90121030aa2a1c2344bc8f38b7a726134501a2a45db28df8b4bee2df4428544c62d731400000000"

    transaction = tx.Tx.deserialize(tx_bytes)

    assert transaction.serialize().hex() == tx_bytes

    assert len(transaction.vin) == 2
    assert len(transaction.vout) == 2
    assert transaction.nLockTime == 0

    assert (
        transaction.txid
        == "a4b76807519aba5740f7865396bc4c5ca0eb8aa7c3744ca2db88fcc9e345424c"
    )
    assert (
        transaction.hash
        == "0936cb8dba90e11345b9c05f457f139ddce4a5329701af4708b2cf4a02d75adb"
    )

    assert transaction.size == 421
    assert transaction.weight == 1033
    assert transaction.vsize == 259


def test_invalid_tx_in() -> None:
    transaction_input = tx_in.TxIn(
        prevout=tx_in.OutPoint("00" * 31 + "01", 256 ** 4 - 1),
        scriptSig=[],
        scriptSigHex="",
        nSequence=1,
        txinwitness=[],
    )

    with pytest.raises(ValueError):
        transaction_input.assert_valid()


def test_invalid_tx_in2() -> None:
    transaction_input = tx_in.TxIn(
        prevout=tx_in.OutPoint("00" * 32, 0),
        scriptSig=[],
        scriptSigHex="",
        nSequence=1,
        txinwitness=[],
    )

    with pytest.raises(ValueError):
        transaction_input.assert_valid()


def test_invalid_tx_out() -> None:
    transaction_output = tx_out.TxOut(nValue=-1, scriptPubKey=["OP_RETURN"])

    with pytest.raises(ValueError):
        transaction_output.assert_valid()


def test_invalid_tx_out2() -> None:
    transaction_output = tx_out.TxOut(
        nValue=2099999997690001, scriptPubKey=["OP_RETURN"]
    )

    with pytest.raises(ValueError):
        transaction_output.assert_valid()


def test_invalid_tx_out3() -> None:
    transaction_output = tx_out.TxOut(nValue=1, scriptPubKey=[])

    with pytest.raises(ValueError):
        transaction_output.assert_valid()


def test_missing_tx_in() -> None:
    transaction = tx.Tx(0, 0, [], [])
    err_msg = "A transaction must have at least one input"
    with pytest.raises(ValueError, match=err_msg):
        transaction.assert_valid()


def test_missing_tx_out() -> None:
    transaction_input = tx_in.TxIn(
        prevout=tx_in.OutPoint("ff" * 32, 0),
        scriptSig=[],
        scriptSigHex="",
        nSequence=1,
        txinwitness=[],
    )
    transaction = tx.Tx(0, 0, [transaction_input], [])
    err_msg = "A transaction must have at least one output"
    with pytest.raises(ValueError, match=err_msg):
        transaction.assert_valid()
