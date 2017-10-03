from __future__  import print_function

import datetime, time
import sqlite3 as sql
from tabulate import tabulate

# Constants.
QUEUED = 'queued'
CANCELLED = 'cancelled'
PROCESSING = 'processing'
DONE = 'done'
FAILED = 'failed'

IDLE_CHECK_INTERVAL_MIN = 0.1


DBNAME = 'runnn_data'


class DB:

  def __init__(self):
    self._create_db()

  def _create_db(self):
    conn = sql.connect(DBNAME, timeout=20)
    c = conn.cursor()
    c.execute(
      'CREATE TABLE IF NOT EXISTS runs (ID_run INTEGER PRIMARY KEY, tag, cmd, params);')

    c.execute(
      'CREATE TABLE IF NOT EXISTS tasks (ID_task INTEGER PRIMARY KEY, ID_run, ID_client, cmd, params, status, log, changed, score);')

    c.execute(
      'CREATE TABLE IF NOT EXISTS clients (ID_client INTEGER PRIMARY KEY, last_online, status, gpu_string);')

    self._commit_and_close(conn, c)

  def _run(self, cmd):
    conn = sql.connect(DBNAME, timeout=20)
    c = conn.cursor()

    result = cmd(c)
    self._commit_and_close(conn, c)

    return result


  def add_run(self, tag, cmd, params, num_iters=20):
    # 1) add to db, get ID

    def add_to_db(c):
      c.execute('INSERT INTO runs (tag, cmd, params) VALUES (?,?,?)', (tag, cmd, params))
      print(c.lastrowid)
      return c.lastrowid

    run_id = self._run(add_to_db)

    # 2) add tasks
    # TODO: expand params

    task_params = params
    def add_task(c):
      c.execute('INSERT INTO tasks(ID_run, cmd, params, status, changed) VALUES (?,?,?,?,(DATETIME("now")))',
                  (run_id, cmd, task_params, QUEUED))

    for i in range(num_iters):
      self._run(add_task)
      time.sleep(0.2)


  def drop_run(self, run_id):
    """
    remove a run using its id
    sets all tasks to cancelled
    """
    def drop_it(c):
      c.execute('UPDATE tasks SET status = ? WHERE ID_run = ?', (CANCELLED, run_id))
    self._run(drop_it)

  def get_task(self):
    def get_tasks(c):
      c.execute("SELECT * FROM tasks WHERE status=? LIMIT 1", (QUEUED,))
      return c.fetchall()

    rows = self._run(get_tasks)

    if len(rows) == 0:
      return None
    else:
      return rows[0]

  def update_task(self, id_task, status, log='', score=0):
    def update(c):
      c.execute("UPDATE tasks SET status=?, log=?, changed=(DATETIME('now')), score=? WHERE ID_task=?",
                  (status, log, score, id_task))
    self._run(update)



  def get_scores(self, run_tag):
    def get_scores(c):
      c.execute("SELECT ID_task, score from tasks, runs WHERE tasks.ID_run = runs.ID_run AND runs.tag = ? ORDER BY score ASC", (run_tag,))
      return c.fetchall()

    return self._run(get_scores)

  def _commit_and_close(self, conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()


  def pretty_print(self, columns, data):
    """

    :param columns: column headers
    :param data: list of entries. should have as many fields as len(columns)
    :return:
    """
    print(tabulate(data, tablefmt='psql'))

  def execute(self, cmd):
    """
    run an arbitrary sql command, and print the result
    :param cmd: 
    :return:
    """
    def f(c):
      c.execute(cmd)
      return c.fetchall()

    self.pretty_print('unknown column headers', self._run(f))



if __name__ == '__main__':
  a = DB()

  #a.add_run('tag','cmd','params')
  a.get_task()


