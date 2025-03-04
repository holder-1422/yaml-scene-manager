import tkinter as tk
from tkinter import ttk, messagebox
import os


class SceneEditor:
    def __init__(self, parent, folder_manager, save_callback, scene_data=None):
        self.folder_manager = folder_manager
        self.save_callback = save_callback
        self.new_scene = None
        self.scene_data = scene_data  # Existing scene data for editing

        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        

        self.setup_ui()

    def setup_ui(self):
        # Save Button at the Top
        save_btn = tk.Button(self.frame, text="Save Scene", command=self.save_scene)
        save_btn.pack(pady=10)

        # Scene ID
        tk.Label(self.frame, text="Scene ID:").pack(pady=5)
        self.scene_id_entry = tk.Entry(self.frame)
        self.scene_id_entry.pack(pady=5)

        # Pre-fill scene ID if editing
        if self.scene_data:
            self.scene_id_entry.insert(0, self.scene_data["scene_id"])
            self.scene_id_entry.config(state='disabled')  # Prevent changing ID

        # Video Selection Dropdown with Dynamic Refresh
        tk.Label(self.frame, text="Select Video:").pack(pady=5)
        self.video_var = tk.StringVar()
        self.video_dropdown = ttk.Combobox(self.frame, textvariable=self.video_var)
        self.video_dropdown.pack(pady=5)
        
        # Refresh videos dynamically on click
        self.video_dropdown.bind("<Button-1>", lambda event: self.refresh_dropdown("videos"))
        

        # Pre-fill video if editing
        if self.scene_data and self.scene_data["video"]:
            self.video_var.set(self.scene_data["video"])

        # Scene Type
        tk.Label(self.frame, text="Scene Type:").pack(pady=5)
        self.scene_type_var = tk.StringVar()
        self.scene_type_dropdown = ttk.Combobox(
            self.frame,
            textvariable=self.scene_type_var,
            values=["Continue", "Question"]
        )
        self.scene_type_dropdown.pack(pady=5)

        if self.scene_data:
            self.scene_type_var.set(self.scene_data["scene_type"])

        # Scene Heading
        self.heading_label = tk.Label(self.frame, text="Scene Heading:")
        self.heading_label.pack(pady=5)
        self.heading_entry = tk.Entry(self.frame)
        self.heading_entry.pack(pady=5)

        if self.scene_data:
            self.heading_entry.insert(0, self.scene_data["heading"])

        # Choices Section (Scrollable Frame)
        choices_container = tk.Frame(self.frame)
        choices_container.pack(fill=tk.BOTH, expand=True, pady=10)
        choices_container.grid_rowconfigure(0, weight=1)
        choices_container.grid_columnconfigure(0, weight=1)
        

        # Add a canvas for scrolling
        canvas = tk.Canvas(choices_container)
        scrollbar = tk.Scrollbar(choices_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.choices_frame = scrollable_frame
        self.choices = []

        # Pre-fill existing choices if editing
        if self.scene_data and "choices" in self.scene_data:
            for existing_choice in self.scene_data["choices"]:
                self.add_choice(existing_choice)
        else:
            self.add_choice()  # Add one empty choice if new

        # Add Choice Button
        add_choice_btn = tk.Button(self.frame, text="Add Choice", command=self.add_choice)
        add_choice_btn.pack(pady=10)
        
        # Refresh Media Files Button
        refresh_media_btn = tk.Button(self.frame, text="Refresh Media Files", command=lambda: self.refresh_dropdown("videos"))
        refresh_media_btn.pack(pady=10)
        
        
    def add_choice(self, existing_choice=None):
        # Create the main frame for each choice
        choice_frame = tk.Frame(self.choices_frame, bd=1, relief=tk.SOLID, padx=5, pady=5)
        choice_frame.pack(fill=tk.X, pady=5)
    
        # Full-width Option Text Entry
        tk.Label(choice_frame, text="Option:", font=("Arial", 10)).pack(anchor="w")
        option_entry = tk.Entry(choice_frame)
        option_entry.pack(fill=tk.X, padx=5, pady=5)
    
        # Sub-frame for Next Scene ID, Image Dropdown, and Temporary Flag (side-by-side)
        details_frame = tk.Frame(choice_frame)
        details_frame.pack(fill=tk.X, padx=5, pady=5)
    
        # Next Scene ID
        tk.Label(details_frame, text="Next ID:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        next_scene_entry = tk.Entry(details_frame, width=10)
        next_scene_entry.pack(side=tk.LEFT, padx=(0, 10))
    
        # Image Dropdown
        tk.Label(details_frame, text="Image:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        image_var = tk.StringVar()
        image_files = self._get_files("images")
        image_dropdown = ttk.Combobox(details_frame, textvariable=image_var, values=image_files, width=20)
        image_dropdown.pack(side=tk.LEFT, padx=(0, 10))
    
        # Temporary Flag Checkbox
        temp_flag = tk.BooleanVar()
        temp_checkbox = tk.Checkbutton(details_frame, text="Temporary", variable=temp_flag)
        temp_checkbox.pack(side=tk.LEFT)
    
        # Pre-fill existing data if editing
        if existing_choice:
            option_entry.insert(0, existing_choice["option"])
            next_scene_entry.insert(0, existing_choice["next_scene"])
            if existing_choice.get("image"):
                image_var.set(existing_choice["image"])
            if existing_choice.get("temporary"):
                temp_flag.set(existing_choice["temporary"])
    
        # Store the choice data
        choice_data = {
            "option_entry": option_entry,
            "next_scene_entry": next_scene_entry,
            "image_var": image_var,
            "temporary_flag": temp_flag
        }
    
        self.choices.append(choice_data)
    
    
    

    def _get_files(self, subfolder):
        """Get files from the given subfolder, ensuring the folder exists."""
        if not self.folder_manager or not self.folder_manager.source_folder:
            return []
    
        folder_path = os.path.join(self.folder_manager.source_folder, subfolder)
        return os.listdir(folder_path) if os.path.exists(folder_path) else []
    
    

    def refresh_dropdown(self, media_type):
        """Refresh the dropdown list for videos or images dynamically."""
        folder_path = os.path.join(self.folder_manager.source_folder, media_type)
        file_list = os.listdir(folder_path) if os.path.exists(folder_path) else []
    
        if media_type == "videos":
            self.video_dropdown['values'] = file_list
        elif media_type == "images":
            for choice in self.choices:
                if "image_dropdown" in choice:
                    choice["image_dropdown"]['values'] = file_list
    
    
    

    def save_scene(self):
        scene_id = self.scene_id_entry.get().strip()
        video = self.video_var.get()
        scene_type = self.scene_type_var.get()
        scene_heading = self.heading_entry.get().strip()

        if not scene_id or not video or not scene_type or not scene_heading:
            messagebox.showerror("Missing Information", "Please fill in all required fields.")
            return

        # Create a new scene object
        new_scene = {
            "scene_id": scene_id,
            "video": video,
            "scene_type": scene_type,
            "heading": scene_heading,
            "choices": []  # Store choices here
        }

        # Save all choices
        for choice in self.choices:
            option_text = choice["option_entry"].get().strip()
            next_scene = choice["next_scene_entry"].get().strip()
            image = choice["image_var"].get()
            temporary = choice["temporary_flag"].get()

            if not option_text or not next_scene:
                messagebox.showerror("Missing Information", "Each choice must have an option text and a next scene ID.")
                return

            # Add the choice details
            new_scene["choices"].append({
                "option": option_text,
                "next_scene": next_scene,
                "image": image if image else None,
                "temporary": temporary
            })

        # Pass the scene data to the main window
        self.new_scene = new_scene
        self.save_callback(new_scene)  # Send the scene back for storage
        self.frame.destroy()  # Close the editor
