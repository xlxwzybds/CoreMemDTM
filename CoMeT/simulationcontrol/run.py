import runlib


def example2():
    for benchmark in (
                      'parsec-blackscholes',
                      #'parsec-bodytrack',
                      #'parsec-canneal',
                      #'parsec-dedup',
                      #'parsec-fluidanimate',
                      #'parsec-streamcluster',
                      #'parsec-swaptions',
                      #'parsec-x264',
                      #'splash2-barnes',
                      #'splash2-fmm',
                      #'splash2-ocean.cont',
                      #'splash2-ocean.ncont',
                      #'splash2-radiosity',
                      #'splash2-raytrace',
                      #'splash2-water.nsq',
                      #'splash2-water.sp',
                      #'splash2-cholesky',
                      #'splash2-fft',
                      #'splash2-lu.cont',
                      #'splash2-lu.ncont',
                      #'splash2-radix'
                      ):
        min_parallelism = runlib.get_feasible_parallelisms(benchmark)[0]
        max_parallelism = runlib.get_feasible_parallelisms(benchmark)[-1]
        for freq in (1, 2, 3, 4):
            for parallelism in (min_parallelism, max_parallelism):
                # you can also use try_run instead
                runlib.run(['open', '{:.1f}GHz'.format(freq), 'constFreq'], runlib.get_instance(benchmark, parallelism, input_set='simsmall'))


def example():
    #for freq in (1.0,1.3,1.6,2.0,2.3,2.6,3.0,3.3,3.6,4.0,):  # when adding a new frequency level, make sure that it is also added in base.cfg
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.cfg
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-blackscholes', parallelism=8, input_set='medium'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-swaptions', parallelism=8, input_set='medium'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-bodytrack', parallelism=8, input_set='small'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-streamcluster', parallelism=8, input_set='medium'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-dedup', parallelism=8, input_set='medium'))


def case_study():
    runlib.run(['open', 'ondemand'], runlib.get_instance('parsec-swaptions', parallelism=4, input_set='medium'))


def main():
    example()
    #case_study()


if __name__ == '__main__':
    main()
