#!/usr/bin/env python3

# Copyright (C) 2017-2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

"Tests for `btclib.curves` module."

import unittest
from typing import Dict

import pytest

from btclib.alias import INF, INFJ
from btclib.curve import Curve, _jac_from_aff
from btclib.curvemult import mult
from btclib.curves import CURVES
from btclib.numbertheory import mod_sqrt
from btclib.secpoint import bytes_from_point, point_from_octets


# FIXME Curve repr should use "dedbeef 00000000", not "0xdedbeef00000000"
# FIXME test curves when n>p


# test curves: very low cardinality
low_card_curves: Dict[str, Curve] = {}
# 13 % 4 = 1; 13 % 8 = 5
low_card_curves["ec13_11"] = Curve(13, 7, 6, (1, 1), 11, 1, False)
low_card_curves["ec13_19"] = Curve(13, 0, 2, (1, 9), 19, 1, False)
# 17 % 4 = 1; 17 % 8 = 1
low_card_curves["ec17_13"] = Curve(17, 6, 8, (0, 12), 13, 2, False)
low_card_curves["ec17_23"] = Curve(17, 3, 5, (1, 14), 23, 1, False)
# 19 % 4 = 3; 19 % 8 = 3
low_card_curves["ec19_13"] = Curve(19, 0, 2, (4, 16), 13, 2, False)
low_card_curves["ec19_23"] = Curve(19, 2, 9, (0, 16), 23, 1, False)
# 23 % 4 = 3; 23 % 8 = 7
low_card_curves["ec23_19"] = Curve(23, 9, 7, (5, 4), 19, 1, False)
low_card_curves["ec23_31"] = Curve(23, 5, 1, (0, 1), 31, 1, False)

all_curves: Dict[str, Curve] = {}
all_curves.update(low_card_curves)
all_curves.update(CURVES)


class TestEllipticCurves(unittest.TestCase):
    def test_all_curves(self):
        for ec in all_curves.values():
            assert mult(0, ec.G, ec) == INF
            assert mult(0, ec.G, ec) == INF

            assert mult(1, ec.G, ec) == ec.G
            assert mult(1, ec.G, ec) == ec.G

            Gy_odd = ec.y_odd(ec.G[0], True)
            assert Gy_odd % 2 == 1
            Gy_even = ec.y_odd(ec.G[0], False)
            assert Gy_even % 2 == 0
            self.assertTrue(ec.G[1] in (Gy_odd, Gy_even))

            Gbytes = bytes_from_point(ec.G, ec)
            G2 = point_from_octets(Gbytes, ec)
            assert ec.G == G2

            Gbytes = bytes_from_point(ec.G, ec, False)
            G2 = point_from_octets(Gbytes, ec)
            assert ec.G == G2

            P = ec.add(INF, ec.G)
            assert P == ec.G
            P = ec.add(ec.G, INF)
            assert P == ec.G
            P = ec.add(INF, INF)
            assert P == INF

            P = ec.add(ec.G, ec.G)
            assert P == mult(2, ec.G, ec)

            P = mult(ec.n - 1, ec.G, ec)
            assert ec.add(P, ec.G) == INF
            assert mult(ec.n, ec.G, ec) == INF

            assert mult(0, INF, ec) == INF
            assert mult(1, INF, ec) == INF
            assert mult(25, INF, ec) == INF

            ec_repr = repr(ec)
            if ec in low_card_curves.values() or ec.psize < 24:
                ec_repr = ec_repr[:-1] + ", False)"
            ec2 = eval(ec_repr)
            assert str(ec) == str(ec2)

    def test_octets2point(self):
        for ec in all_curves.values():
            Q = mult(ec.p, ec.G, ec)  # just a random point, not INF

            Q_bytes = b"\x03" if Q[1] & 1 else b"\x02"
            Q_bytes += Q[0].to_bytes(ec.psize, byteorder="big")
            R = point_from_octets(Q_bytes, ec)
            assert R == Q
            assert bytes_from_point(R, ec) == Q_bytes

            Q_hex_str = Q_bytes.hex()
            R = point_from_octets(Q_hex_str, ec)
            assert R == Q

            Q_bytes = b"\x04" + Q[0].to_bytes(ec.psize, byteorder="big")
            Q_bytes += Q[1].to_bytes(ec.psize, byteorder="big")
            R = point_from_octets(Q_bytes, ec)
            assert R == Q
            assert bytes_from_point(R, ec, False) == Q_bytes

            Q_hex_str = Q_bytes.hex()
            R = point_from_octets(Q_hex_str, ec)
            assert R == Q

            # scalar in point multiplication can be int, str, or bytes
            t = tuple()
            self.assertRaises(TypeError, mult, t, ec.G, ec)

            # not a compressed point
            Q_bytes = b"\x01" * (ec.psize + 1)
            self.assertRaises(ValueError, point_from_octets, Q_bytes, ec)
            # not a point
            Q_bytes += b"\x01"
            self.assertRaises(ValueError, point_from_octets, Q_bytes, ec)
            # not an uncompressed point
            Q_bytes = b"\x01" * 2 * (ec.psize + 1)
            self.assertRaises(ValueError, point_from_octets, Q_bytes, ec)

        # invalid x coordinate
        ec = CURVES["secp256k1"]
        x = 0xEEFDEA4CDB677750A420FEE807EACF21EB9898AE79B9768766E4FAA04A2D4A34
        xstr = format(x, "32X")
        self.assertRaises(ValueError, point_from_octets, "03" + xstr, ec)
        self.assertRaises(ValueError, point_from_octets, "04" + 2 * xstr, ec)
        self.assertRaises(ValueError, bytes_from_point, (x, x), ec)
        self.assertRaises(ValueError, bytes_from_point, (x, x), ec, False)

        # Point must be a tuple[int, int]
        P = x, x, x
        self.assertRaises(ValueError, ec.is_on_curve, P)

        # y-coordinate not in (0, p)
        P = x, ec.p + 1
        self.assertRaises(ValueError, ec.is_on_curve, P)

    def test_symmetry(self):
        """Methods to break simmetry: quadratic residue, odd/even, low/high"""
        for ec in low_card_curves.values():

            # setup phase
            # compute quadratic residues
            hasRoot = set()
            hasRoot.add(1)

            for i in range(2, ec.p):
                hasRoot.add(i * i % ec.p)

            # test phase
            Q = mult(ec.p, ec.G, ec)  # just a random point, not INF
            x = Q[0]
            if ec.p % 4 == 3:
                quad_res = ec.y_quadratic_residue(x, True)
                not_quad_res = ec.y_quadratic_residue(x, False)
                # in this case only quad_res is a quadratic residue
                self.assertIn(quad_res, hasRoot)
                root = mod_sqrt(quad_res, ec.p)
                assert quad_res == (root * root) % ec.p
                root = ec.p - root
                assert quad_res == (root * root) % ec.p

                self.assertTrue(not_quad_res == ec.p - quad_res)
                self.assertNotIn(not_quad_res, hasRoot)
                self.assertRaises(ValueError, mod_sqrt, not_quad_res, ec.p)

                y_odd = ec.y_odd(x, True)
                self.assertTrue(y_odd in (quad_res, not_quad_res))
                self.assertTrue(y_odd % 2 == 1)
                y_even = ec.y_odd(x, False)
                self.assertTrue(y_even in (quad_res, not_quad_res))
                self.assertTrue(y_even % 2 == 0)

                y_low = ec.y_low(x, True)
                self.assertTrue(y_low in (y_odd, y_even))
                y_high = ec.y_low(x, False)
                self.assertTrue(y_high in (y_odd, y_even))
                self.assertTrue(y_low < y_high)
            else:
                self.assertTrue(ec.p % 4 == 1)
                # cannot use y_quadratic_residue in this case
                self.assertRaises(ValueError, ec.y_quadratic_residue, x, True)
                self.assertRaises(ValueError, ec.y_quadratic_residue, x, False)

                y_odd = ec.y_odd(x, True)
                self.assertTrue(y_odd % 2 == 1)
                y_even = ec.y_odd(x, False)
                self.assertTrue(y_even % 2 == 0)
                # in this case neither or both are quadratic residues
                neither = y_odd not in hasRoot and y_even not in hasRoot
                both = y_odd in hasRoot and y_even in hasRoot
                self.assertTrue(neither or both)
                if y_odd in hasRoot:  # both have roots
                    root = mod_sqrt(y_odd, ec.p)
                    assert y_odd == (root * root) % ec.p
                    root = ec.p - root
                    assert y_odd == (root * root) % ec.p
                    root = mod_sqrt(y_even, ec.p)
                    assert y_even == (root * root) % ec.p
                    root = ec.p - root
                    assert y_even == (root * root) % ec.p
                else:
                    self.assertRaises(ValueError, mod_sqrt, y_odd, ec.p)
                    self.assertRaises(ValueError, mod_sqrt, y_even, ec.p)

                y_low = ec.y_low(x, True)
                self.assertTrue(y_low in (y_odd, y_even))
                y_high = ec.y_low(x, False)
                self.assertTrue(y_high in (y_odd, y_even))
                self.assertTrue(y_low < y_high)

        # with the last curve
        self.assertRaises(ValueError, ec.y_low, x, 2)
        self.assertRaises(ValueError, ec.y_odd, x, 2)
        self.assertRaises(ValueError, ec.y_quadratic_residue, x, 2)

    def test_aff_jac_conversions(self):
        for ec in all_curves.values():
            Q = mult(ec.p, ec.G, ec)  # just a random point, not INF
            QJ = _jac_from_aff(Q)
            checkQ = ec._aff_from_jac(QJ)
            assert Q == checkQ
            x = ec._x_aff_from_jac(QJ)
            assert Q[0] == x

            checkINF = ec._aff_from_jac(_jac_from_aff(INF))
            assert INF == checkINF
            # relevant for BIP340-Schnorr signature verification
            self.assertFalse(ec.has_square_y(INF))
            self.assertRaises(ValueError, ec._x_aff_from_jac, INFJ)
            self.assertRaises(TypeError, ec.has_square_y, "notapoint")

    def test_add(self):
        for ec in all_curves.values():
            Q1 = mult(ec.p, ec.G, ec)  # just a random point, not INF
            Q1J = _jac_from_aff(Q1)

            # distinct points
            Q3 = ec._add_aff(Q1, ec.G)
            Q3J = ec._add_jac(Q1J, ec.GJ)
            assert Q3 == ec._aff_from_jac(Q3J)

            # point at infinity
            Q3 = ec._add_aff(ec.G, INF)
            Q3J = ec._add_jac(ec.GJ, INFJ)
            assert Q3 == ec._aff_from_jac(Q3J)
            Q3 = ec._add_aff(INF, ec.G)
            Q3J = ec._add_jac(INFJ, ec.GJ)
            assert Q3 == ec._aff_from_jac(Q3J)

            # point doubling
            Q3 = ec._add_aff(Q1, Q1)
            Q3J = ec._add_jac(Q1J, Q1J)
            assert Q3 == ec._aff_from_jac(Q3J)

            # negate points
            Q1opp = ec.negate(Q1)
            Q3 = ec._add_aff(Q1, Q1opp)
            Q3J = ec._add_jac(Q1J, _jac_from_aff(Q1opp))
            assert Q3 == ec._aff_from_jac(Q3J)


def test_negate():
    for ec in all_curves.values():
        Q = mult(ec.p, ec.G, ec)  # just a random point, not INF
        minus_Q = ec.negate(Q)
        assert ec.add(Q, minus_Q) == INF

        # Jacobian coordinates
        QJ = _jac_from_aff(Q)
        minus_QJ = _jac_from_aff(minus_Q)
        assert ec._add_jac(QJ, minus_QJ) == INFJ

        # negate of INF is INF
        minus_INF = ec.negate(INF)
        assert minus_INF == INF

        # negate of INFJ is INFJ
        minus_INFJ = ec.negate(INFJ)
        assert minus_INFJ == INFJ

    with pytest.raises(TypeError, match="Not a point"):
        ec.negate("notapoint")


if __name__ == "__main__":
    # execute only if run as a script
    unittest.main()  # pragma: no cover
