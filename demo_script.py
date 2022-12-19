import market as mkt
from datetime import datetime, timedelta
sim = mkt.Simulator(file_path="data/688001.SH/20220812/逐笔委托.csv")

sim.reset()
time = datetime(year=2022, month=8, day=12) + timedelta(hours=9, minutes=15, seconds=0)
end_time = datetime(year=2022, month=8, day=12) + timedelta(hours=9, minutes=25, seconds=0)
while time < end_time:
    time = sim.next_step()
print(sim.order_book)
