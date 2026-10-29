#!/usr/bin/env python3
import os
import re
import sys
import shutil
import subprocess
import yaml
from datetime import datetime

UPLOAD = '../yaml/upload.yaml'
REPO = '../'
URL_SAFE = re.compile(r"^[A-Za-z0-9._/-]+$")


def option(name):
  if name in sys.argv:
    i = sys.argv.index(name)
    value = sys.argv[i + 1]
    del sys.argv[i:i + 2]
    return value
  return None


def sourceDir(entry, stage):
  source = entry['source']
  if source.startswith('__STAGE__'):
    if not stage:
      sys.exit(f"{entry['name']}: no stage folder (stage in upload.yaml or --stage)")
    return os.path.join(stage, source[len('__STAGE__'):].lstrip('/'))
  return os.path.join(REPO, source)


def unsafeNames(path):
  bad = []
  for root, _, files in os.walk(path):
    for name in files:
      rel = os.path.relpath(os.path.join(root, name), path)
      if not URL_SAFE.match(rel):
        bad.append(rel)
  return bad


def target(remote, entry):
  return remote.rstrip('/') + ('/' + entry['folder'] if entry['folder'] else '')


def upload(entry, remote, stage, go, replace, log):
  name = entry['name']
  path = sourceDir(entry, stage)
  if not os.path.isdir(path):
    print(f"== {name}: no folder {path}, skipped")
    return
  bad = unsafeNames(path)
  if bad:
    sys.exit(f"{name}: not url-safe, nothing uploaded:\n  " + '\n  '.join(sorted(bad)[:50]))
  for files in entry['files']:
    print(f"== {name}: {files['include']} ({files['type']}) -> {target(remote, entry)}")
    command = ['rclone', 'copy', path, target(remote, entry),
      '--include', files['include'],
      '--header-upload', f"Content-Type: {files['type']}",
      '--header-upload', f"Cache-Control: {entry['cache_control']}",
      '--s3-no-check-bucket',
      '--s3-no-head',
      '--transfers', os.environ.get('DSC_TRANSFERS', '4'),
      '--log-file', log, '--log-level', 'INFO', '--stats-one-line', '--stats', '30s', '--progress']
    if not (entry.get('manual') or replace):
      command.append('--ignore-existing')
    if os.environ.get('DSC_ACL'):
      command += ['--s3-acl', os.environ['DSC_ACL']]
    if not go:
      command.append('--dry-run')
    subprocess.run(command, check=True)


def check(entry, remote, stage, log):
  name = entry['name']
  path = sourceDir(entry, stage)
  if not os.path.isdir(path):
    return True
  print(f"== check {name}")
  command = ['rclone', 'check', path, target(remote, entry), '--one-way', '--size-only',
    '--s3-no-check-bucket', '--log-file', log, '--log-level', 'INFO']
  for files in entry['files']:
    command += ['--include', files['include']]
  return subprocess.run(command).returncode == 0


def main():
  go = '--go' in sys.argv
  if go:
    sys.argv.remove('--go')
  replace = '--replace' in sys.argv
  if replace:
    sys.argv.remove('--replace')
  with open(UPLOAD) as fp:
    plan = yaml.safe_load(fp)
  remote = option('--remote') or plan.get('remote')
  stage = option('--stage') or plan.get('stage')
  names = sys.argv[1:]
  if not names:
    sys.exit(open(__file__).read().split('\nimport ')[0])
  if not remote:
    sys.exit('no remote (remote in upload.yaml or --remote)')
  if shutil.which('rclone') is None:
    sys.exit('rclone is not installed (sudo apt install rclone)')
  remotes = subprocess.run(['rclone', 'listremotes'], capture_output=True, text=True).stdout.split()
  if remote.split(':')[0] + ':' not in remotes:
    sys.exit(f"no rclone remote {remote.split(':')[0]}: (rclone config)")

  folders = plan['folders']
  known = [e['name'] for e in folders]
  for name in names:
    if name not in known + ['all', 'check']:
      sys.exit(f"unknown {name} (known: {', '.join(known)}, all, check)")
  log = f"upload-{datetime.now():%Y%m%d-%H%M%S}.log"
  for entry in folders:
    if 'check' in names:
      check(entry, remote, stage, log)
    elif entry['name'] in names or ('all' in names and not entry.get('manual')):
      if entry.get('manual') and go:
        missing = [e['name'] for e in folders if not e.get('manual') and not check(e, remote, stage, log)]
        if missing:
          sys.exit(f"{entry['name']}: not uploaded, the bucket does not hold all of {', '.join(missing)} yet")
      upload(entry, remote, stage, go, replace, log)
  if not go:
    print('dry run: nothing uploaded (add --go)')
  print(f"log: {log}")


if __name__ == '__main__':
  main()
