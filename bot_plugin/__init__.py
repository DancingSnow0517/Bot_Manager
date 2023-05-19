import json
import time
import math
import re
import os

from mcdreforged.api.all import *
from mcdreforged.translation.translation_text import RTextMCDRTranslation

from .Config import Config, BotInfo, CommandInfo

config: Config
plugin_server: PluginServerInterface

CONFIG_FILE = os.path.join('config', 'bots.json')
PLUGIN_ID = 'bot_plugin'
Prefix = '!!bot'

dim_id = {
    -1: 'minecraft:the_nether',
    0: 'minecraft:overworld',
    1: 'minecraft:the_end'
}

helps = [
    'add',
    'del',
    'info',
    'list',
    'move',
    'reload',
    'rename',
    'run',
    'setcmd',
]

namechar_ascii_width_pixels = {
    '0': 5,
    '1': 5,
    '2': 5,
    '3': 5,
    '4': 5,
    '5': 5,
    '6': 5,
    '7': 5,
    '8': 5,
    '9': 5,
    'A': 5,
    'B': 5,
    'C': 5,
    'D': 5,
    'E': 5,
    'F': 5,
    'G': 5,
    'H': 5,
    'I': 3,
    'J': 5,
    'K': 5,
    'L': 5,
    'M': 5,
    'N': 5,
    'O': 5,
    'P': 5,
    'Q': 5,
    'R': 5,
    'S': 5,
    'T': 5,
    'U': 5,
    'V': 5,
    'W': 5,
    'X': 5,
    'Y': 5,
    'Z': 5,
    'a': 5,
    'b': 5,
    'c': 5,
    'd': 5,
    'e': 5,
    'f': 4,
    'g': 5,
    'h': 5,
    'i': 1,
    'j': 5,
    'k': 4,
    'l': 2,
    'm': 5,
    'n': 5,
    'o': 5,
    'p': 5,
    'q': 5,
    'r': 5,
    's': 5,
    't': 3,
    'u': 5,
    'v': 5,
    'w': 5,
    'x': 5,
    'y': 5,
    'z': 5,
    '_': 5,
}

namechar_unicode_width_pixels = {
    '0': 6,
    '1': 5,
    '2': 6,
    '3': 6,
    '4': 6,
    '5': 6,
    '6': 6,
    '7': 6,
    '8': 6,
    '9': 6,
    'A': 6,
    'B': 6,
    'C': 6,
    'D': 6,
    'E': 6,
    'F': 6,
    'G': 6,
    'H': 6,
    'I': 5,
    'J': 7,
    'K': 6,
    'L': 6,
    'M': 6,
    'N': 6,
    'O': 6,
    'P': 6,
    'Q': 6,
    'R': 6,
    'S': 6,
    'T': 7,
    'U': 6,
    'V': 7,
    'W': 6,
    'X': 6,
    'Y': 7,
    'Z': 6,
    'a': 6,
    'b': 6,
    'c': 6,
    'd': 6,
    'e': 6,
    'f': 5,
    'g': 6,
    'h': 6,
    'i': 5,
    'j': 5,
    'k': 6,
    'l': 5,
    'm': 6,
    'n': 6,
    'o': 6,
    'p': 6,
    'q': 6,
    'r': 6,
    's': 6,
    't': 5,
    'u': 6,
    'v': 6,
    'w': 6,
    'x': 6,
    'y': 6,
    'z': 6,
    '_': 7,
}


def tr(translation_key: str, *args) -> RTextMCDRTranslation:
    return ServerInterface.get_instance().rtr(
        translation_key.format(PLUGIN_ID), *args)


def save_config():
    plugin_server.save_config_simple(config=config,
                                     in_data_folder=False,
                                     file_name=CONFIG_FILE)


def load_config():
    global config
    config = plugin_server.load_config_simple(file_name=CONFIG_FILE,
                                              in_data_folder=False,
                                              target_class=Config)


def print_help_message(source: CommandSource):

    def to_help_msg(prefix: str, des: str) -> list:
        ret = [{
            'text': prefix + f' {des} ',
            'color': '#999D9C'
        },
               tr('help.{}.' + des).set_color(RColor.white).to_json_object()]
        return ret

    if isinstance(source, PlayerCommandSource):
        player = source.player
        server = source.get_server()
        for i in helps:
            server.execute(
                f'tellraw {player} {json.dumps(to_help_msg(Prefix, i))}')
    else:
        for i in helps:
            source.reply(tr('help.{}.' + i))


@new_thread(PLUGIN_ID)
def show_list(source: CommandSource):
    '''
    显示bot的名称与可用命令
    例：demo        [s] [k] [+]
    玩家输入指令，将显示按钮，并添加悬浮窗、单击事件
    控制台输入指令，将显示命令内容
    '''
    server = source.get_server()
    entries = []
    for i in config.bots.keys():
        bot = config.bots[i]
        bot_data = []
        # 显示内容分名称，中部的留白和指令
        bot_data.append(i)
        # 计算留白的长度，按像素点为单位，补足约20个空格字符的空间
        name_display_width = 0
        reserved_space = 20
        lang = server.get_mcdr_language()
        if lang == 'en_us':
            # 英文环境，假设客户端不开启强制Unicode
            # 但是其实不应该这样假设，怎么能硬要中国人用英文端
            for char in i:
                # bot也是玩家，名字的字符只能是标识符字符
                # 提前查表计算长度
                name_display_width += namechar_ascii_width_pixels[char]
            reserved_space -= math.floor(name_display_width / 5)
        else:
            # 中文环境，假设客户端开启了强制Unicode
            for char in i:
                name_display_width += namechar_unicode_width_pixels[char]
            reserved_space -= math.ceil(name_display_width / 7)
        bot_data.append(' ' * reserved_space)
        # 逐个记录指令
        for j in bot.commands:
            bot_data.append((j, bot.commands[j].cmd))
        entries.append(bot_data)
        # 收集完毕，开始输出
    if isinstance(source, PlayerCommandSource):
        raw = []
        for bot_data in entries:
            # entries: [bot名称, 留白区域, (指令按钮,指令内容)*n]
            bot_name = bot_data[0]
            show_text_str = tr('message.{}.show_text')
            # 可点击的bot名称，留白区域也要可以点
            name_raw = {
                'text': f'{bot_name+bot_data[1]}',
                'color': '#ED6DF1',
                'hoverEvent': {
                    'action': 'show_text',
                    'value': f'{show_text_str}'
                },
                'clickEvent': {
                    'action': 'run_command',
                    'value': f'{Prefix} info {bot_name}'
                }
            }
            raw.append(name_raw)
            # 指令按钮的命令显示要用实际的bot名字
            # spawn指令除外，按照保存的名字显示，前后缀是carpet加的
            # 单击事件提交bot名字也按照保存的名字
            display_name: str
            for cmd in bot_data[2:]:
                if cmd[1] == 'spawn':
                    display_name = bot_name
                else:
                    display_name = config.bot_prefix + bot_name + config.bot_suffix
                action_raw = {
                    'text': f' [{cmd[0]}]',
                    'hoverEvent': {
                        'action': 'show_text',
                        'value': f'/player {display_name} {cmd[1]}'
                    },
                    'clickEvent': {
                        'action': 'run_command',
                        'value': f'{Prefix} run {display_name} {cmd[0]}'
                    },
                    'color': config.bots[bot_name].commands[cmd[0]].color
                }
                raw.append(action_raw)
            # 显示一个添加命令用的按钮
            show_text_str = tr('message.{}.add_cmd')
            action_raw = {
                'text': ' [+]',
                'hoverEvent': {
                    'action': 'show_text',
                    'value': f'{show_text_str}'
                },
                'clickEvent': {
                    'action': 'suggest_command',
                    'value': f'{Prefix} setcmd {bot_name} <key> <command>'
                },
                'color': '#FF7F00'
            }
            raw.append(action_raw)
            raw.append('\n')
        source.reply(tr('message.{}.bot_list_title'))
        server.execute(f'tellraw {source.player} {json.dumps(raw)}')
        source.reply(tr('message.{}.bot_total', len(config.bots)))
    else:
        source.reply(tr('message.{}.bot_list_title'))
        s = ''
        for bot_data in entries:
            # 直接显示bot的具体命令
            ss = ''
            for cmd in bot_data[2:]:
                ss += f' "{cmd[0]}": "{cmd[1]}",'
            # 格式化输出bot的名字，留白，具体命令（多出来的逗号删掉）
            s += f'{bot_data[0]} {ss[:-1]}\n'
        source.reply(s)
        source.reply(tr('message.{}.bot_total', len(config.bots)))


@new_thread(PLUGIN_ID)
def add_bot_p(source: CommandSource, ctx):
    '''
    添加bot
    仅限玩家操作，不需要提供坐标，维度和视角
    '''
    global config
    server = source.get_server()
    if isinstance(source, ConsoleCommandSource):
        source.reply(tr('message.{}.bad_executor_type').set_color(RColor.red))
        source.reply(
            tr('message.{}.reject_console_action').set_color(RColor.red))
        return
    bot_name = ctx['name']
    if bot_name not in config.bots:
        api = server.get_plugin_instance('minecraft_data_api')
        pos = api.get_player_coordinate(source.player)
        dim = api.get_player_dimension(source.player)
        rotation = api.get_player_info(source.player, 'Rotation')
        config.bots[bot_name] = BotInfo(pos=[pos.x, pos.y, pos.z],
                                        rotation=rotation,
                                        dim=dim_id[dim],
                                        commands={
                                            's':
                                            CommandInfo(cmd='spawn',
                                                        color='#00FFFF'),
                                            'k':
                                            CommandInfo(cmd='kill',
                                                        color='#FF0000')
                                        })
        save_config()
        source.reply(tr('message.{}.bot_add_success').set_color(RColor.green))
    else:
        source.reply(tr('message.{}.bot_exist').set_color(RColor.red))


@new_thread(PLUGIN_ID)
def add_bot_c(source: CommandSource, ctx):
    '''
    添加bot
    需要提供坐标，维度和视角
    '''
    global config
    server = source.get_server()
    bot_name = ctx['name']
    api = server.get_plugin_instance('minecraft_data_api')
    if bot_name not in config.bots:
        # 传入的参数包括x, y, z, dim, yaw, pitch
        # x, y, z为必需, dim在玩家输入时可选，控制台必需，yaw, pitch可选
        pos = [ctx['x'], ctx['y'], ctx['z']]
        dim = 0
        rotation = (0, 0)
        try:
            if 'other' not in ctx:
                other = []
            else:
                other = str(ctx['other']).split()
            if len(other) == 0:
                # 无额外参数，所以必须是玩家
                if isinstance(source, PlayerCommandSource):
                    dim = api.get_player_dimension(source.player)
                    rotation = api.get_player_info(source.player, 'Rotation')
                else:
                    source.reply(tr('message.{}.bad_executor_type'))
                    source.reply(tr('message.{}.reject_console_action'))
            #只有1个额外参数，参数直接处理为维度
            if len(other) == 1:
                dim = int(other[0])
                if dim not in dim_id.keys():
                    raise IllegalArgument()
            #有2个额外参数，比较麻烦
            if len(other) == 2:
                if isinstance(source, PlayerCommandSource):
                    # 玩家提供两个参数，认为是指定了视角
                    dim = api.get_player_dimension(source.player)
                    rotation = (int(other[0]), int(other[1]))
                elif isinstance(source, ConsoleCommandSource):
                    # 控制台提供两个参数，这是不允许的
                    source.reply(tr('message.{}.bad_executor_type'))
                    source.reply(tr('message.{}.reject_console_action'))
            #有至少3个额外参数，那就是都指定了，多余的参数废弃
            if len(other) >= 3:
                dim = int(other[0])
                if dim not in dim_id.keys():
                    raise IllegalArgument()
                rotation = (int(other[0]), int(other[1]))

            config.bots[bot_name] = BotInfo(pos=pos,
                                            rotation=rotation,
                                            dim=dim_id[dim],
                                            commands={
                                                's':
                                                CommandInfo(cmd='spawn',
                                                            color='#00FFFF'),
                                                'k':
                                                CommandInfo(cmd='kill',
                                                            color='#FF0000')
                                            })
            save_config()
            source.reply(
                tr('message.{}.bot_add_success').set_color(RColor.green))
        except Exception:
            source.reply(
                tr('message.{}.bad_executor_type').set_color(RColor.red))
    else:
        source.reply(tr('message.{}.bot_exist').set_color(RColor.red))


def remove(source: CommandSource, ctx):
    global config
    bot_name = ctx['name']
    if bot_name in config.bots:
        del config.bots[bot_name]
        save_config()
        source.reply(
            tr('message.{}.bot_remove_success').set_color(RColor.green))
    else:
        source.reply(tr('message.{}.bot_not_exist').set_color(RColor.red))


def setcmd(source: CommandSource, ctx):
    global config
    bot_name = ctx['name']
    if bot_name not in config.bots:
        source.reply(tr('message.{}.bot_not_exist').set_color(RColor.red))
        return
    k = ctx['key']
    if k in config.bots[bot_name].commands:
        #玩家不可以重复设置's'和'k'键，他们默认为召唤和踢出bot
        #但是控制台可以任意改动
        if (k == 's' or k == 'k') and isinstance(source, PlayerCommandSource):
            source.reply(
                tr('message.{}.bad_executor_type').set_color(RColor.red))
            source.reply(
                tr('message.{}.reject_player_action').set_color(RColor.red))
            return
        source.reply(tr('message.{}.setcmd_overwrite').set_color(RColor.gold))
    config.bots[bot_name].commands[ctx['key']] = CommandInfo(cmd=ctx['cmd'],
                                                             color='#FFFF00')
    save_config()
    source.reply(tr('message.{}.setcmd_success').set_color(RColor.green))


def reload(source: CommandSource):
    load_config()
    source.reply(tr('message.{}.reload_success').set_color(RColor.green))


def move(source: CommandSource, ctx):
    global config
    bot_name = ctx['name']
    if bot_name not in config.bots:
        source.reply(tr('message.{}.bot_not_exist').set_color(RColor.red))
        return
    pos = [ctx['x'], ctx['y'], ctx['z']]
    conf2 = config.bots[bot_name]
    del config.bots[bot_name]
    conf2.pos = pos
    config.bots[bot_name] = conf2
    save_config()
    source.reply(tr('message.{}.move_success').set_color(RColor.green))


def rename(source: CommandSource, ctx):
    global config
    bot_name = ctx['name']
    if bot_name not in config.bots:
        source.reply(tr('message.{}.bot_not_exist').set_color(RColor.red))
        return
    config.bots[ctx['new_name']] = config.bots[bot_name]
    del config.bots[bot_name]
    save_config()
    source.reply(tr('message.{}.change_name_success').set_color(RColor.green))


def delete(source: CommandSource, ctx):
    global config
    bot_name = ctx['name']
    if bot_name not in config.bots:
        source.reply(tr('message.{}.bot_not_exist').set_color(RColor.red))
        return
    del config.bots[bot_name]
    save_config()
    source.reply(tr('message.{}.bot_delete_success').set_color(RColor.green))


@new_thread(PLUGIN_ID)
def run(source: CommandSource, ctx):
    name = ctx['name']
    key = ctx['key']
    server = source.get_server()
    if ctx['name'] in config.bots:
        if ctx['key'] in config.bots[name].commands:
            if config.bots[name].commands[key].cmd == 'spawn':
                info = config.bots[name]
                server.execute(
                    f'player {name} spawn at {info.pos[0]} {info.pos[1]} {info.pos[2]} facing {info.rotation[0]} {info.rotation[1]} in {info.dim}'
                )
            else:
                bot_name = config.bot_prefix + name + config.bot_suffix
                server.execute(
                    f'player {bot_name} {config.bots[name].commands[key].cmd}')
        else:
            source.reply(tr('message.{}.key_not_exist').set_color(RColor.red))
    else:
        source.reply(tr('message.{}.bot_not_exist').set_color(RColor.red))


def info(source: CommandSource, ctx):
    name = ctx['name']
    if name not in config.bots:
        source.reply(tr('message.{}.bot_not_exist').set_color(RColor.red))
        return
    bot = config.bots[name]
    source.reply(tr('info.{}.name', name))
    source.reply(
        tr('info.{}.detail_pos', bot.dim, int(bot.pos[0]), int(bot.pos[1]),
           int(bot.pos[2])))
    source.reply(
        tr('info.{}.detail_rotation', int(bot.rotation[0]),
           int(bot.rotation[1])))


def register_command(server: PluginServerInterface):

    def get_literal_node(literal):
        lvl = config.command_perm.get(literal, 0)
        return Literal(literal).requires(lambda src: src.has_permission(lvl)). \
            on_error(RequirementNotMet,
                     lambda src: src.reply(
                         tr('message.{}.permission_denied')),
                     handled=True)

    server.register_command(
        Literal(Prefix).runs(print_help_message).then(
            get_literal_node('list').runs(show_list)).then(
                get_literal_node('add').runs(lambda src: src.reply(
                    tr('usage.{}.add', Prefix).set_color(RColor.gray))).then(
                        Text('name').in_length_range(
                            1, 16 - len(config.bot_prefix) -
                            len(config.bot_suffix)).runs(add_bot_p).then(
                                Float('x').then(
                                    Float('y').then(
                                        Float('z').runs(add_bot_c).then(
                                            GreedyText('other').runs(
                                                add_bot_c))))))
            ).then(
                get_literal_node('del').runs(lambda src: src.reply(
                    tr('usage.{}.del', Prefix).set_color(RColor.gray))).then(
                        Text('name').runs(delete))).
        then(
            get_literal_node('setcmd').runs(lambda src: src.reply(
                tr('usage.{}.setcmd', Prefix).set_color(RColor.gray))).then(
                    Text('name').then(
                        Text('key').in_length_range(1, 1).then(
                            GreedyText('cmd').runs(setcmd))))
        ).then(Literal('reload').runs(reload)).then(
            Literal('run').runs(lambda src: src.reply(
                tr('usage.{}.run', Prefix).set_color(RColor.gray))).then(
                    Text('name').then(
                        Text('key').in_length_range(1, 1).runs(run)))).then(
                            Literal('info').runs(lambda src: src.reply(
                                tr('usage.{}.info', Prefix).set_color(
                                    RColor.gray))).then(
                                        Text('name').runs(info))).
        then(
            Literal('rename').runs(lambda src: src.reply(
                tr('usage.{}.rename', Prefix).set_color(RColor.gray))).then(
                    Text('name').then(
                        Text('new_name').in_length_range(
                            1, 16 - len(config.bot_prefix) -
                            len(config.bot_suffix)).runs(rename)))
        ).then(
            Literal('move').runs(lambda src: src.reply(
                tr('usage.{}.move', Prefix).set_color(RColor.gray))).then(
                    Text('name').then(
                        Float('x').then(
                            Float('y').then(Float('z').runs(move)))))))


def on_load(server: PluginServerInterface, old_module):
    '''
    加载配置
    '''
    global plugin_server
    plugin_server = server
    load_config()
    register_command(server)
    server.register_help_message(Prefix, tr('message.{}.bot'))
    if server.is_server_startup():
        on_server_startup(server)


detect_fz_pack: bool = False


@new_thread(PLUGIN_ID)
def on_server_startup(server: PluginServerInterface):
    '''
    如果有FZ生存数据包，则根据避让策略调整
    false: 强制允许/player指令，即使FZ生存数据包提供的tagplayer等功能存在
    true: 放弃使用/player指令，屈服于FZ生存数据包，并卸载本插件
    '''
    global detect_fz_pack
    time.sleep(1)
    if config.fz_pack_tolerate:
        # 检查可能出现的FZ生存数据包，然后通过控制台输出决定怎么办
        server.execute('datapack list')
        detect_fz_pack = True
    else:
        server.execute('carpet commandPlayer true')


def on_info(server: PluginServerInterface, info: Info):
    global detect_fz_pack
    if config.fz_pack_tolerate:
        if detect_fz_pack:
            detect_fz_pack = False
            pat = '.* \\d+ data packs enabled'
            if re.match(pat, info.content):
                if 'file/FZ Survival Data Pack' in info.content:
                    #真的有开启FZ生存数据包，而且是屈服（True），快跑
                    server.unload_plugin('bot_plugin')