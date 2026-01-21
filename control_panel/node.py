class NodeState:
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DELETING = "deleting"
    DELETED = "deleted"

class Node:
    def __init__(self, state: NodeState):
        self.state = state

    
    