from renderer_utils import *
from ray_tracing_parameters import *
from raw_utils import *
from qr_utils import create_qr_code_image, decode_qr_code_image
import numpy as np
import os

def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
def spherical_to_cartesian(theta, phi):
    return [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)]

def rotate_to_normal(normal, v):
    if normal[2] < -0.999999: 
        vv = np.array((-v[1], -v[0], -v[2]))
        return vv

    a = 1.0/(1.0 + normal[2])
    b = -normal[0]*normal[1]*a
    vv = np.array((1.0 - normal[0]*normal[0]*a, b, -normal[0])) * v[0] + np.array((b, 1.0 - normal[1]*normal[1]*a, -normal[1]))*v[1] + np.array(normal) * v[2]
    return vv

def simulate_scene(scene, ray_parameters, destination_folder, time_per_frame):
    theta_subdiv = 25
    phi_subdiv = 25
    radius = 4
    create_dir(destination_folder)
    positions = []
    pass_test = []

    for i in range(theta_subdiv):
        theta = float(i) / theta_subdiv * np.pi / 2 
        for j in range(phi_subdiv):
            if i == 0 and j > 0:
                continue
            unique_name = "image_%d_%d.png" % (int(float(i) / theta_subdiv * 90) , int(float(j) / phi_subdiv * 360) )
            phi = float(j) / phi_subdiv * np.pi * 2
            pos = np.array(spherical_to_cartesian(theta, phi))
            pos = pos * radius
            positions.append(pos)
            pos = rotate_to_normal([0,1,0], pos)
            print(pos)
            pos = pos.tolist()
            scene.set_camera_eye(pos)
            dest_path = os.path.join(destination_folder, unique_name)
            if not os.path.exists(dest_path):
                start_renderer(scene, ray_parameters, time=time_per_frame, output="image.png")
                image_path = os.path.join(get_renderer_folder(),"image.png")
                shutil.copyfile(image_path, dest_path)
            success, text = decode_qr_code_image(dest_path)
            pass_test.append(success)
            
    positions = np.array(positions)   
    pass_test = np.array(pass_test)     

    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(positions[pass_test,0], positions[pass_test,1], positions[pass_test,2], c='g', s=100)
    ax.scatter(positions[~pass_test,0], positions[~pass_test,1], positions[~pass_test,2], c='r', s=100)
    ax.set_xlim([-radius, radius])
    ax.set_ylim([-radius, radius])
    ax.set_zlim([0, radius])
    
    
scene = Scene("../data/qr_code_only_scene.xml")
scene.set_camera_lookat([0.,0.,0.])
scene.set_camera_up([1., 1.1, 0.])
scene.set_material_diffuse_color(0,0, [0,0,0,0])
scene.set_material_diffuse_color(0,1, [1,1,1,1])
create_qr_code_image("Hello world!", os.path.join(get_renderer_folder(),"qr_code.png"))
scene.set_environment_map_as_color([0.0, 0.0, 0.0, 0.0])
scene.set_material_selector_texture(0, "qr_code.png")
ray_parameters = RayEngineParameters("../data/ray_tracing_parameters.xml", screen_width = 1024, screen_height = 1024)

simulate_scene(scene, ray_parameters, "../results/results_bw", 1.0)

scene_constant = Scene("../data/qr_code_ridged_scene.xml")
scene_constant.set_camera_lookat([0.,0.,0.])
scene_constant.set_camera_up([1., 1.1, 0.])
scene_constant.set_material_diffuse_color(0,0, [1,1,1,1])
scene_constant.set_material_diffuse_color(0,1, [1,1,1,1])
scene_constant.set_material_roughness(0,0, 0.142)
scene_constant.set_material_roughness(0,1, 0.142)
create_qr_code_image("Hello world!", os.path.join(get_renderer_folder(),"qr_code.png"))
scene_constant.set_environment_map_as_color([0.7,0.7,0.7,1.0])
scene_constant.set_material_selector_texture(0, "qr_code.png")

simulate_scene(scene_constant, ray_parameters, "../results/results_ridged_constant", 1.0)

scene_full = Scene("../data/qr_code_ridged_scene.xml")
scene_full.set_camera_lookat([0.,0.,0.])
scene_full.set_camera_up([1., 1.1, 0.])
scene_full.set_material_diffuse_color(0,0, [1,1,1,1])
scene_full.set_material_diffuse_color(0,1, [1,1,1,1])
scene_full.set_material_roughness(0,0, 0.142)
scene_full.set_material_roughness(0,1, 0.142)
create_qr_code_image("Hello world!", os.path.join(get_renderer_folder(),"qr_code.png"))
scene_full.set_environment_map(os.path.abspath("../data/envmap_test.png"))
scene_full.set_material_selector_texture(0, "qr_code.png")

simulate_scene(scene_full, ray_parameters, "../results/results_ridged", 1.0)
