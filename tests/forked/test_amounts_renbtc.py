from brownie.test import given, strategy
from hypothesis import Phase, settings


@given(st_amounts=strategy("uint[100]", min_value=10**5, max_value=10**8, unique=True))
@settings(max_examples=5, phases=[Phase.generate])
def test_get_amounts(renbtc_swap, accounts, pool_renbtc, RenBTC, WBTC, st_amounts):
    amounts = renbtc_swap.get_exchange_amounts(
        pool_renbtc,
        RenBTC,
        WBTC,
        st_amounts,
    )
    for i in range(100):
        amount = renbtc_swap.get_exchange_amount(pool_renbtc, RenBTC, WBTC, st_amounts[i])
        assert amount == amounts[i]


@given(st_amounts=strategy("uint[100]", min_value=10**5, max_value=10**8, unique=True))
@settings(max_examples=5, phases=[Phase.generate])
def test_get_amounts_reversed(renbtc_swap, accounts, pool_renbtc, RenBTC, WBTC, st_amounts):
    amounts = renbtc_swap.get_exchange_amounts(
        pool_renbtc,
        WBTC,
        RenBTC,
        st_amounts,
    )
    for i in range(100):
        amount = renbtc_swap.get_exchange_amount(pool_renbtc, WBTC, RenBTC, st_amounts[i])
        assert amount == amounts[i]
