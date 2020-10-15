import brownie
import pytest

from scripts.utils import pack_values

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@pytest.mark.parametrize("idx", range(4))
def test_remove(accounts, registry_all, pool_compound, pool_y, pool_susd, pool_eth, idx):
    pool_list = [pool_compound, pool_y, pool_susd, pool_eth]
    registry_all.remove_pool(pool_list[idx], {'from': accounts[0]})
    pool_list[idx] = pool_list[-1]
    pool_list[-1] = ZERO_ADDRESS

    assert registry_all.pool_count() == 3
    assert [registry_all.pool_list(i) for i in range(4)] == pool_list


def test_remove_all(accounts, registry_all, pool_compound, pool_y, pool_susd, pool_eth):
    for pool in (pool_compound, pool_y, pool_susd, pool_eth):
        registry_all.remove_pool(pool, {'from': accounts[0]})

    assert registry_all.pool_count() == 0
    for i in range(5):
        assert registry_all.pool_list(i) == ZERO_ADDRESS


def test_admin_only(accounts, registry_all, pool_compound):
    with brownie.reverts("dev: admin-only function"):
        registry_all.remove_pool(pool_compound, {'from': accounts[1]})


def test_cannot_remove_twice(accounts, registry_all, pool_compound):
    registry_all.remove_pool(pool_compound, {'from': accounts[0]})

    with brownie.reverts("dev: pool does not exist"):
        registry_all.remove_pool(pool_compound, {'from': accounts[0]})


def test_pool_coins(accounts, registry_all, pool_compound, pool_y, pool_susd):
    compound_info = registry_all.get_pool_coins(pool_compound)
    susd_info = registry_all.get_pool_coins(pool_susd)

    registry_all.remove_pool(pool_y, {'from': accounts[0]})

    assert registry_all.get_pool_coins(pool_compound) == compound_info
    assert registry_all.get_pool_coins(pool_susd) == susd_info

    coin_info = registry_all.get_pool_coins(pool_y)
    assert not next((i for i in coin_info[0] if i != ZERO_ADDRESS), False)
    assert not next((i for i in coin_info[1] if i != ZERO_ADDRESS), False)
    assert coin_info[2] == [0, 0, 0, 0, 0, 0, 0, 0]


def test_get_pool_info(accounts, registry_all, pool_y, pool_susd, lp_susd):
    pool_info = registry_all.get_pool_info(pool_susd)

    registry_all.remove_pool(pool_y, {'from': accounts[0]})
    assert registry_all.get_pool_info(pool_susd) == pool_info

    registry_all.remove_pool(pool_susd, {'from': accounts[0]})
    with brownie.reverts():
        registry_all.get_pool_info(pool_susd)

    registry_all.add_pool(
        pool_susd,
        4,
        lp_susd,
        "0x00",
        pack_values([18, 6, 6, 18]),
        pack_values([18, 6, 6, 18]),
        True,
        True,
        {'from': accounts[0]}
    )
    assert registry_all.get_pool_info(pool_susd) == pool_info
