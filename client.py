#!/usr/bin/env python3
import argparse
import subprocess
import time
import db
import numpy as np

data = db.DB()

SLEEP_TIME = 10  # seconds
PARAM_PREFIX = 'flags:'
SCORE_PREFIX = 'final_score'
RESULT_INFO_PREFIX = '@@'

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


def get_gpu_usage(gpu):
  cur_usage = []
  for i in range(3):
    query = 'nvidia-smi --query-gpu=utilization.gpu --format=csv,nounits,noheader | sed -n "{}p"'.format(gpu+1)

    cur_usage.append(int(subprocess.getoutput(query)))
    time.sleep(1)

  return np.mean(np.asarray(cur_usage))

def get_free_memory(gpu):
  query = 'nvidia-smi --query-gpu=memory.free --format=csv,nounits,noheader | sed -n "{}p"'.format(gpu+1)

  return int(subprocess.getoutput(query))

def process_task(gpu, skip_gpu_check):
  # check GPU usage. If used, wait
  if not skip_gpu_check:  # magic number to just run it
    usage = get_gpu_usage(gpu)
    print('usage', usage)
    if usage > 20:
      time.sleep(SLEEP_TIME)
      return

    free_mem = get_free_memory(gpu)
    print('free gpu memory', free_mem)
  else:
    free_mem = 99999

  task = data.get_task(free_mem)

  if task is None:
    time.sleep(SLEEP_TIME)
    return

  print('processing task', task)

  cuda_string = 'CUDA_VISIBLE_DEVICES=' + str(gpu)+' '

#(1, 3, None, u'cmd', u'params', u'queued', None, u'2017-10-03 11:10:35', None
  (id_task, id_run, id_client, cmd, params, status, log, changed, score) = task

  data.update_task(id_task, name, db.PROCESSING)

  cmd += ' --taskid '+str(id_task)

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
    param_lines = [line for line in log if line.startswith(PARAM_PREFIX)]
    if len(param_lines):
      params = param_lines[-1][len(PARAM_PREFIX)+1:]
    else:
      params = ''

    score_lines = [line for line in log if line.startswith(SCORE_PREFIX)]

    if len(score_lines):
      score = float(score_lines[-1][len(SCORE_PREFIX)+1:])
    else:
      score = 0

    data.update_task(id_task, name, db.DONE, '\n'.join(log), score, params=params)

    # find additional info
    info_lines = [line for line in log if line.startswith(RESULT_INFO_PREFIX)]

    info = dict()
    for line in info_lines:
      try:
        c_ind = line.index(':')
      except ValueError:
        continue

      param_name = line[len(RESULT_INFO_PREFIX):c_ind]
      value = line[c_ind+1:]
      print(param_name, value)
      info[param_name] = value

    data.add_task_result_info(id_task, info)

  else:
    data.update_task(id_task, name, db.FAILED, '\n'.join(log))

    print('exiting client, as task failed', name)
    import sys
    sys.exit()

  time.sleep(1)




if __name__ == '__main__':
    # really not much to do here
    parser = argparse.ArgumentParser()

    parser.add_argument("--gpu", help="GPU ID", default=0, type=int)
    parser.add_argument("--skip_gpu_check", help="Skip check if GPU is available", default=False, type=bool)

    args = parser.parse_args()

    gpu = args.gpu
    skip_gpu_check = args.skip_gpu_check

    while True:
      register_client()
      process_task(gpu, skip_gpu_check)
