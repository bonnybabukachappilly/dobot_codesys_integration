from time import sleep
from robodk.robolink import Robolink


RDK = Robolink()


def main() -> None:
    RDK.ShowMessage('Working')
