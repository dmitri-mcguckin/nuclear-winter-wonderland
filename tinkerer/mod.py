class Mod:
    def __init__(self,
                 name: str,
                 project_id: int,
                 file_id: int,
                 required: bool):
        self.name = name
        self.project_id = project_id
        self.file_id = file_id
        self.required = required

    def to_dict(self):
        return {"name": self.name,
                "projectID": self.project_id,
                "fileID": self.file_id,
                "required": self.required}

    def __str__(self):
        return "<Mod [{}] (required: {}) ({}/{})>".format(self.name,
                                                          self.required,
                                                          self.project_id,
                                                          self.file_id)

    def to_mod(data: dict):
        name = data['name']
        required = bool(data['required'])
        project_id = int(data['projectID'])
        file_id = int(data['fileID'])
        return Mod(name, project_id, file_id, required)
