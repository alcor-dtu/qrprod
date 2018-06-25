import xml.etree.cElementTree as ET
import pdb
import subprocess
import shutil
import os

class RayEngineParameters:
    def __init__(self, ray_template, screen_width = 512, screen_height = 512, print_buffer_size = 2000, stack_size = 30000, max_depth = 100, auto_camera=False):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.print_buffer_size = print_buffer_size
        self.stack_size = stack_size
        self.max_depth = max_depth
        self.auto_camera = auto_camera
        self.tree = ET.ElementTree(file = ray_template)
        
    def _set(self, var, value):
        n = self.tree.getroot().findall('.//' + var)
        assert(len(n) == 1)
        n = n[0]
        n.text = str(value)
    
    def dump(self, dest_file):
        self._set('screen_width', self.screen_width)
        self._set('screen_height', self.screen_height)
        self._set('print_buffer_size', self.print_buffer_size)
        self._set('stack_size', self.stack_size)
        self._set('max_depth', self.max_depth)
        val = "true" if self.auto_camera else "false"
        self._set('use_auto_camera', val)    
        self.tree.write(dest_file)
