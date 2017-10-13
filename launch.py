# todo move pcs to separate file
import subprocess

clients = [
'atcremers14'
'atcremers16'
'atcremers45'
'atcremers48'
'atcremers49'
'atcremers50'
'atcremers51'
'atcremers52'
'atcremers53'
'atcremers54'
'atcremers55'
'atcremers57'
'atcremers58'
'atcremers59'
'atcremers60'
'atcremers61'
'atcremers62'
'atcremers63'
'atcremers64'
'atcremers65'
'atcremers66'
'atcremers75'
'atcremers76'
]

TEMPLATE = "ssh {} bash -c ' cd runnn && cd runnn && nohup python3 client.py & '"

for client in clients:
   res = subprocess.getoutput(TEMPLATE.format(client))
   print('launched on {}'.format(client), res)