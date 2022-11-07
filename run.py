
import json
import os
import sys
import time

import sh



known_gun_peers = [
  "https://relay.peer.ooo/gun",
  "https://replicant.adamantium.online/gun",
  "http://gun-matrix.herokuapp.com/gun",
  "https://shockblox-gun-server.herokuapp.com/gun",
  "https://mg-gun-manhattan.herokuapp.com/gun",
  "https://gunmeetingserver.herokuapp.com/gun",
  "https://gun-eu.herokuapp.com/gun",
  "https://gunjs.herokuapp.com/gun",
  "https://myriad-gundb-relay-peer.herokuapp.com/gun",
  "https://gun-armitro.herokuapp.com/",
  "https://fire-gun.herokuapp.com/gun",
  "http://34.101.247.230:8765/gun",
  "https://gun-sashimi.herokuapp.com/gun",
  "https://gun-ams1.cl0vr.co:443/gun",
  "https://gun-manhattan.herokuapp.com/gun",
  "https://us-west.xerberus.net/gun",
  "https://dletta.rig.airfaas.com/gun",
  "https://e2eec.herokuapp.com/gun",
  "https://gun-us.herokuapp.com/gun",
  "https://www.raygun.live/gun"
] # https://github.com/amark/gun/wiki/volunteer.dht

class DckrRunner(object):
  @property
  def gun_server_is_up(self):
   for item in self.get_containers():
    entry = json.loads(item)
    if entry.get('Image') == 'gunrunner/gundb' and entry.get('Ports') == '0.0.0.0:8765->8765/tcp':
      if not hasattr(self, 'server_container_id'):
        self.server_container_id = entry.get('ID')
      return True
    return False

  def get_dckr_images(self):
    return [x.strip() for x in sh.docker.image.ls('--format', '{{json .}}').strip().split('\n')]

  def get_containers(self):
    return [x.strip() for x in sh.docker.container.ls('--format', '{{json .}}').strip().split('\n')]

  def build_gunserver(self):
    dckr_image_exists = False
    for line in self.get_dckr_images():
      entry = json.loads(line)
      if entry.get('Repository') == self.gunserver_image_name:
        dckr_image_exists = True
    if not dckr_image_exists:
      sh.docker.build('.',  '-t', self.gunserver_image_name, _out=sys.stdout, _cwd='./servers/docker')

  def run_gunserver(self):
    if not self.gun_server_is_up:
      self.server_container_id = sh.docker.run(
        '-d', '--rm', '--name', 'gunrunner', '-p', '8765:8765', self.gunserver_image_name, 
        _cwd=self.server_dir, _bg=True, _env=os.environ
      ).strip()

  def parcel_with_parcelmw(self):
    
    # TEARDOWN INSTRUCTIONS
    print(f'docker stop {self.server_container_id}')
    print("for i in $( ps ax | awk '/[p]arcelserve.js/ {print $1}' ); do kill ${i}; done && ps ax | grep node;")
    npm_install = sh.npm.install
    npm_install(_cwd=self.code_dir, _out=sys.stdout, _bg=False, _env=os.environ)
    sh.npm.run('serve', _cwd=self.code_dir, _bg=True, _out=sys.stdout, _env=os.environ)
    time.sleep(5)
    sh.open("http://localhost:1234/", _bg=True)
    sh.open("http://localhost:8765/gun", _bg=True)
    # time.sleep(10)
    # sh.docker.stop(container_id)

  def __call__(self):
    self.server_dir = './servers/docker'
    self.code_dir = './packagers/parcel'
    self.gunserver_image_name = 'gunrunner/gundb' # rename it here if you must
    self.build_gunserver()
    self.run_gunserver()
    self.parcel_with_parcelmw()

if __name__ == '__main__':
  dckr = DckrRunner()
  dckr()