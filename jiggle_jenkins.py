#!/usr/bin/python
import sys
import math
import getpass
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester
import time
import click

class Helper:
    def __init__(self, url, user, password, use_crumbs):
        self._trace = []
        self._ok_count = 0
        self._disabled_count = 0
        self._rebuilt_count = 0
        self._already_queued_count = 0
        requester = self.get_requester(use_crumbs, url, user, password)
        self._jenkins = Jenkins(baseurl=url, username=user, password=password, requester=requester)
        self._keys = self._jenkins.keys()
        self._idx = -1;
        print('%i project%s...' % (len(self._keys), self._s(len(self._keys))))

    def get_requester(self, use_crumbs, url, username, password):
      if use_crumbs:
        return CrumbRequester(baseurl=url, username=username, password=password)
      return None

    def next(self):
        if self._idx < (len(self._keys) - 1):
            return self._go_next()
        return False

    def get_trace(self):
      return self._trace[:]

    def process_current(self):
        self._trace = []
        if not self._current_project.is_enabled():
            return self._report_disabled()
        self.trace('get last build')
        build = self._current_project.get_last_build()
        self.trace('check status');
        if build.get_status() != 'FAILURE':
            return self._report_ok()
        self.trace('check already queued')
        if self._current_project.is_queued():
            return self._report_already_queued()
        self.trace('kicking off build')
        self._try_invoke_current_project()
        self._current_project.invoke()
        self.trace('reporting rebuilding (:')
        self._report_rebuilt()

    def _try_invoke_current_project(self):
      last_exception = None
      for i in range(0, 5):
        try:
          self._current_project.invoke()
          return
        except Exception as e:
          print('fail: %s' % e)
          last_exception = e
          time.sleep(1)
          pass
      raise last_exception
    def trace(self, message):
        self._trace.append(message)

    def print_stats(self):
        for m in [
                (self._disabled_count, 'Disabled project' + self._s(self._disabled_count)),
                (self._already_queued_count, 'Project' + self._s(self._already_queued_count) + ' already queued for build'),
                (self._ok_count, 'OK project' + self._s(self._ok_count)),
                (self._rebuilt_count, 'Project' + self._s(self._rebuilt_count) + ' queued for rebuild')
                ]:
            print('%i %s' % m)

    def _s(self, i):
        if i == 1:
            return '';
        return 's'

    def _go_next(self):
        self._idx += 1
        k = self._keys[self._idx]
        perc = str(math.ceil(self._idx * 100.0 / float(len(self._keys))))
        if len(perc) < 2:
            perc = ' ' + perc
        perc += '%'
        self._status(perc, k)   
        self._current_project = self._jenkins[k]
        return True
    
    def _status(self, perc, s):
        s = '[' + perc + '] ' + s
        while len(s) < 60:
            s += ' '
        sys.stdout.write(s)

    def _report_ok(self):
        self._ok_count += 1
        print(' [ OK ]')

    def _report_disabled(self):
        self._disabled_count += 1
        print(' [ DISABLED ]')

    def _report_already_queued(self):
        self._already_queued_count += 1
        print(' [ QUEUED ]')

    def _report_rebuilt(self):
        self._rebuilt_count += 1
        print(' [ REBUILT ]')

@click.command()
@click.option('--base-url', default='http://jenkins', help='Base url of your Jenkins server')
@click.option('--auth/--no-auth', default=True, help='Prompt for user credentials')
@click.option('--user', default=None, help='Set or override (if prompting) username')
@click.option('--password', default=None, help='Set password instead of prompting')
@click.option('--use-crumbs/--no-crumbs', default=True, help='Use CrumbRequester')
def main(base_url, auth, user, password, use_crumbs):
  if auth:
    if user is None:
      user = getpass.getuser()
    if password is None:
      password = getpass.getpass()
  helper = Helper(base_url, user, password, use_crumbs)
  while helper.next():
      try:
          helper.process_current()
      except Exception as e:
          print(' [ FAIL ]')
          print('Unable to process current item: %s' % (e))
          print('trace follows:\n\t')
          print('\n\t'.join(helper.get_trace()))
  helper.print_stats()

def oldmain():
    user = getpass.getuser()
    password = getpass.getpass()
    helper = Helper('http://jenkins', user, password)
    while helper.next():
        try:
            helper.process_current()
        except Exception as e:
            print(' [ FAIL ]')
            print('Unable to process current item: %s' % (e))
            print('trace follows:\n\t')
            print('\n\t'.join(helper.get_trace()))
    helper.print_stats()

if __name__ == '__main__':
  main()

