#!/usr/bin/env python3

from __future__ import print_function
import argparse

import db

data = db.DB()

# simple actions that are just sql commands
sql_actions = {
  'show_clients': 'SELECT * FROM clients',
  'good_runs': 'SELECT runs.*, count(tasks.score) FROM runs, tasks WHERE runs.id_run = tasks.id_run AND score > 0.95 GROUP BY runs.id_run',
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


actions = {
  'actions': list_actions,
  'run': add_run,
  'get_scores': get_scores,
  'sql': run_sql,
  'kill_client': kill_client
}

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument("action", nargs='*')

  parser.add_argument("--tag", help="Tag", default=None)
  parser.add_argument("--run_id", help="Id of the run", type=int, default=None)
  parser.add_argument("--cmd", help="Command to use", default='train.py')
  parser.add_argument("--params", help="Params for the command", default='')
  parser.add_argument("--num_iters", help="How often the command should be repeated", type=int, default=20)

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
