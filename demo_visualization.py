import market as mkt
from datetime import time
from visualization import *


sim = mkt.Simulator(code=688017)

sim.reset()
current_time = time(hour=9, minute=15, second=0)
end_time = time(hour=10, minute=50, second=0)

while current_time < end_time:
    current_time = sim.next_step()
draw_historical_spread(sim.order_book)
print(sim.order_book)
