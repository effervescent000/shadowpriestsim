import parse_file
import sim

pf = parse_file.ParseFile('spriest.xlsx')
iterations = 10
duration = 2.5 * 60
stat_weights = True
toons = pf.toons
simmed_dps = {}
for x in toons:
    toon_sim = sim.Sim(x, iterations, duration, True, 'v')
    print('Done simming row {}!'.format(x.name))
    simmed_dps[x.name] = toon_sim.dps
for x in simmed_dps.items():
    print(x)
