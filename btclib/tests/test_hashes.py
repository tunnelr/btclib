#!/usr/bin/env python3

# Copyright (C) 2017-2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

"Tests for `btclib.hashes` module."

from btclib import bip32
from btclib.hashes import fingerprint


def test_fingerprint() -> None:

    seed = "bfc4cbaad0ff131aa97fa30a48d09ae7df914bcc083af1e07793cd0a7c61a03f65d622848209ad3366a419f4718a80ec9037df107d8d12c19b83202de00a40ad"
    xprv = bip32.rootxprv_from_seed(seed)
    pf = fingerprint(xprv)  # xprv is automatically converted to xpub
    child_key = bip32.derive(xprv, 0x80000000)
    pf2 = bip32.deserialize(child_key)["parent_fingerprint"]
    assert pf == pf2
