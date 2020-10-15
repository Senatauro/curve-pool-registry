import pytest

from scripts.utils import pack_values, right_pad


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module")
def pool_base(PoolMock, accounts, DAI, USDC, USDT):
    coins = [DAI, USDC, USDT, ZERO_ADDRESS]
    yield PoolMock.deploy(3, coins, coins, 70, 4000000, {'from': accounts[0]})


@pytest.fixture(scope="module")
def pool_meta(MetaPoolMock, accounts, DAI, USDC, USDT, sUSD, lp_base, pool_base):
    coins = [sUSD, lp_base, ZERO_ADDRESS, ZERO_ADDRESS]
    underlying_coins = [sUSD, DAI, USDC, USDT]
    yield MetaPoolMock.deploy(2, 4, pool_base, coins, underlying_coins, 70, 4000000, {'from': accounts[0]})


@pytest.fixture(scope="module")
def lp_base(ERC20, accounts):
    yield ERC20.deploy("Curve Base LP Token", "lpBASE", 18, {"from": accounts[0]})


@pytest.fixture(scope="module")
def lp_meta(ERC20, accounts):
    yield ERC20.deploy("Curve Base LP Token", "lpBASE", 18, {"from": accounts[0]})



def test_add_metapool(accounts, registry, pool_base, lp_base, pool_meta, lp_meta, sUSD):
    registry.add_pool_without_underlying(
        pool_base,
        3,
        lp_base,
        "0x00",
        pack_values([18, 6, 6]),
        pack_values([False] * 8),
        True,
        True,
        {'from': accounts[0]}
    )
    registry.add_metapool(pool_meta, 2, 3, lp_meta, pack_values([18, 18]), {'from': accounts[0]})

    coin_info = registry.get_pool_coins(pool_meta)

    assert coin_info['coins'] == [sUSD, lp_base] + [ZERO_ADDRESS] * 6
    assert coin_info['decimals'] == [18, 18, 0, 0, 0, 0, 0, 0]
    assert coin_info['underlying_decimals'] == [18, 18, 6, 6, 0, 0, 0, 0]

    expected = [sUSD] + [pool_base.underlying_coins(i) for i in range(3)] + [ZERO_ADDRESS] * 4
    assert coin_info['underlying_coins'] == expected
