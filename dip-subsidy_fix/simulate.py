#!/usr/bin/env python3

"""
        simulate.py
        DIP-subsidy_fix
        author: Yoshi Jaeger
"""

"""
	This script contains both, mathematical functions and
	unperformant, but more accurate, simulations.

	The math is 99% accurate, however, due to integer arithmetics
	in divisions we get small rounding errors of up to a few satoshis,
	especially for phase 5 and 6.
"""

"""
	The following mathematical equations are given for completeness sake
	to calculate the supply on the fly.
"""

COIN = 100000000
GENESIS = 8000
BLOCK_TIME = 15

LAST_KNOWN_BLOCK = {
	'height': 14419132,
	'time': 1643092914,
}

def check(minVal, maxVal, val):
	if val < minVal or val >= maxVal:
		raise ValueError('Invalid value passed. {} must be between {} and {}', val, minVal, maxVal)

def math_phase6_acc(n):
	n = n + 1
	norm = 1430000
	interval = 175200
	base = 2157/2 * COIN * interval
	pmax = int((n - norm)/interval)
	d = 98884/100000

	series = (1 - pow(d, pmax))/(1 - d) + \
		pow(d, pmax) * ((n - norm) % interval)/interval

	return base * series

def math_phase5_acc(n):
	n = n + 1
	norm = 400000
	interval = 80160
	base = 2459 * COIN * interval
	pmax = int((n - norm) / interval) + 1
	d = 99/100

	series = (1 - pow(d, pmax))/(1 - d) + \
		pow(d, pmax) * ((n - norm) % interval)/interval - 1

	return base * series

def math_phase4_acc(n):
	n = n + 1
	norm = 67200
	interval = 10080
	base = 8000 * COIN * interval
	pmax = int((n - norm) / interval) + 1
	d = 995/1000

	series = (1 - pow(d, pmax))/(1 - d) + \
		pow(d, pmax) * ((n - norm) % interval)/interval - 1

	return base * series	

def math_phase3_acc(n):
	base = 8000 * COIN
	times = n - 5760 + 1
	return base * times

def math_phase2_acc(n):
	base = 16000 * COIN
	times = n - 1440 + 1
	return base * times

def math_phase1_acc(n):
	base = 72000 * COIN
	times = n
	return base * times

def math_phase1_single(n): return 72000 * COIN

def math_phase2_single(n): return 16000 * COIN

def math_phase3_single(n): return 8000 * COIN

def math_phase4_single(n):
	base = 8000 * COIN
	decay = 0.995
	interval = 10080
	norm = 67200

	m = 1 + int((n - norm) / interval)
	return base * pow(decay, m)

def math_phase5_single(n):
	base = 2459 * COIN
	decay = 0.99
	interval = 80160
	norm = 400000
	
	m = 1 + int((n - norm) / interval)
	return base * pow(decay, m)

def math_phase6_single(n):
	base = 2157 * COIN / 2
	decay = 0.98884
	interval = 175200
	norm = 1430000
	
	m = int((n - norm) / interval)
	return base * pow(decay, m)

"""
	The following functions will calculate the supply by
	performing integer arithmetics.
	This will yield the most accurate numbers.

	Caution: Calling these functions can take several seconds up to several minutes.
"""

def sim_phase1_single(n): return 72000 * COIN

def sim_phase2_single(n): return 16000 * COIN

def sim_phase3_single(n): return 8000 * COIN

def sim_phase4_single(n):
	base = 8000 * COIN
	norm = 67200
	interval = 10080
	blocks = n - norm
	weeks = int(blocks / interval) + 1

	val = base

	for i in range(0, weeks):
		val = val - int(val / 200)

	return val

def sim_phase5_single(n):
	base = 2459 * COIN
	norm = 400000
	interval = 80160
	blocks = n - norm
	weeks = int(blocks / interval) + 1

	val = base

	for i in range(0, weeks):
		val = val - int(val / 100)

	return val

def sim_phase6_single(n):
	base = int(2157 * COIN / 2)
	norm = 1430000
	interval = 175200
	decay_n = 98884
	decay_m = 100000
	blocks = n - norm
	months = int(blocks / interval)

	val = base

	for i in range(0, months):
		val = int(val * decay_n)
		val = int(val / decay_m)

	return val

def sim_phase7_single(n):
	raise NotImplementedError('Not implemented yet')

def sim_phase1_acc(n = 1440 - 1):
	start = 1
	total = 0

	for i in range(start, n + 1):
		total = total + sim_phase1_single(i)

	return total

def sim_phase2_acc(n = 5760 - 1):
	start = 1440
	total = 0

	for i in range(start, n + 1):
		total = total + sim_phase2_single(i)

	return total

def sim_phase3_acc(n = 67200 - 1):
	start = 5760
	total = 0

	for i in range(start, n + 1):
		total = total + sim_phase3_single(i)

	return total

def sim_phase4_acc(n = 400000 - 1):
	start = 67200
	total = 0

	for i in range(start, n + 1):
		total = total + sim_phase4_single(i)

	return total

def sim_phase5_acc(n = 1430000 - 1):
	start = 400000
	total = 0

	for i in range(start, n + 1):
		total = total + sim_phase5_single(i)

	return total

def sim_phase6_acc(n):
	start = 1430000
	total = 0

	for i in range(start, n + 1):
		total = total + sim_phase6_single(i)

	return total

def calc_error(a, b):
	return (a - b)

def find_cutoff_with_current_subsidy(use_shortcut):
	print("Finding cutoff block number and last block emission")

	max_supply = 21000000000 * COIN

	if use_shortcut:
		blockheight = 40000000 + 1
		circulating_supply = 2097598365856027708

	else:
		blockheight = 1430000
		circulating_supply = GENESIS + \
			sim_phase1_acc() + \
			sim_phase2_acc() + \
			sim_phase3_acc() + \
			sim_phase4_acc() + \
			sim_phase5_acc()

	while True:
		subsidy_block = sim_phase6_single(blockheight)

		if circulating_supply + subsidy_block >= max_supply:
			print("Cutoff at block height {} with emission of {}".format(blockheight, max_supply - circulating_supply))
			break

		circulating_supply = circulating_supply + subsidy_block
		if blockheight % 10000000 == 0: print("height = {}, circulating_supply = {}".format(blockheight, circulating_supply))

		blockheight = blockheight + 1

	seconds_until_block = (blockheight - LAST_KNOWN_BLOCK['height']) * BLOCK_TIME
	expected_block_timestamp = seconds_until_block + LAST_KNOWN_BLOCK['time']

	print("Expected timestamp of block {}: {}".format(blockheight, expected_block_timestamp))


def check():
	print("Single picks (math):")
	print('math_phase1_single(1000):    {}'.format(math_phase1_single(1000)))
	print('math_phase2_single(2000):    {}'.format(math_phase2_single(2000)))
	print('math_phase3_single(10000):   {}'.format(math_phase3_single(10000)))
	print('math_phase4_single(100000):  {}'.format(math_phase4_single(100000)))
	print('math_phase5_single(1000000): {}'.format(math_phase5_single(1000000)))
	print('math_phase6_single(5000000): {}'.format(math_phase6_single(5000000)))

	print("\nAccumulated (math):")
	print('math_phase1_acc(1000):       {}'.format(math_phase1_acc(1000)))
	print('math_phase2_acc(2000):       {}'.format(math_phase2_acc(2000)))
	print('math_phase3_acc(10000):      {}'.format(math_phase3_acc(10000)))
	print('math_phase4_acc(100000):     {}'.format(math_phase4_acc(100000)))
	print('math_phase5_acc(1000000):    {}'.format(math_phase5_acc(1000000)))
	print('math_phase6_acc(5000000):    {}'.format(math_phase6_acc(5000000)))

	print("\nSingle picks (sim):")
	print('sim_phase1_single(1000):    {}'.format(sim_phase1_single(1000)))
	print('sim_phase2_single(2000):    {}'.format(sim_phase2_single(2000)))
	print('sim_phase3_single(10000):   {}'.format(sim_phase3_single(10000)))
	print('sim_phase4_single(100000):  {}'.format(sim_phase4_single(100000)))
	print('sim_phase5_single(1000000): {}'.format(sim_phase5_single(1000000)))
	print('sim_phase6_single(5000000): {}'.format(sim_phase6_single(5000000)))

	print("\nAccumulated (sim):")
	print('sim_phase1_acc(1000):       {}'.format(sim_phase1_acc(1000)))
	print('sim_phase2_acc(2000):       {}'.format(sim_phase2_acc(2000)))
	print('sim_phase3_acc(10000):      {}'.format(sim_phase3_acc(10000)))
	print('sim_phase4_acc(100000):     {}'.format(sim_phase4_acc(100000)))
	print('sim_phase5_acc(1000000):    {}'.format(sim_phase5_acc(1000000)))
	print('sim_phase6_acc(5000000):    {}'.format(sim_phase6_acc(5000000)))	

	print("\nErrors (single):")
	print('e(phase1_single) =          {}'.format(calc_error(math_phase1_single(1000), sim_phase1_single(1000))))
	print('e(phase2_single) =          {}'.format(calc_error(math_phase2_single(2000), sim_phase2_single(2000))))
	print('e(phase3_single) =          {}'.format(calc_error(math_phase3_single(10000), sim_phase3_single(10000))))
	print('e(phase4_single) =          {}'.format(calc_error(math_phase4_single(100000), sim_phase4_single(100000))))
	print('e(phase5_single) =          {}'.format(calc_error(math_phase5_single(1000000), sim_phase5_single(1000000))))
	print('e(phase6_single) =          {}'.format(calc_error(math_phase6_single(5000000), sim_phase6_single(5000000))))

	print("\nErrors (acc):")
	print('e(phase1_acc) =             {}'.format(calc_error(math_phase1_acc(1000), sim_phase1_acc(1000))))
	print('e(phase2_acc) =             {}'.format(calc_error(math_phase2_acc(2000), sim_phase2_acc(2000))))
	print('e(phase3_acc) =             {}'.format(calc_error(math_phase3_acc(10000), sim_phase3_acc(10000))))
	print('e(phase4_acc) =             {}'.format(calc_error(math_phase4_acc(100000), sim_phase4_acc(100000))))
	print('e(phase5_acc) =             {}'.format(calc_error(math_phase5_acc(1000000), sim_phase5_acc(1000000))))
	print('e(phase6_acc) =             {}'.format(calc_error(math_phase6_acc(5000000), sim_phase6_acc(5000000))))


if __name__ == '__main__':
	use_shortcut = False
	check()
	find_cutoff_with_current_subsidy(use_shortcut)
