class Project:
    def __init__(self, project_id: str, project_name: str):
        self.project_id = project_id
        self.project_name = project_name
    
    def to_json(self):
        return {
            'project_id': self.project_id,
            'project_name': self.project_name
        }

    def from_json(json):
        return Project(
            json['project_id'],
            json['project_name']
        )