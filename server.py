#!/usr/bin/env python3

from __future__ import print_function
import argparse

import db
import numpy as np

data = db.DB()

# simple actions that are just sql commands
sql_actions = {
  'show_clients': 'SELECT * FROM clients',
  'good_runs': 'SELECT runs.*, '
                  '100. * (select count(*) from tasks as t3 where t3.id_run = runs.id_run and score > 0.95) '
                   '/ (select count(*) from tasks as t2 where t2.id_run = runs.id_run and score > 0) as good_run_percentage '
                'FROM runs GROUP BY runs.id_run',
  'count_runs': 'SELECT runs.*, count(tasks.score) FROM runs, tasks WHERE runs.id_run = tasks.id_run AND score > 0.1 GROUP BY runs.id_run',
}


# more complex actions that require a function
def add_run(args):
  data.add_run(args.tag, args.cmd, args.params, args.num_iters)


def kill_client(args):
  data.update_client(args.action[1], next_action='shutdown')


def get_scores(args):
  """
  Get all scores of a run
  :param args:
  :return:
  """
  scores = data.get_scores(args.tag, args.run_id)
  data.pretty_print(('ID_task', 'score'), scores)


def run_sql(args):
  data.execute(args.action[1])


def list_actions(_=0):
  for a in list(actions.keys()) + list(sql_actions.keys()):
    print(a)


def hp_random_search(args):
  """
  randomly search for good hyperparameters
  starts --num_runs training runs with --num_iters tasks each
  randomly samples hyperparameters, that are provided in a file
  all runs will have the same tag
  """
  import yaml

  param_ranges = yaml.load(open(args.action[1]))

  def sample_params(config):
    params = []
    for key, values in config.items():
      value = np.random.choice(values)
      params.append([key, value])
    return params

  base_cmd = args.cmd

  for i in range(args.num_runs):

    # sample parameters
    p = sample_params(param_ranges)
    cmd = base_cmd
    for [k, v] in p:
      cmd += ' --{}={}'.format(k, v)

    args.cmd = cmd  # todo: mutating args is probably not the best idea

    add_run(args)




actions = {
  'actions': list_actions,
  'run': add_run,
  'get_scores': get_scores,
  'sql': run_sql,
  'kill_client': kill_client,
  'search_hps': hp_random_search
}

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument("action", nargs='*')

  parser.add_argument("--tag", help="Tag", default=None)
  parser.add_argument("--run_id", help="Id of the run", type=int, default=None)
  parser.add_argument("--cmd", help="Command to use", default='train.py')
  parser.add_argument("--params", help="Params for the command", default='')
  parser.add_argument("--num_iters", help="How often the command should be repeated", type=int, default=20)
  parser.add_argument("--num_runs", help="How many runs should be started", type=int, default=1)

  args = parser.parse_args()

  if len(args.action) == 0:
    print('please specify an action, should be in')
    list_actions()
  else:
    action = args.action[0]
    if action in actions:
      actions[action](args)
    elif action in sql_actions:
      data.execute(sql_actions[action])
    else:
      print('unknown action ', action)
