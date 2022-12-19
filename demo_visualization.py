import market as mkt
from datetime import time
from visualization import draw_spread


sim = mkt.Simulator(code=688017)

sim.reset()
current_time = time(hour=9, minute=15, second=0)
end_time = time(hour=10, minute=50, second=0)
current_time = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
end_time = (end_time.hour * 60 + end_time.minute) * 60 + end_time.second

while current_time < end_time:
    current_time = sim.next_step()
draw_spread(sim.order_book)
print(sim.order_book)
