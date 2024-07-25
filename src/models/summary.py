class Summary:
    def __init__(self, user_id: str, project_id: str, project_name: str, duration_in_minutes: int,
                 task_id: str, task_name: str, user_comment: str, time_entry_type: str):
        self.user_id = user_id
        self.project_id = project_id
        self.project_name = project_name
        self.duration_in_minutes = duration_in_minutes
        self.task_id = task_id
        self.task_name = task_name
        self.user_comment = user_comment
        self.time_entry_type = time_entry_type

    def to_json(self):
        return {
            'user_id': self.user_id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'duration_in_minutes': self.duration_in_minutes,
            'task_id': self.task_id,
            'task_name': self.task_name,
            'user_comment': self.user_comment,
            'time_entry_type': self.time_entry_type
        }
    
    def from_json(json):
        return Summary(
            json['user_id'],
            json['project_id'],
            json['project_name'],
            json['duration_in_minutes'],
            json['task_id'],
            json['task_name'],
            json['user_comment'],
            json['time_entry_type']
        )
