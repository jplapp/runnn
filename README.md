# runnn
run neural networks

yet another runner for neural network training

Core Ideas:
- support multiple workers
- params are stored together with final test score
- support parameter search (sampling, grid search)
- analyze data with sql (no log files)

### Usage

run a script 10 times
`python3 server.py run _command_ --tag=test_run --num_iters=10`

start a worker
`python3 client.py`

check scores
`python3 server.py get_scores --tag=test_run`

analyze results
`python3 server.py sql --cmd 'SELECT log FROM tasks WHERE id_task = 47'`

`python3 server.py sql --cmd 'SELECT log FROM tasks WHERE score > 0.8'`

`python3 server.py sql --cmd 'SELECT score FROM tasks WHERE id_run = 15 and cmd LIKE "%learning_rate=0.001%"'`
Results will be printed to the console. Any sql query is possible!

### credits

inspired by https://github.com/haeusser/NebuLight and https://github.com/haeusser/runjob

