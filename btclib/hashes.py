#!/usr/bin/env python3

# Copyright (C) 2017-2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

""" Hash based helper functions.

"""

from typing import Optional, Tuple

from .alias import HashF, Key, Script, String
from .script import encode
from .to_pubkey import pubkeyinfo_from_key
from .utils import hash160, sha256

_H160Net = Tuple[bytes, str]


def hash160_from_key(
    key: Key, network: Optional[str] = None, compressed: Optional[bool] = None
) -> _H160Net:
    """Return (public key HASH160, nettwork) from a private/public key.

    HASH160 is RIPEMD160(SHA256).
    """
    pubkey, network = pubkeyinfo_from_key(key, network, compressed)
    h160 = hash160(pubkey)
    return h160, network


def hash160_from_script(scriptPubKey: Script) -> bytes:
    """Return the scriptPubKey HASH160 from a private/public key.

    HASH160 is RIPEMD160(SHA256).
    """
    if isinstance(scriptPubKey, list):
        scriptPubKey = encode(scriptPubKey)
    return hash160(scriptPubKey)


def hash256_from_script(scriptPubKey: Script) -> bytes:
    """Return the scriptPubKey HASH256 from a private/public key.

    HASH256 is SHA256(SHA256).
    """
    if isinstance(scriptPubKey, list):
        scriptPubKey = encode(scriptPubKey)
    return sha256(scriptPubKey)


def fingerprint(key: Key, network: Optional[str] = None) -> bytes:
    """Return the public key fingerprint from a private/public key.

    The fingerprint is the last four bytes
    of the compressed public key HASH160.
    """

    pubkey, _ = pubkeyinfo_from_key(key, network, compressed=True)
    return hash160(pubkey)[:4]


def reduce_to_hlen(msg: String, hf: HashF) -> bytes:

    if isinstance(msg, str):
        msg = msg.encode()

    # Steps numbering follows SEC 1 v.2 section 4.1.3
    h = hf()
    h.update(msg)
    return h.digest()  # 4
