class CriticalSection(object):
    def __init__(self, isHold=False, holdId=None, holdTime=None):
        self.isHold = isHold
        self.holdId = holdId
        self.holdTime = holdTime


class Message(object):
    def __init__(self, id=None, timestamp=None):
        self.id = id
        self.timestamp = timestamp
