import os

class FolderManager:
    def __init__(self):
        self.source_folder = None

    def validate_folder_structure(self, folder_path):
        """Check if the folder contains 'videos/' and 'images/' subfolders."""
        videos_path = os.path.join(folder_path, "videos")
        images_path = os.path.join(folder_path, "images")

        if os.path.isdir(videos_path) and os.path.isdir(images_path):
            self.source_folder = folder_path
            return True
        return False
