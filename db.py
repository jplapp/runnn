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

ONLINE = 'online'
SHUTDOWN = 'shutdown'

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
      'CREATE TABLE IF NOT EXISTS result_info (ID_task INTEGER,name, value);')

    c.execute(
      'CREATE TABLE IF NOT EXISTS clients (ID_client PRIMARY KEY, last_online, status, gpu_string, next_action);')

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

  def update_task(self, id_task, client_name, status, log='', score=0):
    def update(c):
      c.execute("UPDATE tasks SET status=?, log=?, changed=(DATETIME('now')), score=?, ID_client=? WHERE ID_task=?",
                  (status, log, score, client_name, id_task))
    self._run(update)

  def add_task_result_info(self, id_task, info):
    """ info is a dict with info[name] = value"""
    values_to_insert = []
    for key, value in info.items():
      values_to_insert.append([id_task, key, value])

    def update(c):
      c.executemany("""
          INSERT INTO result_info (ID_task, name, value) VALUES (?, ?, ?)""", values_to_insert)

    self._run(update)


  def get_scores(self, run_tag=None, id_run=None):
    def get_scores_with_tag(c):
      c.execute("SELECT ID_task, score from tasks, runs WHERE tasks.ID_run = runs.ID_run AND runs.tag = ? ORDER BY score ASC", (run_tag,))
      return c.fetchall()

    def get_scores_by_id(c):
      c.execute("SELECT ID_task, score from tasks WHERE tasks.ID_run = ? ORDER BY score ASC", (id_run,))
      return c.fetchall()

    if run_tag is not None:
      return self._run(get_scores_with_tag)
    elif id_run is not None:
      return self._run(get_scores_by_id)
    else:
      return 'please provide either a run_id or a run_tag'




  # clients

  def set_client_status(self, name, status, gpu_string):
    def set_client(c):
      c.execute('REPLACE INTO clients (ID_client, last_online, status, gpu_string) VALUES (?, (DATETIME("now")), ?,?)', (name, status, gpu_string))

    self._run(set_client)

  def update_client(self, name, next_action=None):
    def update(c):
      c.execute('UPDATE clients SET next_action=? WHERE ID_client=?', (next_action, name))

    return self._run(update)

  def check_action(self, name):
    def check(c):
      c.execute('SELECT next_action FROM clients WHERE ID_client=?', (name,))
      return c.fetchone()

    def update(c):
      c.execute('UPDATE clients SET next_action="" WHERE ID_client=?', (name,))

    result = self._run(check)
    self._run(update)
    return result

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


