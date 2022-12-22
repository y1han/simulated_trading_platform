from market import Order


def strategy_execution(portfolio, optimal_bid, optimal_ask):
    return_orders = []
    if optimal_bid is None:
        return return_orders
    if portfolio.active_orders is not None:
        for order in portfolio.active_orders:
            return_orders.append((True, Order(uid=order[0], is_buy=order[1])))

    return_orders.extend(
        [(False, Order(uid=portfolio.order_index, is_buy=True, price=optimal_bid, quantity=100, is_ours=True)),
         (False, Order(uid=portfolio.order_index - 1, is_buy=False, price=optimal_ask, quantity=100, is_ours=True))]
    )

    portfolio.order_index -= 2
    return return_orders
