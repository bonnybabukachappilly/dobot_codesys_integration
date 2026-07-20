from typing import NamedTuple

from robodk.robolink import Item, Robolink
from robodk import robolink
from robodk.robomath import Mat

# ****************************************************************************

MECHANISM_NAME = 'm_TV_MainAssembly'
TOOL_NAME_BASE = 't_TV_MainAssembly_base'
TOOL_NAME_PCB = 't_TV_MainAssembly_pcb'
TOOL_NAME_SCREW = 't_TV_MainAssembly_screw'
TOOL_NAME_ASSEMBLY = 't_TV_MainAssembly_assembly'

# Merged Names
BASE_NAME = 'merged_base_assembly'
PCB_NAME = 'merged_sub_assembly'
SCREW_NAME = 'merged_base_assembly'

# Frames
TOOL_FRAME = 'f_TV_MainAssembly'
REF_PART_FRAME = 'f_Ref_TV_MainAssembly'

# Objects
REF_PART_NAME = 'TV_MainAssembly_Ref'

# Targets
HOME_JOINT: list[float] = [200000.00]
INCREMENT_JOINT: float = -1040.00

# Speed & Acceleration
JOINT_SPEED = 500.0
JOINT_ACCELERATION = 250.0

# ****************************************************************************
# self._rdk.ShowMessage(str(type(current)))


class MainAssemblyFrames(NamedTuple):
    tool: Item
    ref_part: Item


class TVMainAssemblyMechanism:
    def __init__(self) -> None:
        self._rdk = Robolink()

        self._mechanism: Item = self._rdk.Item(
            MECHANISM_NAME, robolink.ITEM_TYPE_ROBOT)
        self._tool_base: Item = self._rdk.Item(
            TOOL_NAME_BASE, robolink.ITEM_TYPE_TOOL)
        self._tool_pcb: Item = self._rdk.Item(
            TOOL_NAME_PCB, robolink.ITEM_TYPE_TOOL)
        self._tool_screw: Item = self._rdk.Item(
            TOOL_NAME_SCREW, robolink.ITEM_TYPE_TOOL)
        self._tool_assembly: Item = self._rdk.Item(
            TOOL_NAME_ASSEMBLY, robolink.ITEM_TYPE_TOOL)
        self._frames: MainAssemblyFrames = self.__create_frames()

        self._home_joints: list[float] = HOME_JOINT
        self._inc_joints: float = INCREMENT_JOINT

        self._ref_part_name = REF_PART_NAME
        self._tolerance = 0.1

        self.initialize()

    def initialize(self) -> None:
        # self._mechanism.setTool(self._tool)

        if 'JOINT_SPEED' in globals():
            self._mechanism.setSpeedJoints(globals()['JOINT_SPEED'])
        if 'JOINT_ACCELERATION' in globals():
            self._mechanism.setAccelerationJoints(
                globals()['JOINT_ACCELERATION'])

    @property
    def _new_part_name(self) -> str:
        return self._ref_part_name.replace('Ref', 'New')

    @property
    def base_tool(self) -> Item:
        return self._tool_base

    @property
    def pcb_tool(self) -> Item:
        return self._tool_pcb

    @property
    def screw_tool(self) -> Item:
        return self._tool_screw

    def __create_frames(self) -> MainAssemblyFrames:
        return MainAssemblyFrames(
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

        del_list: list[str] = [self._new_part_name,
                               BASE_NAME, PCB_NAME, SCREW_NAME]

        for item in items:
            if item.Name() in del_list:
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
        self.__merge_items()
        self.__swap_items()

        current = self._mechanism.Joints().tolist()
        current[0] += self._inc_joints
        self._mechanism.MoveJ(current)

    def __merge_items(self) -> None:
        if merge := [
            child
            for child in self.base_tool.Childs()
            if 'support' not in child.Name().lower()
        ]:
            item: Item = self._rdk.MergeItems(merge)
            item.setName(BASE_NAME)

    def __swap_items(self) -> None:
        # Swap to assembly

        # Swap to screw

        # Swap to pcb
        if children := self._tool_base.Childs():
            for child in children:
                child.setParent(self._tool_pcb)
