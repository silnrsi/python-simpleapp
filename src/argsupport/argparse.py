#!/usr/bin/env python3

import argparse, sys
from argsupport.gooey import GooeyParser
from argsupport.gooey.python_bindings.parameters import gooey_params
from argsupport.gooey.python_bindings.control import choose_hander

argparse_parms = """prog usage description epilog parents formatter_class
                    prefix_chars fromfile_prefix_chars argument_default conflict_handler
                    add_help allow_abbrev exit_on_error""".split()
argument_parms = """dest nargs conts default type choices required help metavar""".split()
gooeyargs_parms = """gooey_options widget""".split()


class ArgumentParser:

    def __init__(self, **kw):
        defaults = {
            'use_cmd_args': True,
        }
        for k, v in defaults.items():
            if k not in kw:
                kw[k] = v
        self.__dict__['kwargs'] = kw.copy()
        self.__dict__['isgooey'] = kw.get('gooey', True)
        base = GooeyParser if self.isgooey else argparse.ArgumenParser
        if self.isgooey and 'prog' in kw and 'program_name' not in kw:
            self.kwargs['program_name'] = kw['prog']
            self.kwargs['show_preview_warning'] = False
        for k in list(kw.keys()):
            if k not in argparse_parms:
                del kw[k]
        self.__dict__['base'] = base(**kw)

    def add_argument(self, *args, **kw):
        for k in list(kw.keys()):
            saveme = k in argument_parms
            if self.isgooey:
                saveme = saveme or k in gooeyargs_parms
            if not saveme:
                del kw[k]
        res = self.base.add_argument(*args, **kw)
        
        if kw.get('required', False) or kw.get('nargs', '?') in '+':
            res.metavar = (getattr(res, 'metavar', None) or res.dest) + '*'

    def parse_args(self, args=None, namespace=None):
        params = gooey_params(**self.kwargs)
        parser_handler = choose_hander(params, self.kwargs.get('cli', args or sys.argv))
        return parser_handler(self, args, namespace)

    def original_parse_args(self, args=None, namespace=None):
        return argparse.ArgumentParser.parse_args(self, args, namespace)

    def __getattr__(self, item):
        return getattr(self.base, item)

    def __setattr__(self, item, val):
        return setattr(self.base, item, val)
