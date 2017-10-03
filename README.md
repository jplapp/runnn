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
`python server.py run _command_ --tag=test_run --num_iters=10`

start a worker
`python client.py`

check scores
`python server.py get_scores --tag=test_run`


inspired by https://github.com/haeusser/NebuLight and https://github.com/haeusser/runjob

