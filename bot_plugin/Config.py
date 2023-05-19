from typing import Dict, List

from mcdreforged.utils.serializer import Serializable


class CommandInfo(Serializable):
    cmd: str = ''
    color: str = '#FFFFFF'


class BotInfo(Serializable):
    pos: List[float] = [0, 0, 0]
    rotation: List[float] = [0, 0]
    dim: str = 'minecraft:overworld'
    commands: Dict[str, CommandInfo] = []


class Config(Serializable):
    bots: Dict[str, BotInfo] = {
        'demo':
        BotInfo(pos=[0, 0, 0],
                rotation=[0, 0],
                commands={
                    's': CommandInfo(cmd='spawn', color='#00FFFF'),
                    'k': CommandInfo(cmd='kill', color='#FF0000')
                })
    }
    command_perm: Dict[str, int] = {
        'add': 2,
        'list': 0,
        'del': 2,
        'info': 0,
        'moveto': 2,
        'reload': 3,
        'rename': 2,
        'run': 1,
        'setcmd': 2,
    }
    bot_prefix: str = ''
    bot_suffix: str = ''
    fz_pack_tolerate: bool = False
