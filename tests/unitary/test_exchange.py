import brownie

from scripts.utils import pack_values

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_exchange(accounts, registry_swap, pool_compound, cDAI, cUSDC):
    cDAI._mint_for_testing(10**18, {'from': accounts[0]})
    cDAI.approve(registry_swap, 10**18, {'from': accounts[0]})
    expected = registry_swap.get_exchange_amount(pool_compound, cDAI, cUSDC, 10**18)

    registry_swap.exchange(pool_compound, cDAI, cUSDC, 10**18, 0, {'from': accounts[0]})
    assert cDAI.balanceOf(accounts[0]) == 0
    assert cUSDC.balanceOf(accounts[0]) == expected


def test_exchange_underlying(accounts, registry_swap, pool_compound, DAI, USDC):
    DAI._mint_for_testing(10**18, {'from': accounts[0]})
    DAI.approve(registry_swap, 10**18, {'from': accounts[0]})
    expected = registry_swap.get_exchange_amount(pool_compound, DAI, USDC, 10**18)

    registry_swap.exchange(pool_compound, DAI, USDC, 10**18, 0, {'from': accounts[0]})
    assert DAI.balanceOf(accounts[0]) == 0
    assert USDC.balanceOf(accounts[0]) == expected


def test_exchange_registry_has_balance(accounts, registry_swap, pool_compound, cDAI, cUSDC):
    cDAI._mint_for_testing(20**18, {'from': accounts[0]})
    cUSDC._mint_for_testing(20**18, {'from': accounts[0]})

    cDAI.transfer(registry_swap, 31337, {'from': accounts[0]})
    cUSDC.transfer(registry_swap, 31337, {'from': accounts[0]})

    cDAI.approve(registry_swap, 10**18, {'from': accounts[0]})
    registry_swap.exchange(pool_compound, cDAI, cUSDC, 10**18, 0, {'from': accounts[0]})

    assert cDAI.balanceOf(registry_swap) == 31337
    assert cUSDC.balanceOf(registry_swap) == 31337


def test_exchange_underlying_registry_has_balance(accounts, registry_swap, pool_compound, DAI, USDC):
    DAI._mint_for_testing(20**18, {'from': accounts[0]})
    USDC._mint_for_testing(20**18, {'from': accounts[0]})

    DAI.transfer(registry_swap, 31337, {'from': accounts[0]})
    USDC.transfer(registry_swap, 31337, {'from': accounts[0]})

    DAI.approve(registry_swap, 10**18, {'from': accounts[0]})
    registry_swap.exchange(pool_compound, DAI, USDC, 10**18, 0, {'from': accounts[0]})

    assert DAI.balanceOf(registry_swap) == 31337
    assert USDC.balanceOf(registry_swap) == 31337


def test_exchange_erc20_no_return_value(accounts, registry_swap, pool_susd, DAI, USDT):
    DAI._mint_for_testing(10**18, {'from': accounts[0]})
    DAI.approve(registry_swap, 10**18, {'from': accounts[0]})

    expected = registry_swap.get_exchange_amount(pool_susd, DAI, USDT, 10**18)
    registry_swap.exchange(pool_susd, DAI, USDT, 10**18, 0, {'from': accounts[0]})

    assert DAI.balanceOf(accounts[0]) == 0
    assert USDT.balanceOf(accounts[0]) == expected

    USDT.approve(registry_swap, expected, {'from': accounts[0]})
    new_expected = registry_swap.get_exchange_amount(pool_susd, USDT, DAI, expected)
    registry_swap.exchange(pool_susd, USDT, DAI, expected, 0, {'from': accounts[0]})

    assert DAI.balanceOf(accounts[0]) == new_expected
    assert USDT.balanceOf(accounts[0]) == 0


def test_min_dy(accounts, registry_all, registry_swap, pool_compound, lp_compound, DAI, USDC):
    DAI._mint_for_testing(10**18, {'from': accounts[0]})
    DAI.approve(registry_all, 10**18, {'from': accounts[0]})
    expected = registry_swap.get_exchange_amount(pool_compound, DAI, USDC, 10**18)
    with brownie.reverts():
        registry_swap.exchange(pool_compound, DAI, USDC, 10**18, expected + 1, {'from': accounts[0]})


def test_unknown_pool(accounts, registry_swap, pool_compound, DAI, USDT):
    with brownie.reverts("dev: no market"):
        registry_swap.exchange(pool_compound, DAI, USDT, 10**18, 0, {'from': accounts[0]})


def test_same_token(accounts, registry_swap, pool_compound, DAI):
    with brownie.reverts("dev: no market"):
        registry_swap.exchange(pool_compound, DAI, DAI, 10**18, 0, {'from': accounts[0]})


def test_same_token_underlying(accounts, registry_swap, pool_compound, cDAI):
    with brownie.reverts("dev: no market"):
        registry_swap.exchange(pool_compound, cDAI, cDAI, 10**18, 0, {'from': accounts[0]})


def test_token_returns_false(RegistrySwaps, PoolMock, accounts, BAD, DAI, registry):
    coins = [DAI, BAD, ZERO_ADDRESS, ZERO_ADDRESS]
    pool = PoolMock.deploy(2, coins, coins, 70, 4000000, {'from': accounts[0]})
    registry.add_pool(
        pool,
        2,
        ZERO_ADDRESS,
        "0x00",
        pack_values([18, 18]),
        pack_values([18, 18]),
        True,
        True,
        {'from': accounts[0]}
    )

    registry_swap = RegistrySwaps.deploy(registry, ZERO_ADDRESS, {'from': accounts[0]})

    DAI._mint_for_testing(10**18, {'from': accounts[0]})
    DAI.approve(registry_swap, 10**18, {'from': accounts[0]})
    expected = registry_swap.get_exchange_amount(pool, DAI, BAD, 10**18)

    registry_swap.exchange(pool, DAI, BAD, 10**18, 0, {'from': accounts[0]})

    assert DAI.balanceOf(accounts[0]) == 0
    assert BAD.balanceOf(accounts[0]) == expected

    new_expected = registry_swap.get_exchange_amount(pool, BAD, DAI, expected)

    BAD.approve(registry_swap, expected, {'from': accounts[0]})
    registry_swap.exchange(pool, BAD, DAI, expected, 0, {'from': accounts[0]})

    assert DAI.balanceOf(accounts[0]) == new_expected
    assert BAD.balanceOf(accounts[0]) == 0


def test_token_returns_false_revert(RegistrySwaps, PoolMock, accounts, BAD, DAI, registry):
    coins = [DAI, BAD, ZERO_ADDRESS, ZERO_ADDRESS]
    pool = PoolMock.deploy(2, coins, coins, 70, 4000000, {'from': accounts[0]})
    registry.add_pool(
        pool,
        2,
        ZERO_ADDRESS,
        "0x00",
        pack_values([18, 18]),
        pack_values([18, 18]),
        True,
        True,
        {'from': accounts[0]}
    )
    registry_swap = RegistrySwaps.deploy(registry, ZERO_ADDRESS, {'from': accounts[0]})

    with brownie.reverts():
        registry_swap.exchange(pool, BAD, DAI, 10**18, 0, {'from': accounts[0]})
