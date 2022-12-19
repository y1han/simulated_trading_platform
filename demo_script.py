import market as mkt

sim = mkt.Simulator(file_path="data/688001.SH/20220812/逐笔委托.csv")

sim.next_step()
sim.next_step()
