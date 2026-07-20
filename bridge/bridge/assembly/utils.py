from enum import Enum, auto


class RobotHome(Enum):
    START = auto()
    END = auto()
    BOTH = auto()
    NONE = auto()


class ToolType(Enum):
    GRIPPER = auto()
    VACUUM = auto()
