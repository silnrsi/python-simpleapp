import os
from argsupport.toml import totoml

def create_pyproject(name, modulepath, **kw):
    res = {}
    res['build-system'] = {'build-backend': "setuptools.build_meta"}
    res['project'] = {'name': name, 'version': kw.get('version', 0.1),
            "classifiers": ["Environment :: Console",
                            "Programming Language :: Python :: 3.8",
                            "Intended Audience :: " + kw.get('audience', "Developers"),
                            "Topic :: " + kw.get("topic", "Text Processing")],
            "requires-python": ">=3.8"}
    if 'license' in kw:
        res['project']['classifiers'].append("License :: "+kw['license']
    res['dependencies'] = kw.get('dependencies', [])
    if 'homepage' in kw:
        res['project.urls'] = {'Home-Page': kw['homepage']}
    res['tool.setuptools.packages.find'] = {
        'where': os.path.relpath(os.path.join(os.path.dirname(modulepath), '..'))
    }
    res['tool.bdist_wheel'] = {"universal": True}
    mname = os.path.splitext(os.path.basename(modulepath))[0]:
    res['projects.scripts'] = {mname: f"{mname}:main"}
    with open("pyproject.toml", "w", encoding="utf-8") as outf:
        outf.write(totoml(res))

def create_module(name, modulepath, **kw):
    template = f"""
import argparse
from argsupport.pipeline import Pipeline, textinfile, textoutfile
from gooey import Gooey

def process(txt, args):
    return txt

@Gooey(program_name="{name}", use_cmd_args=True)
def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("infiles",nargs="+",help="Input file")
    parser.add_argument("-o","--outfile",help="Output file")
    parser.add_argument('-l','--logging',help="Logging level [DEBUG, INFO, WARN, ERROR, number]")
    parser.add_argument('--logfile',default='{name}.log',help='Set logging file')
    args = parser.parse_args(argv)

    Pipeline(args.infiles, args.outfile, args, textinfile, process, textoutfile,
            logging=True, defaultext="_output")

if __name__ == "__main__":
    main()
"""
    mpath = os.path.join("src", os.path.dirname(modulepath))
    os.makedirs(mpath, exist_ok=True)
    with open(os.path.join("src", modulepath+ + ".py"), "w", encoding="utf-8") as outf:
        outf.write(template)
    with open(os.path.join(mpath, "__init__.py"), "w") as outf:
        pass

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name",help="Project name")
    parser.add_argument("module",help="path to module to create from src/")
    args = parser.parse_args(argv)

    create_module(args.name, args.module)
    create_pyproject(args.name, args.module)
