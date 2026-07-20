from typing import NamedTuple

from robodk import robolink
from robodk.robolink import Item, Robolink


ROBOT = 'r_TV_BaseAssembly'
TOOL_GRIPPER = 't_TV_BaseAssemblyGripper'
TOOL_VACUUM = 't_TV_BaseAssemblyVacuum'
TOOL_FRAME = 'f_TV_BaseAssembly'

TARGET_FRAME = 'f_TV_BaseAssembly_Targets'


TARGETS: dict[str, str] = {
    'panel_pick': 't_rack_panel_pick',
    'rim_pick': 't_rack_rim_pick',
    'screen_pick': 't_rack_screen_pick',
    'support_pick': 't_rack_support_pick',
    'panel_place': 't_rack_panel_place',
    'rim_place': 't_rack_rim_place',
    'screen_place': 't_rack_screen_place',
    'support_place': 't_rack_support_place',
    'rect': 't_base_assembly_rect',
    'hm_support': 'J_ASSM_SUPPORT_HOME',
    'hm_grip': 'J_ASSM_GRIP_HOME',
    'hm_vac': 'J_ASSM_VACUUM_HOME',
    'hm_place_grip': 'J_ASSM_PLACE_GRIP_HOME',
    'hm_place_vacuum': 'J_ASSM_PLACE_VACUUM_HOME',
}

GRIPPER_MECH = 'm_TV_BaseAssemblyMech'

GRIPPER_TARGETS: dict[str, list[float]] = {
    'panel_grip': [35.00],
    'rim_grip': [-10.00],
    'support_grip': [35.00],
    'open': [78.00],
}


class GripperTargets(NamedTuple):
    panel_grip: list[float]
    rim_grip: list[float]
    support_grip: list[float]
    open: list[float]


class Gripper(NamedTuple):
    mech: Item
    targets: GripperTargets


class Targets(NamedTuple):
    panel_pick: Item
    rim_pick: Item
    screen_pick: Item
    support_pick: Item
    panel_place: Item
    rim_place: Item
    screen_place: Item
    rect: Item
    support_place: Item
    hm_support: Item
    hm_grip: Item
    hm_vac: Item
    hm_place_grip: Item
    hm_place_vacuum: Item


class Robot(NamedTuple):
    robot: Item
    tool_gripper: Item
    tool_vacuum: Item
    target_frame: Item
    tool_frame: Item
    targets: Targets
    gripper: Gripper


def make_robot() -> Robot:
    rdk_gripper = Robolink()
    rdk_robot = Robolink()

    _targets: dict[str, Item] = {
        key: rdk_gripper.Item(name, robolink.ITEM_TYPE_TARGET)
        for key, name in TARGETS.items()
    }

    g_targets = GripperTargets(**GRIPPER_TARGETS)
    gripper = Gripper(
        mech=rdk_gripper.Item(GRIPPER_MECH, robolink.ITEM_TYPE_ROBOT),
        targets=g_targets
    )

    return Robot(
        robot=rdk_robot.Item(ROBOT, robolink.ITEM_TYPE_ROBOT),
        tool_gripper=rdk_robot.Item(TOOL_GRIPPER, robolink.ITEM_TYPE_TOOL),
        tool_vacuum=rdk_robot.Item(TOOL_VACUUM, robolink.ITEM_TYPE_TOOL),
        target_frame=rdk_robot.Item(TARGET_FRAME, robolink.ITEM_TYPE_FRAME),
        tool_frame=rdk_robot.Item(TOOL_FRAME, robolink.ITEM_TYPE_FRAME),
        targets=Targets(**_targets),
        gripper=gripper
    )
