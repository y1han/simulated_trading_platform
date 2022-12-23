import market as mkt
from datetime import time
from visualization import *


sim = mkt.Simulator(code=688363, date=20220704)

sim.reset()
current_time = time(hour=9, minute=15, second=0)
end_time = time(hour=15, minute=00, second=0)

while current_time < end_time:
    current_time = sim.next_step()

# draw_spread(sim.order_book, given_time=time(hour=9, minute=30, second=0))
# draw_historical_spread(sim.order_book)
# draw_corr_price_volume(sim.order_book, 3)
draw_practical_corr_price_volume(sim.order_book, 1)
# draw_signature_plot_series(sim.order_book)
# draw_cum_trading_volume(sim.order_book)
# draw_order_book_depth_trend(sim.order_book)
# draw_price_series(sim.order_book)
