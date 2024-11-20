#!/usr/bin/env python3

import argparse, sys, os
from gooey import GooeyParser
from gooey.python_bindings.gooey_decorator import defaults as gooey_defaults
from gooey.python_bindings import config_generator, cmd_args
from gooey.gui.util.freeze import getResourcePath

argparse_parms = """prog usage description epilog parents formatter_class
                    prefix_chars fromfile_prefix_chars argument_default conflict_handler
                    add_help allow_abbrev exit_on_error""".split()
argument_parms = """action dest nargs conts default type choices required help metavar""".split()
gooeyargs_parms = """gooey_options widget""".split()


class ArgumentParser:

    def __init__(self, **kw):
        self.__dict__['multiin'] = None
        defaults = {
            'use_cmd_args': True,
            'show_success_modal': False,
            'show_restart_button': False,
            'language_dir': getResourcePath('languages'),
            'image_dir': '::gooey/default',
            #'timing_options': {'show_time_remaining': False}
        }
        for k, v in defaults.items():
            if k not in kw:
                kw[k] = v
        self.__dict__['kwargs'] = kw.copy()
        self.__dict__['isgooey'] = kw.get('gooey', True)
        if '--ignore-gooey' in sys.argv:
            self.__dict__['isgooey'] = False
            sys.argv.remove('--ignore-gooey')
        base = GooeyParser if self.isgooey else argparse.ArgumentParser
        if self.isgooey and 'prog' in kw and 'program_name' not in kw:
            self.kwargs['program_name'] = kw['prog']
        elif 'program_name' not in kw:
            self.kwargs['program_name'] = os.path.basename(sys.argv[0].replace('.py', ''))
        self.kwargs['show_preview_warning'] = False
        for k in list(kw.keys()):
            if k not in argparse_parms:
                del kw[k]
        self.__dict__['base'] = base(**kw)

    def run_gooey(self, args=None, namespace=None):
        parser = self
        cmd_args.parse_cmd_args(parser, args)
        if not self.missing_required():
            return self.get_defaults()
        from gooey.gui import application
        build_spec = config_generator.create_from_parser(parser, sys.argv[0], **self.kwargs)
        application.run(build_spec)
        return None

    def missing_required(self):
        for a in self._actions:
            if a.required or (a.nargs is not None and a.nargs != 0 and a.nargs in '+'):
                if a.default is None:
                    return True
        return False

    def get_defaults(self, namespace=None):
        res = {}
        for a in self._actions:
            if a.default is not None:
                res[a.dest] = a.default
        return argparse.Namespace(**res) if namespace is None else namespace(**res)

    def _get_dest(self, args, kw):
        res = kw.get('dest', None)
        if res is not None:
            return res
        for a in args:
            if a[0] == "-":
                if len(a) > 1 and a[1] == "-":
                    res = a[2:]
                    break
                else:
                    res = a[1:]
            else:       # not optional
                res = a
                break
        if res is not None:
            return res.replace("-", "_")
        return res

    def _get_mult(self, args, kw):
        if args[0][0] == "-":
            return "append" in kw.get('action', '')
        if 'nargs' in kw:
            return kw['nargs'] in "+"

    def add_argument(self, *args, **kw):
        dest = self._get_dest(args, kw)
        ismult = self._get_mult(args, kw)
        if dest == "infile" or dest == 'infiles':
            self.__dict__['multiin'] = ismult
            if 'widget' not in kw:
                kw['widget'] = "MultiFileChooser" if ismult else "FileChooser"
        elif 'widget' not in kw:
            if dest == 'outfile':       # requires infile before outfile
                kw['widget'] = 'DirChooser' if self.multiin else 'FileSaver'
            elif dest == 'outdir':
                kw['widget'] = 'DirChooser'
        for k in list(kw.keys()):
            saveme = k in argument_parms
            if self.isgooey:
                saveme = saveme or k in gooeyargs_parms
            if not saveme:
                del kw[k]
        res = self.base.add_argument(*args, **kw)
        
        if kw.get('required', False) or kw.get('nargs', '?') in '+':
            res.metavar = (getattr(res, 'metavar', None) or res.dest) + '*'
        return res

    def parse_args(self, args=None, namespace=None):
        useargs = args or sys.argv
        if self.isgooey:
            return self.run_gooey()
        else:
            return self.original_parse_args(args=args, namespace=namespace)

    def original_parse_args(self, args=None, namespace=None):
        return argparse.ArgumentParser.parse_args(self, args, namespace)

    def __getattr__(self, item):
        return getattr(self.base, item)

    def __setattr__(self, item, val):
        return setattr(self.base, item, val)
