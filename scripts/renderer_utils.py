import sys
import os
from raw_utils import read_raw
import subprocess
from scene import *

def get_renderer_folder():
    return "./build/renderer/Release/"

def get_renderer_executable():
    if os.name == 'nt':
        return "renderer.exe"
    else:
        return "renderer"
       
def start_renderer(scene=None, output=None, frames=None, time=None, no_display=False, renderer_folder=None):
    old = os.getcwd()
    if renderer_folder is None:
        renderer_folder = get_renderer_folder();
    os.chdir(renderer_folder)
    command = [get_renderer_executable()]    
    if scene is not None:
        command += ["temp_scene.xml"]
        scene.dump("temp_scene.xml")
    if output is None:
        output = "temp_render.raw"
    command += ["-o", output]
    if frames is not None:
        command += ["-f", str(frames)]
    if time is not None:
        command += ["-t", str(time)]
    if no_display:
        command += ["--no-display"]
    subprocess.call(command)
    numpy_data = None
    if frames is not None or time is not None:
        numpy_data = read_raw(output)
    os.chdir(old)
    return numpy_data