import parse_file
import sim
import argparse
import stat_weights


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iterations', type=int, default=1000)
    parser.add_argument('-d', '--duration', type=int, default=150)
    parser.add_argument('-sw', action='store_true')
    args = parser.parse_args()

    pf = parse_file.ParseFile('spriest.xlsx')
    iterations = args.iterations
    duration = args.duration
    if args.sw is True:
        get_weights = True
    else:
        get_weights = False
    toons = pf.toons
    simmed_dps = {}
    if get_weights is True:
        stat_weights.StatWeights(toons[0], iterations, duration)
    else:
        for x in toons:
            toon_sim = sim.Sim(x, iterations, duration, False, 'v')
            print('Done simming row {}!'.format(x.name))
            simmed_dps[x.name] = toon_sim.dps
        for x in simmed_dps.items():
            print(x)


if __name__ == '__main__':
    main()
