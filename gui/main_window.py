import tkinter as tk
from tkinter import filedialog, messagebox
import yaml  # Import PyYAML to handle YAML formatting
from core.folder_manager import FolderManager
from gui.scene_editor import SceneEditor
import re  # Import regex to extract numbers from scene ID
import tkinter.simpledialog as simpledialog  # Add this for popup


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
    
            # Ensure the heading exists before passing data
            selected_scene.setdefault("heading", "")  # Default to empty string if missing
    
            # Open the selected scene in the editor
            self.scene_editor = SceneEditor(
                self.middle_frame,
                self.folder_manager,
                self.save_scene,
                scene_data=selected_scene  # Pass existing data for editing
            )
    

    def setup_ui(self):
        # Main layout frames
        # Ensure right section (YAML Preview) expands to max width first, then middle section fills remaining space
        self.root.grid_columnconfigure(0, weight=1)  # Left sidebar (scene list)
        self.root.grid_columnconfigure(1, weight=1)  # Middle section will fill remaining space
        self.root.grid_columnconfigure(2, weight=2)  # Right section expands first (higher priority)
        
        
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main layout frames with proportional scaling
        self.left_frame = tk.Frame(self.root, width=300)
        self.left_frame.grid_propagate(False)  # Prevent the frame from resizing automatically
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Ensure middle section fully expands to use available space
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.root.grid_columnconfigure(1, weight=4)  # Ensure this section expands dynamically
        
        
        # Allow the middle section to expand dynamically
        self.root.grid_columnconfigure(1, weight=3)  # Increase weight so it takes up more space
        
        
        # Ensure right section expands first to its max width
        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.root.grid_columnconfigure(2, weight=2)  # Ensure right section expands first
        
        

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

        # Allow YAML preview to stretch fully within right section
        self.yaml_frame = tk.Frame(self.right_frame, width=1500)  # Max width constraint
        self.yaml_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # Allow it to stretch
        
        
        
        self.yaml_label = tk.Label(self.yaml_frame, text="Live YAML Preview", font=("Arial", 14))
        self.yaml_label.pack(pady=5)
        
        self.yaml_preview = tk.Text(self.yaml_frame, state=tk.DISABLED, bg="#f4f4f4", width=60)
        self.yaml_preview.pack(fill=tk.BOTH, expand=True, pady=5)
        
        

        # Save YAML Button
        save_yaml_btn = tk.Button(
            self.left_frame, text="Save YAML", command=self.save_yaml_file
        )
        save_yaml_btn.pack(pady=5)
        
        # YAML Toggle Button (Placed Below Save/Load YAML)
        self.toggle_yaml_btn = tk.Button(self.left_frame, text="Hide YAML", command=self.toggle_yaml_preview)
        self.toggle_yaml_btn.pack(pady=5)
        
        
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

    def toggle_yaml_preview(self):
        """Toggles the visibility of the YAML preview section."""
        if self.yaml_frame.winfo_ismapped():
            self.yaml_frame.pack_forget()  # Hide YAML section
            self.toggle_yaml_btn.config(text="Show YAML")
        else:
            self.yaml_frame.pack(fill=tk.Y, side=tk.RIGHT, expand=False)  # Show YAML section
            self.toggle_yaml_btn.config(text="Hide YAML")
    

   
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

    def save_scene(self, new_scene):
        """Updates an existing scene or adds a new scene to the scene list."""
    
        scene_id = new_scene["scene_id"]
    
        # Check if the scene already exists in self.scenes
        for i, scene in enumerate(self.scenes):
            if scene["scene_id"] == scene_id:
                self.scenes[i] = new_scene  # Update existing scene
                break
        else:
            self.scenes.append(new_scene)  # If not found, add as a new scene
    
        # Refresh the scene list and YAML preview
        # Ensure the videos section gets updated
        scene_id = new_scene["scene_id"]
        self.video_associations[scene_id] = f"videos/{new_scene['video']}"
        
        self.update_scene_list()
        self.update_yaml_preview()  # Refresh the preview with updated videos
        
    
    
    

    def update_scene_list(self):
        self.scene_listbox.delete(0, tk.END)  # Clear the list
        for scene in self.scenes:
            display_text = f"{scene['scene_id']} - {scene['scene_type']}"
            if scene.get("auto_created"):
                display_text += " [Incomplete]"
            self.scene_listbox.insert(tk.END, display_text)

    def update_yaml_preview(self):
        """Regenerates the YAML preview while ensuring all referenced scenes stay in `videos`."""
    
        # Ensure `video_associations` exists before using it
        if not hasattr(self, "video_associations"):
            self.video_associations = {}
    
        # Ensure all referenced `next_scene` values are in `videos`
        all_referenced_scenes = set(self.video_associations.keys())
    
        for scene in self.scenes:
            for choice in scene["choices"]:
                next_scene_id = choice["next_scene"]
                if next_scene_id:
                    all_referenced_scenes.add(next_scene_id)
    
                # **Ensure temporary choices store their temp_video under the correct next_scene ID**
                if choice.get("temporary") and "temp_video" in choice:
                    temp_video = choice["temp_video"].strip()
                    if temp_video:
                        self.video_associations[next_scene_id] = f"videos/{temp_video}"
    
        # Ensure all referenced scenes exist in the videos section
        for scene_id in all_referenced_scenes:
            if scene_id not in self.video_associations:
                self.video_associations[scene_id] = f"videos/{scene_id}.mp4"
    
        # **Regenerate the videos section dynamically**
        self.video_associations.update({scene["scene_id"]: f"videos/{scene['video']}" for scene in self.scenes})
    
        # **Ensure temp videos are properly linked to their next_scene IDs**
        for scene in self.scenes:
            for choice in scene.get("choices", []):
                if choice.get("temporary") and "temp_video" in choice:
                    temp_video = choice["temp_video"].strip()
                    next_scene_id = choice["next_scene"]
                    if temp_video and next_scene_id:  # Ensure both exist
                        self.video_associations[next_scene_id] = f"videos/{temp_video}"  # Use next_scene ID, not filename
    
        yaml_data = {
            "start": self.scenes[0]["scene_id"] if self.scenes else "",
            "videos": self.video_associations.copy(),
            "options": {}
        }
    
        # Fill in the options section
        for scene in self.scenes:
            scene_data = {
                "scene_type": scene["scene_type"],
                "choices": {
                    choice["option"]: {
                        "next": choice["next_scene"],
                        "image": f"images/{choice['image']}" if choice["image"] else "",
                        "temporary": choice["temporary"]
                    }
                    for choice in scene["choices"]
                }
            }
    
            # Ensure scene["heading"] exists before using it
            scene_heading = scene.get("heading", "")  # Default to empty string if missing
    
            # Assign the correct heading field based on scene type
            if scene["scene_type"] == "Main":
                scene_data["main_heading"] = scene.get("main_heading", scene_heading)
            elif scene["scene_type"] == "Continue":
                scene_data["continue_heading"] = scene.get("continue_heading", scene_heading)
            elif scene["scene_type"] == "Question":
                scene_data["question_heading"] = scene.get("question_heading", scene_heading)
            else:
                scene_data["scene_heading"] = scene_heading  # Catch-all for unknown types
    
            yaml_data["options"][scene["scene_id"]] = scene_data
    
        # Debugging: Show final YAML data before updating the UI
        print("\nDEBUG: Final YAML structure before updating preview:\n", yaml.dump(yaml_data, sort_keys=False, default_flow_style=False))
    
        # Update the YAML preview UI
        self.yaml_preview.config(state=tk.NORMAL)
        self.yaml_preview.delete(1.0, tk.END)
        self.yaml_preview.insert(tk.END, yaml.dump(yaml_data, sort_keys=False, default_flow_style=False))
        self.yaml_preview.config(state=tk.DISABLED)
    

    def generate_yaml(self):
        """Convert scenes list into YAML format."""
        if not self.scenes:
            return "No scenes available."
    
        # Ensure all main scene videos are included
        self.video_associations = {scene["scene_id"]: f"videos/{scene['video']}" for scene in self.scenes}
    
        yaml_structure = {
            "start": self.scenes[0]["scene_id"],  # First scene becomes the starting scene
            "videos": self.video_associations.copy(),  # Ensure videos include temp videos
            "options": {}
        }
    
        # Fill in the options section
        for scene in self.scenes:
            scene_id = scene["scene_id"]
            scene_data = {
                "scene_type": scene["scene_type"],
                "choices": {}
            }
    
            # Correctly store heading under the appropriate field name
            if scene["scene_type"] == "Main":
                scene_data["main_heading"] = scene.get("heading", "")
            elif scene["scene_type"] == "Continue":
                scene_data["continue_heading"] = scene.get("heading", "")
            elif scene["scene_type"] == "Question":
                scene_data["question_heading"] = scene.get("heading", "")
    
            # Add choices, ensuring temp_video is stored correctly
            for choice in scene.get("choices", []):
                choice_data = {
                    "next": choice["next_scene"]
                }
                if choice["image"]:
                    choice_data["image"] = f"images/{choice['image']}"
                if choice["temporary"]:
                    choice_data["temporary"] = True
                    if "temp_video" in choice:
                        temp_video_file = choice["temp_video"]
                        temp_video_scene_id = choice["next_scene"]  # Use next_scene as the key
                        temp_video_path = f"videos/{temp_video_file}"
    
                        # Ensure temp video is stored under the correct next_scene ID
                        if temp_video_scene_id:
                            self.video_associations[temp_video_scene_id] = temp_video_path  
                            choice_data["temp_video"] = temp_video_path  # Store it under choices
    
                scene_data["choices"][choice["option"]] = choice_data
    
            yaml_structure["options"][scene_id] = scene_data
    
        # Ensure temp videos are written in the final YAML under "videos:"
        yaml_structure["videos"] = self.video_associations.copy()
    
        return yaml.dump(yaml_structure, sort_keys=False, default_flow_style=False)
    
    
    def validate_scene_references(self):
        """Highlight choices with non-existent next scene references, ensuring temporary choices are properly validated."""
        valid_scene_ids = {scene["scene_id"] for scene in self.scenes}
        valid_scene_ids.update(self.video_associations.keys())  # Ensure temporary choices are considered valid
    
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
        """Load a YAML file and ensure the videos section includes all referenced scenes."""
    
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
    
                # Copy the videos section so we can modify it
                video_associations = loaded_yaml["videos"].copy()
    
                # Step 1: **Find all next_scene values from choices and add them to videos**
                for scene_data in loaded_yaml["options"].values():
                    for choice in scene_data.get("choices", {}).values():
                        next_scene_id = choice.get("next", "")
                        if next_scene_id and next_scene_id not in video_associations:
                            video_associations[next_scene_id] = f"videos/{next_scene_id}.mp4"
    
                # Step 2: Store `video_associations` globally so other functions can access it
                self.video_associations = video_associations  # Ensures it's available in update_yaml_preview()
    
                # Step 3: Load scenes from YAML, but only if they are explicitly listed in options
                for scene_id, scene_data in loaded_yaml["options"].items():
                    scene_type = scene_data.get("scene_type", "Continue")
    
                    # Ensure headings are correctly assigned
                    heading = scene_data.get("main_heading", "") if scene_type == "Main" else (
                        scene_data.get("continue_heading", "") if scene_type == "Continue" else
                        scene_data.get("question_heading", "")
                    )
    
                    # Load choices
                    choices = []
                    for option_text, choice_data in scene_data.get("choices", {}).items():
                        next_scene_id = choice_data.get("next", "")
                        is_temporary = choice_data.get("temporary", False)
    
                        choices.append({
                            "option": option_text,
                            "next_scene": next_scene_id,
                            "image": choice_data.get("image", "").replace("images/", ""),
                            "temporary": is_temporary
                        })
    
                    # Add scene to the list
                    self.scenes.append({
                        "scene_id": scene_id,
                        "video": video_associations.get(scene_id, "").replace("videos/", ""),
                        "scene_type": scene_type,
                        "heading": heading,
                        "choices": choices
                    })
    
                # Step 4: Ensure the YAML videos section is explicitly updated before preview refresh
                loaded_yaml["videos"] = self.video_associations
    
                # Update the GUI
                self.update_scene_list()
                self.update_yaml_preview()
    
                messagebox.showinfo("Success", f"YAML loaded successfully from {file_path}")
    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load YAML file:\n{e}")
    
    
    def process_videos_section(self, loaded_yaml):
        """Ensures all referenced scenes (from both videos and choices) exist in the videos section."""
        
        video_associations = loaded_yaml["videos"].copy()
    
        # Collect all referenced scenes, including from choices
        referenced_scenes = set(video_associations.keys())  # Start with explicitly listed video scenes
    
        print("\nDEBUG: Initial video associations:", video_associations)
    
        for scene_id, scene_data in loaded_yaml["options"].items():
            for option_text, choice in scene_data.get("choices", {}).items():
                next_scene_id = choice.get("next", "")
                is_temporary = choice.get("temporary", False)
    
                print(f"DEBUG: Choice '{option_text}' → next_scene: {next_scene_id}, temporary: {is_temporary}")
    
                if next_scene_id:
                    referenced_scenes.add(next_scene_id)
    
                    # **Ensure temporary scenes are forced into videos section**
                    if is_temporary and next_scene_id not in video_associations:
                        video_associations[next_scene_id] = f"videos/{next_scene_id}.mp4"
                        print(f"DEBUG: Added temporary scene to videos: {next_scene_id}")
    
        print("\nDEBUG: All referenced scenes:", referenced_scenes)
    
        # Ensure all referenced scenes exist in the videos section
        for scene_id in referenced_scenes:
            if scene_id not in video_associations:
                video_associations[scene_id] = f"videos/{scene_id}.mp4"
                print(f"DEBUG: Added to videos: {scene_id}")
    
        print("\nDEBUG: Final video associations:", video_associations)
    
        return video_associations

    
    
    def process_options_section(self, loaded_yaml, video_associations):
        """Loads the options section and ensures only explicitly defined scenes are added."""
        
        for scene_id, scene_data in loaded_yaml["options"].items():
            scene_type = scene_data.get("scene_type", "Continue")
    
            # Ensure headings are correctly assigned
            heading = scene_data.get("main_heading", "") if scene_type == "Main" else (
                scene_data.get("continue_heading", "") if scene_type == "Continue" else
                scene_data.get("question_heading", "")
            )
    
            # Load choices
            choices = []
            for option_text, choice_data in scene_data.get("choices", {}).items():
                next_scene_id = choice_data.get("next", "")
                is_temporary = choice_data.get("temporary", False)
    
                # Debugging: Check if temporary scenes are being skipped correctly
                print(f"DEBUG: Processing choice '{option_text}' → next_scene: {next_scene_id}, temporary: {is_temporary}")
    
                choices.append({
                    "option": option_text,
                    "next_scene": next_scene_id,
                    "image": choice_data.get("image", "").replace("images/", ""),
                    "temporary": is_temporary
                })
    
            # Add scene to the list
            self.scenes.append({
                "scene_id": scene_id,
                "video": video_associations.get(scene_id, "").replace("videos/", ""),
                "scene_type": scene_type,
                "heading": heading,
                "choices": choices
            })
    
        # Explicitly update the YAML videos section to ensure all referenced scenes are included
        loaded_yaml["videos"] = video_associations
        print("\nDEBUG: Final loaded videos section in YAML:", loaded_yaml["videos"])  # Debugging Step 6
     

    def show_context_menu(self, event):
        """Show right-click context menu on scene list."""
        selection = self.scene_listbox.nearest(event.y)
        if selection >= 0:
            self.scene_listbox.selection_clear(0, tk.END)
            self.scene_listbox.selection_set(selection)
            self.context_menu.post(event.x_root, event.y_root)
    


    def duplicate_scene(self):
        """Duplicate the selected scene, increment the scene ID, and exclude temporary choices."""
        selection = self.scene_listbox.curselection()
        if selection:
            index = selection[0]
            original_scene = self.scenes[index].copy()
    
            # Remove temporary choices before duplicating
            duplicated_choices = [choice for choice in original_scene["choices"] if not choice.get("temporary", False)]
    
            # Initialize `new_scene_id` and get base scene ID
            base_id = original_scene["scene_id"]
            new_scene_id = base_id  # Default to the original scene ID (we'll modify if needed)
    
            # Extract base scene ID and increment the number
            match = re.match(r"([a-zA-Z]+)(\d+)\.(\d+)", base_id)  # Match format like "s4.3"
            if match:
                prefix, major, minor = match.groups()
                major, minor = int(major), int(minor)
                
                # Find the next available scene ID
                while True:
                    minor += 1  # Increment the minor version (e.g., s4.3 → s4.4)
                    new_scene_id = f"{prefix}{major}.{minor}"
                    if not self.scene_exists(new_scene_id):  # Ensure it's unique
                        break
            else:
                # If no match, just append "_copy" (fallback)
                new_scene_id = f"{base_id}_copy"
    
            # **Popup to Edit Scene ID**
            new_scene_id = simpledialog.askstring("Edit Scene ID", "Modify the Scene ID:", initialvalue=new_scene_id)
            
            if new_scene_id:
                # Create the new scene with the new ID (allow user to edit it)
                new_scene = {
                    "scene_id": new_scene_id,  # Auto-generated new ID
                    "video": original_scene["video"],  # Copy original video's video
                    "scene_type": original_scene["scene_type"],
                    "heading": original_scene.get("heading", ""),
                    "choices": duplicated_choices,  # Only normal choices
                }
    
                # **Add the new scene's video to video_associations**
                self.video_associations[new_scene_id] = f"videos/{original_scene['video']}"
    
                # Open the duplicated scene in the editor for the user to review and edit
                if self.scene_editor:
                    self.scene_editor.frame.destroy()
    
                self.scene_editor = SceneEditor(
                    self.middle_frame,
                    self.folder_manager,
                    self.save_scene,
                    scene_data=new_scene  # Allow editing before saving
                )
    
                # **Force update of YAML preview to include the new scene**
                self.update_yaml_preview()
    
    