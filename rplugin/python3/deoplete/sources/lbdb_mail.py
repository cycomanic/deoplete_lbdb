import re
import subprocess
from subprocess import CalledProcessError
from .base import Base


class Source(Base):
    COLON_PATTERN = re.compile(r':\s?')
    COMMA_PATTERN = re.compile(r'.+,\s?')
    HEADER_PATTERN = re.compile(r'^(Bcc|Cc|From|Reply-To|To):(\s?.+\s?)')

    def __init__(self, vim):
        super().__init__(vim)

        self.rank = 101  # default is 100, give deoplete-abook priority
        self.name = 'lbdb'
        self.mark = '[lbdb]'
        self.min_pattern_length = 0
        self.filetypes = ['mail']
        self.matchers = ['matcher_full_fuzzy', 'matcher_length']

    def on_init(self, context):
        self.command = context['vars'].get('deoplete#sources#lbdb#command',
                                           ['lbdbq'])

    def get_complete_position(self, context):
        colon = self.COLON_PATTERN.search(context['input'])
        comma = self.COMMA_PATTERN.search(context['input'])
        return max(colon.end() if colon is not None else -1,
                   comma.end() if comma is not None else -1)

    def gather_candidates(self, context):
        ret = self.HEADER_PATTERN.search(context['input'])
        if ret is None:
            return
        retn = ret[2].strip()
        if len(retn) < 3:
            return 
        try:
            cmd = self.command + [retn]
            command_results = subprocess.check_output(cmd, universal_newlines=True).split('\n')
        except CalledProcessError:
            return

        results = []
        for row in command_results[1:]:
            try:
                mail, name, department = row.split('\t')
            except ValueError:
                continue
            results.append({'word': "{0} <{1}>".format(name, mail), 'info': department})
        return results
