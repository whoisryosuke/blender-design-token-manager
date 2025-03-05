bl_info = {
    "name": "Design Token Manager",
    "description": "Manage design tokens in Blender and use them in materials",
    "author": "whoisryosuke",
    "version": (0, 0, 1),
    "blender": (2, 80, 0), # not sure if this is right
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
    name = StringProperty(
        name="Name",
        description="The name of the token you want to create",
    )
    value = FloatVectorProperty(
        name="Value",
        description="The value of the token you want to create",
        subtype='COLOR'
    )
    token_type = EnumProperty(
        name = "Type",
        description = "The type of token (color, typography, etc)",
        items=new_token_type_items
        )
    number = IntProperty(default=42)


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
class GI_MIDIInputPanel(bpy.types.Panel):
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
        
        # Legacy: Install deps using pip - we keep deps as git submodules now
        # row = layout.row()
        # row.operator("wm.install_midi")

        layout.label(text="Tokens")
        row = layout.row()

        row.template_list("UI_UL_list", "token_collection", token_props, "token_map", token_props, "active_token_id")
        row = layout.row()

        # Create a new token panel
        if not token_props.new_token_mode:
            row.operator("wm.toggle_token_create")

        if token_props.new_token_mode:
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
        tokens = props.tokens
        token_map = props.token_map

        # New token data
        name = props.new_token_name
        token_type = props.new_token_type
        token_value = props.new_token_value

        # Add to collection
        new_collection_item = token_map.add()
        new_collection_item.name = name
        new_collection_item.token_type = token_type
        new_collection_item.value = token_value

        return {"FINISHED"}
    

class GI_create_node_group(bpy.types.Operator):
    """Create node group"""
    bl_idname = "wm.create_node_group"
    bl_label = "Create node group"
    bl_description = "Adds a node with all design tokens"

    def execute(self, context: bpy.types.Context):
        props = context.scene.token_props
        token_map = props.token_map

        # create a group
        node_group = bpy.data.node_groups.new('testGroup', 'ShaderNodeTree')

        # create group inputs
        group_inputs = node_group.nodes.new('NodeGroupInput')
        group_inputs.location = (-350,0)

        # Create nodes
        new_node = node_group.nodes.new('ShaderNodeRGB')
        print("Created new RGB node")
        print(dir(new_node))
        print("RGB node color")
        print(new_node.color)
        print(new_node.outputs[0].default_value)
        new_node.outputs[0].default_value[0] = 0.0
        new_node.outputs[0].default_value[1] = 0.0
        new_node.outputs[0].default_value[2] = 1.0
        

        # group_inputs.inputs.new('NodeSocketFloat','in_to_greater')
        # group_inputs.inputs.new('NodeSocketFloat','in_to_less')

        # create group outputs
        group_outputs = node_group.nodes.new('NodeGroupOutput')
        print("Created node outputs")
        print(dir(group_outputs))
        group_outputs.location = (300,0)
        output_name = "Color Output"
        node_group.interface.new_socket(name=output_name, in_out='OUTPUT')

        # Connect nodes
        print("Connecting nodes")
        # print(group_outputs.inputs.keys())
        node_group.links.new(new_node.outputs[0], group_outputs.inputs[output_name])

        return {"FINISHED"}


# Load/unload addon into Blender
classes = (
    DesignTokenCollectionItem,
    GI_SceneProperties,
    GI_MIDIInputPanel,
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
