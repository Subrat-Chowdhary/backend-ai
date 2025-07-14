class MockTask:
    def __init__(self, name):
        self.name = name
        self.id = "mock-task-id"
    
    def delay(self, *args, **kwargs):
        return self

process_resume_task = MockTask("process_resume_task")
batch_process_resumes_task = MockTask("batch_process_resumes_task")