import argparse

import db

data = db.DB()


def add_run(args):
  data.add_run(args.tag, args.cmd, args.params, args.num_iters)


def get_scores(args):
  """
  Get all scores of a run
  :param args:
  :return:
  """
  scores = data.get_scores(args.tag)
  data.pretty_print(('ID_task', 'score'), scores)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("action")

    parser.add_argument("--tag", help="Tag", default='')
    parser.add_argument("--cmd", help="Command to use", default='train.py')
    parser.add_argument("--params", help="Params for the command", default='')
    parser.add_argument("--num_iters", help="How often the command should be repeated", type=int, default=20)


    args = parser.parse_args()


    if args.action == 'run':
      add_run(args)
    elif args.action == 'get_scores':
      get_scores(args)
    else:
      print('unknown action ', args.action)

