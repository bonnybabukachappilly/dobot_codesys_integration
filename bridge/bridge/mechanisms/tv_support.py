from typing import NamedTuple

from robodk.robolink import Item, Robolink
from robodk import robolink
from robodk.robomath import Mat

# ****************************************************************************

MECHANISM_NAME = 'm_TV_Support'
TOOL_NAME = 't_TV_Support'

# Frames
TOOL_FRAME = 'f_TV_Support'
REF_PART_FRAME = 'f_Ref_TV_Support'

# Objects
REF_PART_NAME = 'TV_Support_Ref'

# Targets
HOME_JOINT: list[float] = [200000.00]
INCREMENT_JOINT: float = -720.00

# Speed & Acceleration
JOINT_SPEED = 500.0
JOINT_ACCELERATION = 250.0

# ****************************************************************************
# self._rdk.ShowMessage(str(type(current)))


class SupportFrames(NamedTuple):
    tool: Item
    ref_part: Item


class TVSupportMechanism:
    def __init__(self) -> None:
        self._rdk = Robolink()

        self._mechanism: Item = self._rdk.Item(
            MECHANISM_NAME, robolink.ITEM_TYPE_ROBOT)
        self._tool: Item = self._rdk.Item(TOOL_NAME, robolink.ITEM_TYPE_TOOL)
        self._frames: SupportFrames = self.__create_frames()

        self._home_joints: list[float] = HOME_JOINT
        self._inc_joints: float = INCREMENT_JOINT

        self._ref_part_name = REF_PART_NAME
        self._tolerance = 0.1

        self.initialize()

    def initialize(self) -> None:
        self._mechanism.setTool(self._tool)

        if 'JOINT_SPEED' in globals():
            self._mechanism.setSpeedJoints(globals()['JOINT_SPEED'])
        if 'JOINT_ACCELERATION' in globals():
            self._mechanism.setAccelerationJoints(
                globals()['JOINT_ACCELERATION'])

    @property
    def _new_part_name(self) -> str:
        return self._ref_part_name.replace('Ref', 'New')

    def __create_frames(self) -> SupportFrames:
        return SupportFrames(
            tool=self._rdk.Item(TOOL_FRAME, robolink.ITEM_TYPE_FRAME),
            ref_part=self._rdk.Item(REF_PART_FRAME, robolink.ITEM_TYPE_FRAME)
        )

    def set_home(self) -> None:
        self._mechanism.setJoints(self._home_joints)

    def move_home(self) -> None:
        self._mechanism.MoveJ(self._home_joints)

    def reset_parts(self) -> None:
        items: list[Item] = self._rdk.ItemList()

        self._rdk.Render(False)

        for item in items:
            if item.Name() == self._new_part_name:
                item.Delete()

        self._rdk.Render(True)

    def create_parts(self) -> None:
        children: list[Item] = self._frames.ref_part.Childs()

        self._rdk.Render(False)

        for child in children:
            abs_pose: Mat = child.PoseAbs()

            child.Copy()

            new: Item = self._rdk.Paste()  # type: ignore
            new.setParent(child.Parent())
            new.setName(self._new_part_name)

            new.setParentStatic(self._frames.tool)
            new.setPoseAbs(abs_pose)
            new.setVisible(True)

        self._rdk.Render(True)

    def update(self) -> None:
        current = self._mechanism.Joints().tolist()
        current[0] += self._inc_joints
        self._mechanism.MoveJ(current)
