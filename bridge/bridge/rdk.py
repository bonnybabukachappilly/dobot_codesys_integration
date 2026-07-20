from time import sleep
from robodk.robolink import Robolink
from bridge.mechanisms.main_assembly import TVMainAssemblyMechanism
from bridge.mechanisms.tv_support import TVSupportMechanism
from bridge.assembly.base import BaseAssemblyPNP
from bridge.mechanisms.in_feed_rack import (
    in_feed_reset, in_feed_create,
    in_feed_to_passive, in_feed_to_active
)

RDK = Robolink()

assembly_mech = TVMainAssemblyMechanism()
support_mech = TVSupportMechanism()

base_assembly = BaseAssemblyPNP(slider=assembly_mech)


def main() -> None:
    in_feed_create()
    in_feed_to_active()
    base_assembly.run()
    assembly_mech.update()


def reset() -> None:
    in_feed_reset()
    in_feed_to_passive()
    in_feed_create()
    in_feed_to_active()

    assembly_mech.set_home()
    assembly_mech.reset_parts()
    # assembly_mech.create_parts()

    support_mech.reset_parts()
    support_mech.set_home()
    support_mech.create_parts()
