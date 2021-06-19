import parse_file
import sim
import argparse
import stat_weights


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iterations', type=int, default=1000)
    parser.add_argument('-d', '--duration', type=int, default=150)
    parser.add_argument('-sw', action='store_true')
    parser.add_argument('-log', choices=['v', 'verbose', 's', 'stats'])
    args = parser.parse_args()

    pf = parse_file.ParseFile('spriest.xlsx')
    iterations = args.iterations
    duration = args.duration
    if args.sw is True:
        get_weights = True
    else:
        get_weights = False
    log = False
    log_mode = None
    if args.log is not None:
        log = True
        log_mode = args.log
    toons = pf.toons
    simmed_dps = {}
    if get_weights is True:
        stat_weights.StatWeights(toons[0], iterations, duration)
    else:
        for x in toons:
            toon_sim = sim.Sim(x, iterations, duration, log, log_mode)
            print('Done simming row {}!'.format(x.name))
            simmed_dps[x.name] = toon_sim.dps
        for x in simmed_dps.items():
            print(x)


if __name__ == '__main__':
    main()
