#   Copyright 2012 David Malcolm <dmalcolm@redhat.com>
#   Copyright 2012 Red Hat, Inc.
#
#   This is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.

from collections import OrderedDict, namedtuple
import re
import urllib

class NewBug:
    def __init__(self, product, version, component, summary, comment, blocked, bug_file_loc=None):
        self.product = product
        self.version = version
        self.component = component
        self.summary = summary
        self.comment = comment
        self.blocked = blocked
        self.bug_file_loc = bug_file_loc # appears as "URL"

    def make_url(self):
        query = OrderedDict()
        query['product'] = self.product
        query['version'] = self.version
        query['component'] = self.component
        query['short_desc'] = self.summary
        query['comment'] = self.comment
        query['blocked'] = self.blocked
        query['bug_file_loc'] = self.bug_file_loc

        fields = urllib.urlencode(query, True)
        return 'https://bugzilla.redhat.com/enter_bug.cgi?%s' % fields

class Srpm(namedtuple('Srpm',
                      ('name', 'version', 'release'))):
    def __str__(self):
        return '%s-%s-%s' % (self.name, self.version, self.release)

class BugReport(namedtuple('BugReport',
                           ('srpm', 'id', 'url'))):
    def get_status(self):
        return ('bug already filed for %s (%s)'
                % (self.srpm,
                   'https://bugzilla.redhat.com/show_bug.cgi?id=%i'
                   % self.id))

class Unreported(namedtuple('Unreported',
                           ('srpm', 'notes'))):
    def get_status(self):
        return 'bug not filed for %s (%s)' % (self.srpm, self.notes)

class BugReportDb:
    def __init__(self):
        self.statuses = []
        with open('bugreports.txt') as f:
            for line in f:
                # Skip comment lines:
                if line.startswith('#'):
                    continue
                line = line.strip()
                if line == '':
                    continue
                m = re.match('^(\S+)-(\S+)-(\S+)\s+rhbz#([0-9]+)\s+(\S+)$', line)
                if m:
                    # print(m.groups())
                    srpm = Srpm(*(m.groups()[0:3]))
                    self.statuses.append(BugReport(srpm=srpm,
                                               id=int(m.group(4)),
                                               url=m.group(5)))
                    continue

                m = re.match('^(\S+)-(\S+)-(\S+)\s+(.+)$', line)
                if m:
                    # print(m.groups())
                    srpm = Srpm(*(m.groups()[0:3]))
                    self.statuses.append(Unreported(srpm=srpm,
                                                    notes=m.group(4)))
                    continue

                raise RuntimeError('unparsed line in bugreports.txt: %r' % line)
        if 0:
            from pprint import pprint
            pprint(self.statuses)

    def find(self, srpmname):
        result = []
        for status in self.statuses:
            if srpmname == status.srpm.name:
                result.append(status)
        return result

def main():
    # Test code: open the user's webbrowser to a page with various fields
    # prepopulated, for manual review.
    bug = NewBug(product='Fedora',
                 version='rawhide',
                 component='python-krbV', # arbitrary component
                 summary='This is the summary',
                 comment='This is a comment\n\nSo is this',
                 blocked=['cpychecker'])
    url = bug.make_url()
    import webbrowser
    webbrowser.open(url)

if __name__ == '__main__':
    main()
