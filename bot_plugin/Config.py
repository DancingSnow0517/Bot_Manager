from typing import Dict, List

from mcdreforged.utils.serializer import Serializable


class CommandInfo(Serializable):
    cmd: str = ''
    color: str = ''


class BotInfo(Serializable):
    pos: List[float] = [0, 0, 0]
    rotation: List[float] = [0, 0]
    dim: str = 'minecraft:overworld'
    commands: Dict[str, CommandInfo] = []


class Config(Serializable):
    bots: Dict[str, BotInfo] = {
        "test": BotInfo(pos=[0, 0, 0], rotation=[0, 0], commands={
            "S": CommandInfo(cmd='spawn', color='#F2ACDA')
        })
    }
    command_perm: Dict[str, int] = {
        "list": 0,
        "add": 2,
        "remove": 2,
        "modify": 2,
        "run": 0,
        "reload": 2
    }
    bot_prefix: str = ''
    bot_suffix: str = ''
