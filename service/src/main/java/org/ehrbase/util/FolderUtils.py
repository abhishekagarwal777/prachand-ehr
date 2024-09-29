class Folder:
    def __init__(self, name, subfolders=None):
        self.name = name
        self.subfolders = subfolders if subfolders is not None else []

    def get_folders(self):
        return self.subfolders

    def get_name_as_string(self):
        return self.name


class FolderUtils:

    @staticmethod
    def check_sibling_name_conflicts(folder):
        """
        Checks each subfolder level for conflicts. For this purpose, for each subfolder level,
        there will be a set created that contains all names of the siblings as values. If at least 
        one value could not be inserted, it will be identified as duplicate and will throw a 
        ValueError that can be handled at the controller layer.

        :param folder: Folder to check subfolders for
        """
        if folder.get_folders():
            folder_names = set()

            for sub_folder in folder.get_folders():
                # A new entry in the set results to False if there is already a duplicate element existing
                if sub_folder.get_name_as_string() in folder_names:
                    raise ValueError(f"Duplicate folder name {sub_folder.get_name_as_string()}")
                else:
                    folder_names.add(sub_folder.get_name_as_string())
                    # Check subfolder hierarchies as well for duplicates
                    FolderUtils.check_sibling_name_conflicts(sub_folder)
