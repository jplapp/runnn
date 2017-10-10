#!/usr/bin/env python3
import argparse
import subprocess
import time
import db

data = db.DB()

SLEEP_TIME = 10  # seconds
SCORE_PREFIX = 'final_score'

name = subprocess.getoutput('hostname')

def register_client():
  # 1) check if we should do sth
  gpu_info = subprocess.getoutput('nvidia-smi')

  action = data.check_action(name)

  print(action)

  if action is not None:
    if action[0] == 'restart':
      print('restarting')
      # todo: restart here
    elif action[0] == 'shutdown':
      data.set_client_status(name, db.SHUTDOWN, gpu_info)
      import sys
      sys.exit()

  # 2) register (or update) client info on db
  data.set_client_status(name, db.ONLINE, gpu_info)


def process_task(gpu):
  task = data.get_task()

  if task is None:
    time.sleep(SLEEP_TIME)
    return

  print('processing task', task)

  cuda_string = 'CUDA_VISIBLE_DEVICES=' + str(gpu)+' '

#(1, 3, None, u'cmd', u'params', u'queued', None, u'2017-10-03 11:10:35', None
  (id_task, id_run, id_client, cmd, params, status, log, changed, score) = task

  data.update_task(id_task, name, db.PROCESSING)

  proc = subprocess.Popen(cuda_string + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  log = []

  while True:
    output = proc.stdout.readline()
    output = output.decode('utf-8')
    if output == '' and proc.poll() is not None:
      break
    if output:
      print('>> ' + output.strip())
      log.append(output.strip())

  rc = proc.poll()

  if rc == 0:
    score_lines = [line for line in log if line.startswith(SCORE_PREFIX)]

    if len(score_lines):
      score = float(score_lines[-1][len(SCORE_PREFIX)+1:])
    else:
      score = 0

    data.update_task(id_task, name, db.DONE, '\n'.join(log), score)
  else:
    data.update_task(id_task, name, db.FAILED, '\n'.join(log))

  time.sleep(1)




if __name__ == '__main__':
    # really not much to do here
    parser = argparse.ArgumentParser()

    parser.add_argument("--gpu", help="GPU ID", default=0, type=int)

    args = parser.parse_args()

    gpu = args.gpu

    while True:
      register_client()
      process_task(gpu)
