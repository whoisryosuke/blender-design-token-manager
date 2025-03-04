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
                       EnumProperty,
                       BoolProperty,
                       PointerProperty,
                       )
from bpy.types import (
                       PropertyGroup,
                       )
import math
import subprocess
import sys
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


def selected_track_enum_callback(scene, context):
    global midi_file_loaded, selected_tracks_raw

    token_props = context.scene.token_props
    midi_file_path = token_props.midi_file

    # Check input and ensure it's actually MIDI
    is_midi_file = ".mid" in midi_file_path
    # TODO: Return error to user somehow??
    if not is_midi_file:
        return []
        

    # Have we already scanned this file? Check the "cache"
    if midi_file_loaded == midi_file_path:
        return selected_tracks_raw

    # Import the MIDI file
    from mido import MidiFile

    fixed_path = handle_midi_file_path(midi_file_path)
    mid = MidiFile(fixed_path)

    # Setup time for track
    selected_tracks_raw = []
    time = 0
    # current_frame = context.scene.frame_current
    scene_start_frame = context.scene.frame_start
    scene_end_frame = context.scene.frame_end
    total_frames = scene_end_frame - scene_start_frame
    

    # Determine active track
    for i, track in enumerate(mid.tracks):
        # Loop over each note in the track
        for msg in track:
            if not msg.is_meta:
                # add to list of tracks
                selected_tracks_raw.insert(len(selected_tracks_raw), ("{}".format(i), "Track {} {}".format(i, track.name), ""))
                break;

    # print(selected_tracks_raw)

    # Mark this MIDI file as "cached"
    midi_file_loaded = midi_file_path
    
    return selected_tracks_raw

# UI properties
ANIM_MODE_KEYFRAMES = "KEYFRAMES"
ANIM_MODE_ACTIONS = "ACTIONS"

class GI_SceneProperties(PropertyGroup):
        
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
    
    
    # App State (not for user)
    initial_state = {}

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

        layout.label(text="Tokens", icon="OUTLINER_OB_SPEAKER")
        row = layout.row()
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


# Load/unload addon into Blender
classes = (
    GI_SceneProperties,
    GI_MIDIInputPanel,
    # GI_assign_keys,
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
