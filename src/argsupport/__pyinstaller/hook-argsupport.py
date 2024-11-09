from PyInstaller.utils.hooks import collect_data_files
import os

pwd = os.path.join(os.path.dirname(__file__), '..')

datas = [ (pwd + '/gooey/languages/*.json', 'gooey/languages'),
         (pwd + '/gooey/images/*.png', 'gooey/images'),
         (pwd + '/gooey/images/program_icon.*', 'gooey/images') ]
         
