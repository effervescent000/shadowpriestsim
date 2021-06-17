import parse_file
import sim
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iterations', type=int, default=1000)
    parser.add_argument('-d', '--duration', type=int, default=150)
    args = parser.parse_args()

    pf = parse_file.ParseFile('spriest.xlsx')
    iterations = args.iterations
    duration = args.duration
    stat_weights = True
    toons = pf.toons
    simmed_dps = {}
    for x in toons:
        toon_sim = sim.Sim(x, iterations, duration, True, 'v')
        print('Done simming row {}!'.format(x.name))
        simmed_dps[x.name] = toon_sim.dps
    for x in simmed_dps.items():
        print(x)
    if stat_weights is True:
        pass


if __name__ == '__main__':
    main()
