[Example of plugin](https://github.com/user-attachments/assets/dc90301c-569a-493f-a6f9-35798aeb086b)

# Design Token Manager Blender plugin

This is a free Blender addon to manage and use design tokens.

## ⬇️ Installation

1. [Download the plugin zip](https://github.com/whoisryosuke/blender-design-token-manager/releases/download/v0.0.2/design-token-manager-v0.0.1.zip) from the releases page.
1. Open Blender
1. Go to Edit > Preferences and go to the Addons tab on left.
1. Click install button.
1. Select the zip you downloaded.
1. You can confirm it's installed by searching for **"Design Token Manager"** and seeing if it's checked off

## 🔰 How to use

![The plugin panel inside Blender](/docs/screenshots/plugin-panel.jpg)

1. Navigate to a node editor window (like the Shading or Geometry Nodes)
1. Open the side panel (aka "n-panel"). If it's not visible press the little arrow on the right side of panel). You can also use `CTRL + ]` if using industry compatible shortcuts.
1. Open up the side panel tab labeled **"Design"** to find the **Design Token Manager panel**.

## ⚙️ How it works

Check out [my blog](https://whoisryosuke.com/blog/) for tips and tricks on writing Python plugins for Blender.

## Development

1. Clone the repo: `git clone`
1. Zip up the folder.
1. Install in Blender.
1. Open the plugin code inside your Blender plugin folder.
1. Edit, Save, Repeat.

## Publish

1. Bump version in `__init__.py`
1. Bump version in `blender_manifest.toml`
1. `blender --command extension build --output-dir dist`
1. Upload the new `.zip` file generated inside `/dist` folder to Blender addon marketplace and [GitHub Releases page](https://github.com/whoisryosuke/blender-midi-keyframes/releases/new).

> On Windows? You can add `blender` to your command line by going to Start annd searching for "Edit Environment Variables for your account". Find the Variable "PATH" and edit it. Add the full path to where your `blender.exe` is located (e.g. `C:/Program Files/Blender/4.2/`).

## 💪 Credits

- [MIDI to Keyframes addon](https://github.com/whoisryosuke/blender-midi-to-keyframes)
