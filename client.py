import shlex
import subprocess
import time
import db

data = db.DB()

SLEEP_TIME = 10  # seconds
SCORE_PREFIX = 'final_score'


def register_client():
  """TODO:Implement"""
  2

def process_task():
  task = data.get_task()

  if task is None:
    time.sleep(SLEEP_TIME)
    return

  print('processing task', task)

#(1, 3, None, u'cmd', u'params', u'queued', None, u'2017-10-03 11:10:35', None
  (id_task, id_run, id_client, cmd, params, status, log, changed, score) = task

  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  data.update_task(id_task, db.PROCESSING)

  log = []

  while True:
    output = proc.stdout.readline()
    if output == '' and proc.poll() is not None:
      break
    if output:
      print('>> ' + output.strip())
      log.append(output.strip())

  rc = proc.poll()

  if rc == 0:
    score_lines = [line for line in log if line.startswith(SCORE_PREFIX)]

    if len(score_lines):
      score = float(score_lines[0][len(SCORE_PREFIX)+1:])
    else:
      score = 0

    data.update_task(id_task, db.DONE, '\n'.join(log), score)
  else:
    data.update_task(id_task, db.FAILED, '\n'.join(log))

  time.sleep(1)




if __name__ == '__main__':
    # really not much to do here
    register_client()
    while True:
      process_task()
