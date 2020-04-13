class Mod:
    def __init__(self, mod_id, file_id, name, required = True):
        self.mod_id = mod_id
        self.file_id = file_id
        self.name = name
        self.required = required

    def to_dict(self):
        return {
                 "name": self.name,
                 "projectID": self.mod_id,
                 "fileID": self.file_id,
                 "required": self.required }

    def __str__(self):
        if self.required: req = "REQUIRED"
        else: req = "OPTIONAL"
        return self.name.ljust(60) + str("(pid: " + str(self.mod_id) + " | fid:" + str(self.file_id) + ")").ljust(27) + "\t[" + req + "]"
