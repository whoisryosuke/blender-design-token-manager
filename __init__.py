bl_info = {
    "name": "Design Token Manager",
    "description": "Manage design tokens in Blender and use them in materials",
    "author": "whoisryosuke",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Output",
    # "warning": "Make sure to press 'Install dependencies' button in the plugin panel before using", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/whoisryosuke/blender-design-token-manager",
    "tracker_url": "",
    "category": "Development"
}


import bpy
from bpy.props import (StringProperty,
                       FloatProperty,
                       IntProperty,
                       EnumProperty,
                       FloatVectorProperty,
                       BoolProperty,
                       PointerProperty,
                       CollectionProperty,
                       )
from bpy.types import (
                       PropertyGroup,
                       )
import os

# Constants


# Global state

def handle_midi_file_path(midi_file_path):
    fixed_midi_file_path = midi_file_path

    # Relative file path? Lets fix that
    if "//" in midi_file_path:
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        midi_path_base = midi_file_path.replace("//", "")
        fixed_midi_file_path = os.path.join( directory , midi_path_base)
        
    return fixed_midi_file_path
    

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

# Hydrate the enum with a dict constant
def new_token_type_items(scene, context):

    items = []

    keys = TOKEN_TYPES.keys()

    for key in keys:
        items.append((key, TOKEN_TYPES[key], ""))
    
    return items

# UI properties
TOKEN_TYPES = {
    "COLOR": "Color",
    "TYPOGRAPHY": "Color",
}

class DesignTokenCollectionItem(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="The name of the token you want to create",
    )
    value: FloatVectorProperty(
        name="Value",
        description="The value of the token you want to create",
        subtype='COLOR',
        min=0.0,
        max=1.0,
    )
    token_type: StringProperty(
        name = "Type",
        description = "The type of token (color, typography, etc)",
        )
    number: IntProperty(default=42)


class GI_SceneProperties(PropertyGroup):
        
    # New token
    new_token_mode: BoolProperty(
        name = "New Token Mode",
        description = "Lets user add new token via panel",
        default = False,
        )
    new_token_name: StringProperty(
        name="Name",
        description="The name of the token you want to create",
    )
    new_token_value: FloatVectorProperty(
        name="Value",
        description="The value of the token you want to create",
        subtype='COLOR',
        min=0.0,
        max=1.0,
    )
    new_token_type: EnumProperty(
        name = "Type",
        description = "The type of token (color, typography, etc)",
        items=new_token_type_items
        )
    
    # midi_file: StringProperty(
    #     name="MIDI File",
    #     description="Music file you want to import",
    #     subtype = 'FILE_PATH'
    #     )
    # action_advanced_mode: BoolProperty(
    #     name = "Advanced Mode",
    #     description = "Lets you add an action per note (instead of 1 for all)",
    #     default = False,
    #     )
    # direction: EnumProperty(
    #     name = "Direction",
    #     description = "Do the objects move up or down?",
    #     items=[ ('down', "Down", ""),
    #             ('up', "Up", ""),
    #           ]
    #     )
    # speed: FloatProperty(
    #         name = "Speed",
    #         description = "Controls the tempo by this rate (e.g. 2 = 2x slower, 0.5 = 2x faster)",
    #         default = 1.0,
    #         min = 0.01,
    #         max = 100.0
    #     )

    # MIDI Keys
    # obj_jump: PointerProperty(
    #     name="Jumping Object",
    #     description="Object that 'jumps' between key objects",
    #     type=bpy.types.Object,
    #     )
    
    token_map: CollectionProperty(type=DesignTokenCollectionItem)
    active_token_id: IntProperty(min=-1,default=-1)
    
    # App State (not for user)
    # tokens = []

# UI Panel
class GI_TokenManagerPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_category = "Design"
    bl_label = "Design Token Manager"
    bl_idname = "SCENE_PT_design_token_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    # bl_context = "output"
    
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        token_props = scene.token_props

        layout.label(text="Tokens")

        row = layout.row()
        row.template_list("UI_UL_list", "token_collection", token_props, "token_map", token_props, "active_token_id")

        # Create a new token panel
        if not token_props.new_token_mode:
            row = layout.row()
            row.operator("wm.toggle_token_create")

        if token_props.new_token_mode:
            row = layout.row()
            layout.label(text="Create New Token")
            row = layout.row()
            row.prop(token_props, "new_token_name")
            row = layout.row()
            row.prop(token_props, "new_token_type")
            row = layout.row()
            row.prop(token_props, "new_token_value")
            row = layout.row()
            row.operator("wm.create_new_token")

        row = layout.row()
        row.operator("wm.create_node_group")

        # row.prop(token_props, "midi_file")

        # layout.separator(factor=1.5)
        # layout.label(text="Animation Settings", icon="IPO_ELASTIC")

        # Button
        # row.operator("wm.delete_all_keyframes", icon="TRASH")


# class GI_assign_keys(bpy.types.Operator):
#     """Test function for gamepads"""
#     bl_idname = "wm.assign_keys"
#     bl_label = "Auto-Assign Keys"
#     bl_description = "Finds piano keys in currently selected collection"

#     def execute(self, context: bpy.types.Context):
#         token_props = context.scene.token_props

#         for check_obj in context.collection.all_objects:
#             obj_name_split = check_obj.name.split(".")
#             obj_name_key = obj_name_split[-1]
#             for note in midi_note_map:
#                 if note == obj_name_key:
#                     replace_note_obj(token_props, note, check_obj)

#         return {"FINISHED"}

class GI_toggle_token_create(bpy.types.Operator):
    """Toggle new token"""
    bl_idname = "wm.toggle_token_create"
    bl_label = "Toggle Token Creation"
    bl_description = "Reveal the 'New Token' panel"

    def execute(self, context: bpy.types.Context):
        token_props = context.scene.token_props
        
        token_props.new_token_mode = not token_props.new_token_mode;

        return {"FINISHED"}
    
class GI_create_new_token(bpy.types.Operator):
    """Toggle new token"""
    bl_idname = "wm.create_new_token"
    bl_label = "Create token"
    bl_description = "Saves token to Blender file"

    def execute(self, context: bpy.types.Context):
        props = context.scene.token_props
        token_map = props.token_map

        # New token data
        name = props.new_token_name
        token_type = props.new_token_type
        token_value = props.new_token_value

        # Add to collection
        print("Creating collection for token")
        # TODO: Check for existing first
        new_collection_item = token_map.add()
        new_collection_item.name = name
        new_collection_item.token_type = token_type
        # new_collection_item.value = token_value.hsv
        print("Value:")
        print(token_value)
        new_collection_item.value = token_value

        return {"FINISHED"}

COLOR_NODE_TYPES = {
    'SHADER': 'ShaderNodeRGB',
    'GN': 'FunctionNodeInputColor'
}    

def create_node_group(node_group_type, name):
    # Create node group
    # TODO: Check for existing first
    node_group = bpy.data.node_groups.new(name, node_group_type)

    # create group inputs
    group_inputs = node_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-350,0)

    # create group outputs
    group_outputs = node_group.nodes.new('NodeGroupOutput')
    print("Created node outputs")
    print(dir(group_outputs))
    group_outputs.location = (300,0)

    return (node_group, group_inputs, group_outputs)

def generate_color_tokens(node_type, token_map, node_group, group_outputs):
    node_offset_y = 0
    for token in token_map:
        # Create an output (color in this case)
        node_group.interface.new_socket(name=token.name, socket_type="NodeSocketColor", in_out='OUTPUT')

        # Create nodes

        # Debug
        # print("token:")
        # print(token)
        # print("Created new RGB node")
        # print(token.name)
        # print(token.token_type)
        # print("RGB node color")
        # print(token.value)
        # print(token.value.r)

        # Create Color/RGB node
        # Shaders and geo nodes use different nodes for color (see `COLOR_NODE_TYPES`)
        new_node = node_group.nodes.new(COLOR_NODE_TYPES[node_type])
        new_node.location = (100, node_offset_y)
        new_node.name = token.name

        if(node_type == "SHADER"):
            new_node.outputs[0].default_value[0] = token.value.r
            new_node.outputs[0].default_value[1] = token.value.g
            new_node.outputs[0].default_value[2] = token.value.b
        if(node_type == "GN"):
            new_node.value[0] = token.value.r
            new_node.value[1] = token.value.g
            new_node.value[2] = token.value.b

        # connect node to output
        node_group.links.new(new_node.outputs[0], group_outputs.inputs[token.name])

        # Push next node down so they don't overlap
        node_offset_y -= 200



class GI_create_node_group(bpy.types.Operator):
    """Create node groups"""
    bl_idname = "wm.create_node_group"
    bl_label = "Create node group"
    bl_description = "Adds a node group to shaders and geometry nodes with all design tokens"

    def execute(self, context: bpy.types.Context):
        props = context.scene.token_props
        token_map = props.token_map

        # Create shader node group
        (node_group, _, group_outputs) = create_node_group('ShaderNodeTree', 'Design Tokens (Shader)')
        generate_color_tokens('SHADER', token_map, node_group, group_outputs)

        # Create geometry node group
        (node_group, _, group_outputs) = create_node_group('GeometryNodeTree', 'Design Tokens (GN)')
        generate_color_tokens('GN', token_map, node_group, group_outputs)


        return {"FINISHED"}


# Load/unload addon into Blender
classes = (
    DesignTokenCollectionItem,
    GI_SceneProperties,
    GI_TokenManagerPanel,
    GI_toggle_token_create,
    GI_create_new_token,
    GI_create_node_group,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.token_props = PointerProperty(type=GI_SceneProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
