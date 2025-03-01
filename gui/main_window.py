import tkinter as tk
from tkinter import filedialog, messagebox
import yaml  # Import PyYAML to handle YAML formatting
from core.folder_manager import FolderManager
from gui.scene_editor import SceneEditor


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("YAML Scene Manager")
        self.root.geometry("1200x700")

        self.folder_manager = FolderManager()
        self.scenes = []  # List to store scenes

        self.setup_ui()

    def scene_exists(self, scene_id):
        """Check if a scene with the given ID already exists."""
        return any(scene["scene_id"] == scene_id for scene in self.scenes)

    def edit_selected_scene(self, event):
        selection = self.scene_listbox.curselection()  # Get the selected scene index
        if selection:
            index = selection[0]
            selected_scene = self.scenes[index]  # Fetch the scene details

            # Clear the existing editor if open
            if self.scene_editor:
                self.scene_editor.frame.destroy()

            # Open the selected scene in the editor
            self.scene_editor = SceneEditor(
                self.middle_frame,
                self.folder_manager,
                self.save_scene,
                scene_data=selected_scene  # Pass existing data for editing
            )

    def setup_ui(self):
        # Main layout frames
        # Use a grid-based layout for better scaling
        self.root.grid_columnconfigure(0, weight=3)  # 30% width
        self.root.grid_columnconfigure(1, weight=3)  # 30% width
        self.root.grid_columnconfigure(2, weight=4)  # 40% width
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main layout frames with proportional scaling
        self.left_frame = tk.Frame(self.root, width=300)
        self.left_frame.grid_propagate(False)  # Prevent the frame from resizing automatically
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        

        # Folder Selection Section
        select_folder_btn = tk.Button(
            self.left_frame,
            text="Select Source Folder",
            command=self.select_source_folder
        )
        select_folder_btn.pack(pady=10)

        self.folder_label = tk.Label(
            self.left_frame,
            text="No folder selected",
            wraplength=250,  # Limit the width in pixels before wrapping
            justify=tk.LEFT,  # Align text to the left
            anchor="w"  # Align text inside the label
        )
        self.folder_label.pack(pady=10, fill=tk.X)  # Allow it to expand horizontally
        

        # Scene List Section (with drag-and-drop enabled)
        add_scene_btn = tk.Button(
            self.left_frame,
            text="Add Scene",
            command=self.show_scene_editor
        )
        add_scene_btn.pack(pady=10)

        self.scene_listbox = tk.Listbox(self.left_frame, width=40)
        self.scene_listbox.bind("<<ListboxSelect>>", self.edit_selected_scene)
        self.scene_listbox.pack(fill=tk.BOTH, expand=True, pady=10)

        # Enable Drag-and-Drop for reordering
        self.scene_listbox.bind("<ButtonPress-1>", self.start_drag)
        self.scene_listbox.bind("<B1-Motion>", self.drag_motion)
        self.scene_listbox.bind("<ButtonRelease-1>", self.end_drag)

        # Scene Editor Section
        self.scene_editor = None  # Placeholder for the editor

        # YAML Preview Section
        self.yaml_label = tk.Label(self.right_frame, text="Live YAML Preview", font=("Arial", 14))
        self.yaml_label.pack(pady=10)

        self.yaml_preview = tk.Text(self.right_frame, state=tk.DISABLED, bg="#f4f4f4")
        self.yaml_preview.pack(fill=tk.BOTH, expand=True, pady=10)
        

        # Save YAML Button
        save_yaml_btn = tk.Button(
            self.left_frame, text="Save YAML", command=self.save_yaml_file
        )
        save_yaml_btn.pack(pady=5)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Duplicate Scene", command=self.duplicate_scene)
        
        # Bind right-click event
        self.scene_listbox.bind("<Button-3>", self.show_context_menu)
        

        # Load YAML Button
        load_yaml_btn = tk.Button(
            self.left_frame, text="Load YAML", command=self.load_yaml_file
        )
        load_yaml_btn.pack(pady=5)

    # Drag-and-Drop Event Handlers
    def start_drag(self, event):
        """Start dragging a scene with highlight."""
        self.dragging_index = self.scene_listbox.nearest(event.y)
        self.scene_listbox.itemconfig(self.dragging_index, bg="lightblue")
    
    def drag_motion(self, event):
        """Handle the dragging motion and auto-scroll."""
        new_index = self.scene_listbox.nearest(event.y)
    
        # Auto-scroll when dragging near the edges
        if event.y < 10:  # Near the top
            self.scene_listbox.yview_scroll(-1, "units")
        elif event.y > self.scene_listbox.winfo_height() - 10:  # Near the bottom
            self.scene_listbox.yview_scroll(1, "units")
    
        if new_index != self.dragging_index:
            # Swap scenes in the list
            self.scenes[self.dragging_index], self.scenes[new_index] = (
                self.scenes[new_index],
                self.scenes[self.dragging_index]
            )
            self.update_scene_list()
            self.dragging_index = new_index
    
    def end_drag(self, event):
        """End dragging, remove highlight, and update YAML preview."""
        self.scene_listbox.itemconfig(self.dragging_index, bg="white")
        self.update_yaml_preview()
    

    def select_source_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            valid = self.folder_manager.validate_folder_structure(folder_path)
            if valid:
                self.folder_label.config(text=f"Selected Folder: {folder_path}")
            else:
                messagebox.showerror("Invalid Folder", "The selected folder must contain 'videos/' and 'images/' subfolders.")

    def show_scene_editor(self):
        if not self.folder_manager.source_folder:
            messagebox.showerror("No Source Folder", "Please select a valid source folder first.")
            return

        # Clear any existing editor
        if self.scene_editor:
            self.scene_editor.frame.destroy()

        # Display a new editor inside the middle frame
        self.scene_editor = SceneEditor(self.middle_frame, self.folder_manager, self.save_scene)

    def save_scene(self, updated_scene):
        # Replace the scene if it already exists
        for i, scene in enumerate(self.scenes):
            if scene["scene_id"] == updated_scene["scene_id"]:
                self.scenes[i] = updated_scene  # Update the existing scene
                break
        else:
            # If it doesn't exist yet, add it as a new scene
            self.scenes.append(updated_scene)

        # Automatically create new scenes for referenced next_scene_id
        for choice in updated_scene.get("choices", []):
            next_scene_id = choice["next_scene"]
            if not self.scene_exists(next_scene_id):
                auto_created_scene = {
                    "scene_id": next_scene_id,
                    "video": None,
                    "scene_type": "Continue",
                    "heading": "[Auto-created Scene]",
                    "choices": [],
                    "auto_created": True
                }
                self.scenes.append(auto_created_scene)

        self.update_scene_list()
        self.update_yaml_preview()

    def update_scene_list(self):
        self.scene_listbox.delete(0, tk.END)  # Clear the list
        for scene in self.scenes:
            display_text = f"{scene['scene_id']} - {scene['scene_type']}"
            if scene.get("auto_created"):
                display_text += " [Incomplete]"
            self.scene_listbox.insert(tk.END, display_text)

    def update_yaml_preview(self):
        yaml_data = self.generate_yaml()
        self.yaml_preview.config(state=tk.NORMAL)  # Enable editing for update
        self.yaml_preview.delete(1.0, tk.END)  # Clear the text
        self.yaml_preview.insert(tk.END, yaml_data)  # Insert new YAML
        self.yaml_preview.config(state=tk.DISABLED)  # Make read-only again

    def generate_yaml(self):
        """Convert scenes list into YAML format."""
        if not self.scenes:
            return "No scenes available."
    
        yaml_structure = {
            "start": self.scenes[0]["scene_id"],  # First scene becomes the starting scene
            "videos": {},
            "options": {}
        }
    
        # Fill in the videos and options sections
        for scene in self.scenes:
            scene_id = scene["scene_id"]
            video_path = f"videos/{scene['video']}" if scene["video"] else "videos/default.mp4"
            yaml_structure["videos"][scene_id] = video_path
    
            # Construct scene data
            scene_data = {
                "scene_type": scene["scene_type"]
            }
    
            # Insert the correct heading field based on scene type
            if scene["scene_type"] == "Main":
                scene_data["main_heading"] = scene.get("main_heading", "")
            elif scene["scene_type"] == "Continue":
                scene_data["continue_heading"] = scene.get("continue_heading", "")
            elif scene["scene_type"] == "Question":
                scene_data["question_heading"] = scene.get("question_heading", "")
    
            # Add choices below scene_type and heading
            scene_data["choices"] = {}
    
            for choice in scene.get("choices", []):
                choice_data = {
                    "next": choice["next_scene"]
                }
                if choice["image"]:
                    choice_data["image"] = f"images/{choice['image']}"
                if choice["temporary"]:
                    choice_data["temporary"] = True
    
                scene_data["choices"][choice["option"]] = choice_data
    
            # Store scene data in the options section
            yaml_structure["options"][scene_id] = scene_data
    
        return yaml.dump(yaml_structure, sort_keys=False, default_flow_style=False)
    
    
    
    def validate_scene_references(self):
        """Highlight choices with non-existent next scene references."""
        valid_scene_ids = {scene["scene_id"] for scene in self.scenes}
        invalid_references = []
    
        for scene in self.scenes:
            for choice in scene.get("choices", []):
                if choice["next_scene"] not in valid_scene_ids:
                    invalid_references.append((scene["scene_id"], choice["next_scene"]))
    
        if invalid_references:
            message = "Invalid scene references found:\n"
            for scene_id, invalid_ref in invalid_references:
                message += f"Scene '{scene_id}' → Invalid next_scene ID '{invalid_ref}'\n"
            messagebox.showerror("Invalid References", message)
            return False  # Validation failed
        return True  # Validation passed
    

    def save_yaml_file(self):
        # Validate scene references first
        if not self.validate_scene_references():
            return  # Abort saving if validation fails
    
        # Ask the user where to save the file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml")],
            title="Save YAML File"
        )
    
        if file_path:
            yaml_data = self.generate_yaml()
            try:
                with open(file_path, "w") as yaml_file:
                    yaml_file.write(yaml_data)
                messagebox.showinfo("Success", f"YAML saved successfully to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save YAML file:\n{e}")
    
    def load_yaml_file(self):
        # Ask the user to select a YAML file
        file_path = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml")],
            title="Load YAML File"
        )
    
        if file_path:
            try:
                with open(file_path, "r") as yaml_file:
                    loaded_yaml = yaml.safe_load(yaml_file)
    
                # Validate the structure
                if "start" not in loaded_yaml or "videos" not in loaded_yaml or "options" not in loaded_yaml:
                    messagebox.showerror("Invalid YAML", "The YAML file does not have the required structure.")
                    return
    
                # Clear the current scenes
                self.scenes.clear()
    
                # Load scenes from YAML
                for scene_id, video_path in loaded_yaml["videos"].items():
                    scene_data = loaded_yaml["options"].get(scene_id, {})
                    scene_type = scene_data.get("scene_type", "Continue")
    
                    # Ensure headings are stored under the correct field
                    heading = ""
                    if scene_type == "Main":
                        heading = scene_data.get("main_heading", "")
                    elif scene_type == "Continue":
                        heading = scene_data.get("continue_heading", "")
                    elif scene_type == "Question":
                        heading = scene_data.get("question_heading", "")
    
                    # Load choices
                    choices = []
                    for option_text, choice_data in scene_data.get("choices", {}).items():
                        choices.append({
                            "option": option_text,
                            "next_scene": choice_data.get("next", ""),
                            "image": choice_data.get("image", "").replace("images/", ""),
                            "temporary": choice_data.get("temporary", False)
                        })
    
                    # Add scene to the list
                    scene = {
                        "scene_id": scene_id,
                        "video": video_path.replace("videos/", ""),
                        "scene_type": scene_type,
                        "heading": heading,  # Ensuring consistent heading storage
                        "choices": choices
                    }
                    self.scenes.append(scene)
                    print(f"DEBUG: Scene Loaded: {scene}")
    
                # Update the GUI
                self.update_scene_list()
                self.update_yaml_preview()
                messagebox.showinfo("Success", f"YAML loaded successfully from {file_path}")
    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load YAML file:\n{e}")
    

    def show_context_menu(self, event):
        """Show right-click context menu on scene list."""
        selection = self.scene_listbox.nearest(event.y)
        if selection >= 0:
            self.scene_listbox.selection_clear(0, tk.END)
            self.scene_listbox.selection_set(selection)
            self.context_menu.post(event.x_root, event.y_root)
    
    def duplicate_scene(self):
        """Duplicate the selected scene and assign a new scene ID."""
        selection = self.scene_listbox.curselection()
        if selection:
            index = selection[0]
            original_scene = self.scenes[index].copy()
    
            # Generate a new unique scene ID
            base_id = original_scene["scene_id"]
            new_id = f"{base_id}_copy"
            count = 1
            while self.scene_exists(new_id):
                count += 1
                new_id = f"{base_id}_copy{count}"
    
            original_scene["scene_id"] = new_id
            self.scenes.insert(index + 1, original_scene)
            self.update_scene_list()
            self.update_yaml_preview()
    