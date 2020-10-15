import brownie
import pytest

from scripts.utils import pack_values, right_pad

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_get_rates_compound(accounts, registry_compound, pool_compound, cDAI):
    assert registry_compound.get_rates(pool_compound) == [10**18, 10**18, 0, 0, 0, 0, 0, 0]

    cDAI._set_exchange_rate(31337, {'from': accounts[0]})
    assert registry_compound.get_rates(pool_compound) == [31337, 10**18, 0, 0, 0, 0, 0, 0]


def test_get_rates_y(accounts, registry_y, pool_y, yDAI):
    assert registry_y.get_rates(pool_y) == [10**18, 10**18, 10**18, 10**18, 0, 0, 0, 0]

    yDAI._set_exchange_rate(31337, {'from': accounts[0]})
    assert registry_y.get_rates(pool_y) == [31337, 10**18, 10**18, 10**18, 0, 0, 0, 0]


def test_pool_without_lending(accounts, registry_susd, pool_susd):
    assert registry_susd.get_rates(pool_susd) == [10**18, 10**18, 10**18, 10**18, 0, 0, 0, 0]


def test_unknown_pool(accounts, registry):
    assert registry.get_rates(accounts[-1]) == [0, 0, 0, 0, 0, 0, 0, 0]


def test_removed_pool(accounts, registry_y, pool_y, yDAI):
    yDAI._set_exchange_rate(31337, {'from': accounts[0]})
    assert registry_y.get_rates(pool_y) == [31337, 10**18, 10**18, 10**18, 0, 0, 0, 0]

    registry_y.remove_pool(pool_y)
    assert registry_y.get_rates(pool_y) == [0, 0, 0, 0, 0, 0, 0, 0]


def test_fix_incorrect_calldata(accounts, registry, pool_compound, lp_compound, cDAI):
    registry.add_pool(
        pool_compound,
        2,
        lp_compound,
        right_pad("0xdEAdbEEf"),
        pack_values([8, 8]),
        pack_values([18, 6]),
        True,
        True,
        {'from': accounts[0]}
    )

    with brownie.reverts("dev: bad response"):
        registry.get_rates(pool_compound)

    registry.remove_pool(pool_compound)
    registry.add_pool(
        pool_compound,
        2,
        lp_compound,
        right_pad(cDAI.exchangeRateStored.signature),
        pack_values([8, 8]),
        pack_values([18, 6]),
        True,
        True,
        {'from': accounts[0]}
    )

    assert registry.get_rates(pool_compound) == [10**18, 10**18, 0, 0, 0, 0, 0, 0]


def test_without_underlying(accounts, registry, pool_compound, cDAI, cUSDC):
    registry.add_pool_without_underlying(
        pool_compound,
        2,
        ZERO_ADDRESS,
        right_pad(cDAI.exchangeRateStored.signature),
        pack_values([8, 8]),
        pack_values([True] + [False] * 7),
        True,
        True,
        {'from': accounts[0]}
    )

    assert registry.get_rates(pool_compound) == [10**18, 10**18, 0, 0, 0, 0, 0, 0]

    cDAI._set_exchange_rate(31337, {'from': accounts[0]})
    cUSDC._set_exchange_rate(31337, {'from': accounts[0]})

    assert registry.get_rates(pool_compound) == [31337, 10**18, 0, 0, 0, 0, 0, 0]
