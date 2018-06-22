from renderer_utils import *
from raw_utils import *
from qr_generator import create_qr_code_image
import os
print(os.getcwd())

scene = Scene("../data/template_scene_plane.xml")
scene.set_camera_eye([-3.,-2.,-4.])
scene.set_camera_lookat([0.,0.,0.])
scene.set_camera_up([0., -1., 0.])
scene.set_screen_dimensions(1024, 1024)
scene.set_material_ambient_color(0,0, [0,0,0,1])
scene.set_material_diffuse_color(0,0, [1,1,1,1])
scene.set_material_specular_color(0,0, [0,0,0,1])
scene.set_material_roughness(0,0,1.00)
scene.set_material_index_of_refraction(0,0,1.3)
scene.set_material_absorption(0,0, [0.03, 0.03, 0.03])
scene.set_material_scattering(0,0, [1.0, 0.03, 2.0])
scene.set_material_asymmetry(0,0, [0.0, 0.0, 0.00])
scene.set_material_selector_texture(0, "qr_code.png")

create_qr_code_image("Hello world!", os.path.join(get_renderer_folder(),"qr_code.png"))

print(scene.get_camera_eye())
print(scene.get_camera_lookat())
print(scene.get_camera_up())
print(scene.get_fov())
print(scene.get_screen_dimensions())
img = start_renderer(scene, time = 1.0)

save_png("test.png", img)