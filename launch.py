# todo move pcs to separate file
import subprocess, time

clients = [
'atcremers14',
'atcremers16',
'atcremers45',
'atcremers48',
'atcremers49',
'atcremers50',
'atcremers51',
'atcremers52',
'atcremers53',
'atcremers54',
'atcremers55',
'atcremers57',
'atcremers58',
'atcremers59',
'atcremers60',
'atcremers61',
'atcremers62',
'atcremers63',
'atcremers64',
'atcremers65',
'atcremers66',
'atcremers75',
'atcremers76',
]

TEMPLATE = "ssh -o StrictHostKeyChecking=no {} bash -c ' cd runnn && killall -9 python3 ; cd runnn && nohup python3 client.py & '"

for client in clients:
   subprocess.Popen(["bash", "-c", TEMPLATE.format(client)])
   print('launched on {}'.format(client))
   time.sleep(2)
