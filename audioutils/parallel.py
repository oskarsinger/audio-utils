from pathos.multiprocessing import ProcessPool
from tqdm import tqdm

def do_parallel(closure, args, num_processes=6):

    print('Inside do_parallel')

    pool = ProcessPool(nodes=num_processes)
    result = pool.amap(closure, args)


def do_parallel_with_pbar(closure, args, num_processes=6):

    pool = ProcessPool(nodes=num_processes)

    print('STARTING TASKS')
    results = [pool.apipe(closure, arg)
               for arg in tqdm(args)]

    print('COMPLETING TASKS')
    total = len(results)

    with tqdm(total=total) as pbar:

        num_ready = 0

        while num_ready < total:
            
            ready = [r for r in results
                     if r.ready()]
            new_num_ready = len(ready)

            if new_num_ready > num_ready:
                pbar.update(new_num_ready - num_ready)

            num_ready = new_num_ready

