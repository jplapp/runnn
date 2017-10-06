from __future__ import print_function
import argparse

import db

data = db.DB()

# simple actions that are just sql commands
sql_actions = {
  'show_clients': 'SELECT * FROM clients',
  'good_runs': 'SELECT runs.*, count(tasks.score) FROM runs, tasks WHERE runs.id_run = tasks.id_run and score > 0.95 group by runs.id_run',
  'count_runs': 'SELECT runs.*, count(tasks.score) FROM runs, tasks WHERE runs.id_run = tasks.id_run and score > 0.1 group by runs.id_run',
}


# more complex actions that require a function
def add_run(args):
  data.add_run(args.tag, args.cmd, args.params, args.num_iters)


def kill_client(args):
  data.update_client(args.name, next_action='shutdown')


def get_scores(args):
  """
  Get all scores of a run
  :param args:
  :return:
  """
  scores = data.get_scores(args.tag, args.run_id)
  data.pretty_print(('ID_task', 'score'), scores)


def run_sql(args):
  data.execute(args.cmd)


actions = {
  'run': add_run,
  'get_scores': get_scores,
  'sql': run_sql,
  'kill_client': kill_client
}

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument("action")

  parser.add_argument("--tag", help="Tag", default=None)
  parser.add_argument("--name", help="Name", default=None)
  parser.add_argument("--run_id", help="Id of the run", type=int, default=None)
  parser.add_argument("--cmd", help="Command to use", default='train.py')
  parser.add_argument("--params", help="Params for the command", default='')
  parser.add_argument("--num_iters", help="How often the command should be repeated", type=int, default=20)

  args = parser.parse_args()

  if args.action in actions:
    actions[args.action](args)
  elif args.action in sql_actions:
    data.execute(sql_actions[args.action])
  else:
    print('unknown action ', args.action)
