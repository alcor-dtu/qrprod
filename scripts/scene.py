import xml.etree.cElementTree as ET
import pdb
import subprocess
import shutil
import os
def get_binary_file(scene_file):
    return scene_file[:-4] + "_binary.xml"

class Scene:
    def __init__(self, scene_file):
         self.tree = ET.ElementTree(file = scene_file)
         self.binary_file = os.path.abspath(get_binary_file(scene_file))

###########################################
#            CAMERA MANIPULATION          #
###########################################

    def _get_main_camera_node(self):
        cameras = self.tree.getroot().findall('.//cameras')
        assert(len(cameras) == 1)
        current_camera_idx = self.tree.getroot().findall('.//current_camera')[0].text
        current_camera_node = cameras[0].find('value' + current_camera_idx)
        return current_camera_node

    def _parse_vector(self,element):
        lst = []
        for s in ["x","y", "z", "w"]:
            found = element.find(s)
            if found is not None:
                lst += [found.text]
        return lst
    
    def _set_vector(self, element, vector):  
        elems = ["x", "y", "z", "w"]  
        for i, e in enumerate(vector):
            found = element.find(elems[i])
            if found is not None:
                found.text = str(e)
            
    def get_camera_eye(self):
        node = self._get_main_camera_node()
        eye = self.tree.getroot().findall('.//eye')[0]
        return self._parse_vector(eye)

    def set_camera_eye(self, new_eye):
        node = self._get_main_camera_node()
        eye = self.tree.getroot().findall('.//eye')[0]
        self._set_vector(eye, new_eye) 

    def get_camera_lookat(self):
        node = self._get_main_camera_node()
        n = self.tree.getroot().findall('.//lookat')[0]
        return self._parse_vector(n)

    def set_camera_lookat(self, new_elem):
        node = self._get_main_camera_node()
        n = self.tree.getroot().findall('.//lookat')[0]
        self._set_vector(n, new_elem) 

    def get_camera_up(self):
        node = self._get_main_camera_node()
        n = self.tree.getroot().findall('.//up')[0]
        return self._parse_vector(n)

    def set_camera_up(self, new_elem):
        node = self._get_main_camera_node()
        n = self.tree.getroot().findall('.//up')[0]
        self._set_vector(n, new_elem) 

    def get_fov(self):
        node = self._get_main_camera_node()
        n = self.tree.getroot().findall('.//vfov')[0]
        return n.text

    def set_fov(self, new_elem):
        node = self._get_main_camera_node()
        n = self.tree.getroot().findall('.//vfov')[0]
        n.text = str(new_elem) 
    
###########################################
#          MATERIAL MANIPULATION          #
###########################################
    def _set_texture_as_file(self, texture_node, new_filename):
        ptr = texture_node.findall('.//ptr_wrapper')[0]
        data = ptr.find("data")
        data.clear()
        mode = ET.Element("mode")
        mode.text = "file"        
        f = ET.Element("file")
        f.text = new_filename
        data.append(mode)
        data.append(f)
        
    def _set_texture_as_color(self, texture_node, color):
        ptr = texture_node.findall('.//ptr_wrapper')[0]
        data = ptr.find("data")
        data.clear()
        mode = ET.Element("mode")
        mode.text = "color"        
        vec = self._create_vector("color", color)
        data.append(mode)
        data.append(vec)
        

    def _get_array_element(self, parent_node, array_name, requested_index):
        m = parent_node.findall('.//' + array_name)
        assert(len(m) == 1)
        m = m[0]
        val = m.find('value' + str(requested_index))
        assert(val is not None)
        return val

    def _get_mesh_node(self, mesh_index):
        return self._get_array_element(self.tree.getroot(), 'meshes', mesh_index)

    def _get_material_node(self, mesh_index, material_index):
        mesh_node = self._get_mesh_node(mesh_index)
        return self._get_array_element(mesh_node, 'materials', material_index)

    def _get_texture_node(self, mesh_index, material_index, texture_index):
        mat = self._get_material_node(mesh_index, material_index)
        return self._get_array_element(mat, 'textures', texture_index)
           
    def _create_vector(self, name, color):
        elems = ["x", "y", "z", "w"]  
        ret = ET.Element(name)
        for i, value in enumerate(color):
            tag = elems[i]
            s = ET.SubElement(ret, tag)
            s.text = str(value)
        return ret

    # Color must be a list with 4 elements in the 0,1 range
    def _set_material_color(self, mesh_index, material_index, texture_index, color):
        texture = self._get_texture_node(mesh_index, material_index, texture_index)
        self._set_texture_as_color(texture, color)
            
    def set_material_ambient_color(self, mesh_index, material_index, color):
        self._set_material_color(mesh_index, material_index, 0, color)

    def set_material_diffuse_color(self, mesh_index, material_index, color):
        self._set_material_color(mesh_index, material_index, 1, color)

    def set_material_specular_color(self, mesh_index, material_index, color):
        self._set_material_color(mesh_index, material_index, 2, color)

    # Texture must be a string
    def _set_material_texture(self, mesh_index, material_index, texture_index, filepath):
        texture = self._get_texture_node(mesh_index, material_index, texture_index)
        self._set_texture_as_file(texture, filepath)
            
    def set_material_ambient_texture(self, mesh_index, material_index, filepath):
        self._set_material_texture(mesh_index, material_index, 0, filepath)

    def set_material_diffuse_texture(self, mesh_index, material_index, filepath):
        self._set_material_texture(mesh_index, material_index, 1, filepath)

    def set_material_specular_texture(self, mesh_index, material_index, filepath):
        self._set_material_texture(mesh_index, material_index, 2, filepath)

    def _set_material_property(self, mesh_index, material_index, property_string, property_value):
        mat = self._get_material_node(mesh_index, material_index)
        ptr = mat.findall('.//' + property_string)[0]
        if isinstance(property_value, float) or isinstance(property_value, str):
            ptr.text = str(property_value)
        elif isinstance(property_value, list):
            self._set_vector(ptr, property_value)
    
    # Monochromatic index of refraction supported, single float
    def set_material_index_of_refraction(self, mesh_index, material_index, ior):
        self._set_material_property(mesh_index, material_index, "index_of_refraction", [ior, ior, ior])
        
    def set_material_roughness(self, mesh_index, material_index, val):
        self._set_material_property(mesh_index, material_index, "roughness", val)
    def set_material_absorption(self, mesh_index, material_index, val):
        self._set_material_property(mesh_index, material_index, "absorption", val)
    def set_material_scattering(self, mesh_index, material_index, val):
        self._set_material_property(mesh_index, material_index, "scattering", val)
    def set_material_asymmetry(self, mesh_index, material_index, val):
        self._set_material_property(mesh_index, material_index, "asymmetry", val)

    def set_material_selector_texture(self, mesh_index, texture_filename):
        mesh_node = self._get_mesh_node(mesh_index)
        material_sel_tex = mesh_node.findall(".//material_selector")[0]
        self._set_texture_as_file(material_sel_tex, texture_filename)

    def set_environment_map(self, texture_filename):
        miss_program = self.tree.getroot().findall('.//miss_program')[0]
        poly_name = miss_program.find("polymorphic_name")
        assert(poly_name.text == "EnvironmentMap")
        tex = miss_program.findall(".//texture")[0]
        self._set_texture_as_file(tex, texture_filename)
        
    def set_environment_map_as_color(self, color):
        miss_program = self.tree.getroot().findall('.//miss_program')[0]
        poly_name = miss_program.find("polymorphic_name")
        assert(poly_name.text == "EnvironmentMap")
        tex = miss_program.findall(".//texture")[0]
        self._set_texture_as_color(tex, color)

    def dump(self, scene_file):
        self.tree.write(scene_file)
        shutil.copyfile(self.binary_file, get_binary_file(scene_file))



