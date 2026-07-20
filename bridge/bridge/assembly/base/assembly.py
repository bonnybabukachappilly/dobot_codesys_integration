from threading import Thread
from typing import Optional
from robodk.robolink import Robolink, Item
from robodk.robomath import Mat, transl

from bridge.assembly.utils import RobotHome, ToolType
from bridge.mechanisms.main_assembly import TVMainAssemblyMechanism

from .components import Robot, make_robot

OFFSET = 300


class BaseAssemblyPNP:
    def __init__(self, slider: TVMainAssemblyMechanism) -> None:
        self._rdk = Robolink()
        self._robot: Robot = make_robot()
        self._slider: TVMainAssemblyMechanism = slider

        self.initialize()
        self._active_tool: Item
        self._active_tool_type: ToolType

        self._gripper_target: list[float]
        # self._attached_part: Item

    def initialize(self) -> None:
        self.__set_gripper()
        self._robot.robot.setFrame(self._robot.target_frame)

    def __set_gripper(self) -> None:
        self._robot.robot.setTool(self._robot.tool_gripper)
        self._active_tool = self._robot.tool_gripper
        self._active_tool_type = ToolType.GRIPPER

    def __set_vacuum(self) -> None:
        self._robot.robot.setTool(self._robot.tool_vacuum)
        self._active_tool = self._robot.tool_vacuum
        self._active_tool_type = ToolType.VACUUM

    def __attach(self) -> None:
        self._active_tool.AttachClosest(tolerance_mm=600)
        # self._attached_part = self._active_tool.Childs()[0]

    def __detach(self) -> None:
        attached: Item = self._active_tool.Childs()[0]
        attached.setParentStatic(self._slider.base_tool)

    def __set_rect(self, offset: Mat, joints: Mat) -> Item:
        self._robot.targets.rect.setPose(offset)
        self._robot.targets.rect.setJoints(joints)
        return self._robot.targets.rect

    @property
    def is_gripper(self) -> bool:
        return self._active_tool_type == ToolType.GRIPPER

    @property
    def is_vacuum(self) -> bool:
        return self._active_tool_type == ToolType.VACUUM

    @property
    def gripper_target(self) -> list[float]:
        return self._gripper_target

    def set_home(self) -> None:
        self._robot.robot.setJoints(self._robot.targets.home_grip)

    def move_home(self) -> None:
        self._robot.robot.MoveJ(self._robot.targets.home_grip)

    def _pick(self, target: Item, home: Item, run_hm: RobotHome) -> None:
        # Configuration
        offset: Mat = transl(0, 0, OFFSET) * target.Pose()
        joints: Mat = target.Joints()

        robot: Item = self._robot.robot
        rect: Item = self.__set_rect(offset, joints)

        th: Optional[Thread] = None

        # Gripper Action
        if self.is_gripper:
            th = Thread(
                target=self._robot.gripper.mech.MoveJ,
                args=(self._robot.gripper.targets.open, ),
                daemon=True
            )
            th.start()

        # Home
        if run_hm in [RobotHome.START, RobotHome.BOTH]:
            robot.MoveJ(home)

        # Pick
        robot.MoveJ(rect)

        if th:
            th.join()

        robot.MoveL(target)

        # Gripper Action
        if self.is_gripper:
            self._robot.gripper.mech.MoveJ(self.gripper_target)

        self.__attach()

        robot.MoveL(rect)

        # Home
        if run_hm in [RobotHome.END, RobotHome.BOTH]:
            robot.MoveJ(home)

    def _place(self, target: Item, home: Item, run_hm: RobotHome) -> None:
        # Configuration
        offset: Mat = transl(0, 0, OFFSET) * target.Pose()
        joints: Mat = target.Joints()

        robot: Item = self._robot.robot
        rect: Item = self.__set_rect(offset, joints)

        # Home
        if run_hm in [RobotHome.START, RobotHome.BOTH]:
            robot.MoveJ(home)

        # Place
        robot.MoveJ(rect)
        robot.MoveL(target)
        self.__detach()

        # Gripper Action
        if self.is_gripper:
            self._robot.gripper.mech.MoveJ(self._robot.gripper.targets.open)

        robot.MoveL(rect)

        # Home
        if run_hm in [RobotHome.END, RobotHome.BOTH]:
            robot.MoveJ(home)

    def run(self) -> None:
        # Change to gripper
        self.__set_gripper()
        self._gripper_target = self._robot.gripper.targets.panel_grip

        # *********************** Pick & Place Support ***********************
        self._pick(self._robot.targets.support_pick,
                   self._robot.targets.hm_support, run_hm=RobotHome.START)

        self._place(self._robot.targets.support_place,
                    self._robot.targets.hm_place_grip, run_hm=RobotHome.NONE)

        # Change to gripper
        self._gripper_target = self._robot.gripper.targets.panel_grip

        # *********************** Pick & Place Panel ***********************
        self._pick(self._robot.targets.panel_pick,
                   self._robot.targets.hm_grip, run_hm=RobotHome.BOTH)

        self._place(self._robot.targets.panel_place,
                    self._robot.targets.hm_place_grip, run_hm=RobotHome.NONE)

        # Change to vacuum
        self.__set_vacuum()

        # *********************** Pick & Place Panel ***********************
        self._pick(self._robot.targets.screen_pick,
                   self._robot.targets.hm_vac, run_hm=RobotHome.BOTH)

        self._place(self._robot.targets.screen_place,
                    self._robot.targets.hm_vac, run_hm=RobotHome.NONE)

        # Change to gripper
        self.__set_gripper()
        self._gripper_target = self._robot.gripper.targets.rim_grip

        # *********************** Pick & Place Panel ***********************
        self._pick(self._robot.targets.rim_pick,
                   self._robot.targets.hm_grip, run_hm=RobotHome.BOTH)

        self._place(self._robot.targets.rim_place,
                    self._robot.targets.hm_place_grip, run_hm=RobotHome.END)
