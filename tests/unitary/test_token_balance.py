import brownie


def test_admin_only(registry_swap, accounts, DAI):
    with brownie.reverts("dev: admin-only function"):
        registry_swap.claim_balance(DAI, {'from': accounts[1]})


def test_claim_normal(registry_swap, accounts, DAI):
    DAI._mint_for_testing(10**18, {'from': accounts[0]})
    DAI.transfer(registry_swap, 10**18, {'from': accounts[0]})
    registry_swap.claim_balance(DAI, {'from': accounts[0]})

    assert DAI.balanceOf(registry_swap) == 0
    assert DAI.balanceOf(accounts[0]) == 10**18


def test_claim_no_return(registry_swap, accounts, USDT):
    USDT._mint_for_testing(10**18, {'from': accounts[0]})
    USDT.transfer(registry_swap, 10**18, {'from': accounts[0]})
    registry_swap.claim_balance(USDT, {'from': accounts[0]})

    assert USDT.balanceOf(registry_swap) == 0
    assert USDT.balanceOf(accounts[0]) == 10**18


def test_claim_return_false(registry_swap, accounts, BAD):
    BAD._mint_for_testing(10**18, {'from': accounts[0]})
    BAD.transfer(registry_swap, 10**18, {'from': accounts[0]})
    registry_swap.claim_balance(BAD, {'from': accounts[0]})

    assert BAD.balanceOf(registry_swap) == 0
    assert BAD.balanceOf(accounts[0]) == 10**18


def test_claim_ether(registry_swap, accounts):
    accounts[1].transfer(registry_swap, "1 ether")
    balance = accounts[0].balance()

    registry_swap.claim_balance("0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", {'from': accounts[0]})
    assert accounts[0].balance() == balance + "1 ether"
