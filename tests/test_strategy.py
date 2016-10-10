# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
Test the signature producing strategy.
"""

import unittest

from hypothesis import errors
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies

from hypothesis_extra_dbus_signature import dbus_signatures

from hypothesis_extra_dbus_signature._signature import _DBusSignatureStrategy

_CODES = _DBusSignatureStrategy.CODES + ['a', '{', '(']

class SignatureStrategyTestCase(unittest.TestCase):
    """
    Test for the signature strategy.
    """

    @given(
       strategies.text(
          alphabet=strategies.sampled_from(_CODES),
          min_size=1,
          max_size=len(_CODES)
       ).flatmap(
          lambda x: strategies.tuples(
             strategies.just(x),
             dbus_signatures(blacklist=x)
          )
       )
    )
    def testOmitsBlacklist(self, strategy):
        """
        Make sure all characters in blacklist are missing from signature.
        """
        (blacklist, signature) = strategy
        assert [x for x in blacklist if x in signature] == []

    @given(
       strategies.integers(min_value=2, max_value=10). \
       flatmap(
          lambda x: strategies.tuples(
             strategies.just(x),
             dbus_signatures(
                   max_codes=x,
                   max_complete_types=1,
                   blacklist='{'
             ).filter(lambda x: x != '')
          )
       )
    )
    @settings(max_examples=100)
    def testBounds(self, strategy):
        """
        Verify that the number of codes in a single complete type does not
        exceed the max number of codes, so long as dict entry types are omitted.
        """
        (max_codes, signature) = strategy
        leaves = [x for x in signature if x in _DBusSignatureStrategy.CODES]
        assert len(leaves) <= max_codes

    @given(dbus_signatures())
    @settings(max_examples=10)
    def testNoBlacklist(self, signature):
        """
        Just make sure there is a result when no blacklist is specified.
        """
        pass

    def testSuperSetBlacklist(self):
        """
        Verify correct behavior when blacklist contains all type codes.
        """
        codes = [
           'b',
           'd',
           'g',
           'h',
           'i',
           'n',
           'o',
           'q',
           's',
           't',
           'u',
           'v',
           'x',
           'y'
        ]

        blacklist = ''.join(codes)
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(blacklist=blacklist)