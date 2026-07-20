from typing import NamedTuple

from robodk.robolink import Item, Robolink
from robodk import robolink
from robodk.robomath import Mat

# ****************************************************************************

MECHANISM_NAME = 'm_TV_Rack_Rim'
TOOL_NAME = 't_TV_Rack_Rim'

# Frames
TOOL_FRAME = 'f_TV_Rack_Rim'
REF_PART_FRAME = 'f_Ref_TV_Rack_Rim'
TARGET_FRAME = 'f_TV_Rack_Rail_Targets'

# Objects
REF_PART_NAME = 'TVRim_Ref'

# Targets
TARGETS: dict[str, str] = {
    'corner_lb': 't_rack_rim_lb',
    'corner_lt': 't_rack_rim_lt',
    'corner_rt': 't_rack_rim_rt',
    'corner_rb': 't_rack_rim_rb',
    'active': 't_rack_rim_active',
    'passive': 't_rack_rim_passive'
}

# Speed & Acceleration
JOINT_SPEED = 2000.0
JOINT_ACCELERATION = 2500.0

# ****************************************************************************
# self._rdk.ShowMessage(str(type(current)))


class RimTargets(NamedTuple):
    corner_lb: Item
    corner_lt: Item
    corner_rt: Item
    corner_rb: Item
    active: Item
    passive: Item


class RimFrames(NamedTuple):
    tool: Item
    ref_part: Item
    target: Item


class TVRimMechanism:
    def __init__(self) -> None:
        self._rdk = Robolink()

        self._mechanism: Item = self._rdk.Item(
            MECHANISM_NAME, robolink.ITEM_TYPE_ROBOT)
        self._tool: Item = self._rdk.Item(TOOL_NAME, robolink.ITEM_TYPE_TOOL)
        self._targets: RimTargets = self.__create_targets()
        self._frames: RimFrames = self.__create_frames()

        self._ref_part_name = REF_PART_NAME
        self._tolerance = 0.1

        self.initialize()

    def initialize(self) -> None:
        self._mechanism.setTool(self._tool)
        self._mechanism.setFrame(self._frames.target)

        if 'JOINT_SPEED' in globals():
            self._mechanism.setSpeedJoints(globals()['JOINT_SPEED'])
        if 'JOINT_ACCELERATION' in globals():
            self._mechanism.setAccelerationJoints(
                globals()['JOINT_ACCELERATION'])

    @property
    def _new_part_name(self) -> str:
        return self._ref_part_name.replace('Ref', 'New')

    def __create_frames(self) -> RimFrames:
        return RimFrames(
            tool=self._rdk.Item(TOOL_FRAME, robolink.ITEM_TYPE_FRAME),
            ref_part=self._rdk.Item(REF_PART_FRAME, robolink.ITEM_TYPE_FRAME),
            target=self._rdk.Item(TARGET_FRAME, robolink.ITEM_TYPE_FRAME)
        )

    def __create_targets(self) -> RimTargets:
        _items: dict[str, Item] = {
            key: self._rdk.Item(name, robolink.ITEM_TYPE_TARGET)
            for key, name in TARGETS.items()
        }

        return RimTargets(**_items)

    def __check_in_pos(self, target: Item) -> bool:
        current: list[float] = self._mechanism.Joints().tolist()
        check: list[float] = target.Joints().tolist()

        return all(
            abs(c-t) < self._tolerance for c, t in zip(current, check)
        )

    def set_home(self) -> None:
        self._mechanism.setJoints(self._targets.passive)

    def move_home(self) -> None:
        self._mechanism.MoveJ(self._targets.passive)

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

    def move_active(self) -> None:
        if self.__check_in_pos(self._targets.active):
            return

        self._mechanism.MoveJ(self._targets.corner_lb)
        self._mechanism.MoveJ(self._targets.corner_lt)
        self._mechanism.MoveJ(self._targets.active)

    def move_passive(self) -> None:
        if self.__check_in_pos(self._targets.passive):
            return

        self._mechanism.MoveJ(self._targets.corner_rt)
        self._mechanism.MoveJ(self._targets.corner_rb)
        self._mechanism.MoveJ(self._targets.passive)
