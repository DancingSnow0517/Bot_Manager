import json
import re
import os.path

from mcdreforged.api.all import *
from mcdreforged.translation.translation_text import RTextMCDRTranslation

from bot_plugin.Config import Config, BotInfo, CommandInfo

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
colors = [
    '#e54d42',
    '#f37b1d',
    '#fbbd08',
    '#8dc63f',
    '#39b54a',
    '#1cbbb4',
    '#0081ff',
    '#6739b6',
    '#9c26b0',
    '#e03997',
    '#a5673f',
    '#8799a3'
]
helps = [
    'list',
    'add',
    'remove',
    'modify',
    'run',
    'reload',
    'info'
]


def tr(translation_key: str, *args) -> RTextMCDRTranslation:
    return ServerInterface.get_instance().rtr(translation_key.format(PLUGIN_ID), *args)


def save_config():
    plugin_server.save_config_simple(config=config, in_data_folder=False, file_name=CONFIG_FILE)


def load_config():
    global config
    config = plugin_server.load_config_simple(file_name=CONFIG_FILE, in_data_folder=False, target_class=Config)


def print_help_massage(source: PlayerCommandSource):
    def to_help_msg(prefix: str, des: str) -> list:
        ret = [{'text': prefix + f' {des} ', 'color': '#999D9C'}, tr('help.{}.' + des).set_color(RColor.white).to_json_object()]
        return ret
    player = source.player
    server = source.get_server()
    for i in helps:
        server.execute(f'tellraw {player} {json.dumps(to_help_msg(Prefix, i))}')


def show_list(source: PlayerCommandSource):
    """
    一共 30 空格
    [ ] = aa
    3空格 = aa
    """
    server = source.get_server()
    for i in config.bots:
        bot = config.bots[i]
        raw = []
        black_num = 30
        if len(i) % 2 == 0:
            raw.append({
                'text': f'{i}',
                'color': '#ED6DF1',
                "hoverEvent": {
                    "action": "show_text",
                    "value": "单击显示信息"
                },
                'clickEvent': {
                    'action': 'run_command',
                    'value': f'{Prefix} info {i}'
                }
            })
            black_num = int(black_num - len(i) / 2 * 3)
        else:
            raw.append({
                'text': f'{i} ',
                'color': '#ED6DF1',
                "hoverEvent": {
                    "action": "show_text",
                    "value": "单击显示信息"
                },
                'clickEvent': {
                    'action': 'run_command',
                    'value': f'{Prefix} info {i}'
                }
            })
            black_num = int(black_num - len(i) / 2 * 3 - 1)
        b = ''
        for j in range(black_num):
            b += ' '
        raw.append({'text': b})
        for j in bot.commands:
            raw.append({
                'text': f' [{j}]',
                'hoverEvent': {
                    'action': 'show_text',
                    'value': f'/player {i} {bot.commands[j].cmd}'
                },
                'clickEvent': {
                    'action': 'run_command',
                    'value': f'{Prefix} run {i} {j}'
                },
                'color': bot.commands[j].color
            })
        raw.append({
            'text': ' [+]',
            'hoverEvent': {
                'action': 'show_text',
                'value': '单击添加命令'
            },
            'clickEvent': {
                'action': 'suggest_command',
                'value': f'{Prefix} modify {i} commands <key> add '
            },
            'color': 'green'
        })
        server.execute(f'tellraw {source.player} {json.dumps(raw)}')
    print(len(config.bots))
    source.reply(tr('massage.{}.bot_totle', len(config.bots)))


@new_thread(PLUGIN_ID)
def add_bot(source: PlayerCommandSource, msg):
    global config
    server = source.get_server()
    bot_name = msg['name']
    if bot_name not in config.bots:
        api = server.get_plugin_instance('minecraft_data_api')
        pos = api.get_player_coordinate(source.player)
        dim = api.get_player_dimension(source.player)
        rotation = api.get_player_info(source.player, 'Rotation')
        config.bots[bot_name] = BotInfo(
            pos=[
                pos.x,
                pos.y,
                pos.z],
            rotation=rotation,
            dim=dim_id[dim],
            commands={"S": CommandInfo(cmd='spawn', color=colors[0])})
        save_config()
        source.reply(tr('massage.{}.bot_add_success').set_color(RColor.green))
    else:
        source.reply(tr('massage.{}.bot_exist').set_color(RColor.red))


def remove(source: PlayerCommandSource, msg):
    bot_name = msg['name']
    if bot_name in config.bots:
        del config.bots[bot_name]
        source.reply(tr('massage.{}.bot_remove_success').set_color(RColor.green))
    else:
        source.reply(tr('massage.{}.bot_not_exist').set_color(RColor.red))
    save_config()


def modifys(source: PlayerCommandSource, msg, T, cmd=None):
    bot_name = msg['name']
    if bot_name not in config.bots:
        source.reply(tr('massage.{}.bot_not_exist').set_color(RColor.red))
        return
    if T == 'cmd_add':
        if msg['key'] not in config.bots[bot_name].commands:
            config.bots[bot_name].commands[msg['key']] = CommandInfo(cmd=cmd, color=colors[
                len(config.bots[bot_name].commands) % len(colors)])
            source.reply(tr('massage.{}.command_add_success').set_color(RColor.green))
        else:
            source.reply(tr('massage.{}.key_exist').set_color(RColor.red))
        pass
    if T == 'cmd_remove':
        if msg['key'] in config.bots[bot_name].commands:
            del config.bots[bot_name].commands[msg['key']]
            source.reply(tr('massage.{}.command_remove_success').set_color(RColor.green))
        else:
            source.reply(tr('massage.{}.key_not_exist').set_color(RColor.red))
    if T == 'cmd_edit_color':
        if re.match('#[A-F|0-9].....', msg['color']) is None:
            source.reply(tr('massage.{}.color_not_match').set_color(RColor.red))
        elif msg['key'] in config.bots[bot_name].commands:
            config.bots[bot_name].commands[msg['key']].color = msg['color']
            source.reply(tr('massage.{}.change_color_success'))
        else:
            source.reply(tr('massage.{}.key_not_exist').set_color(RColor.red))
    if T == 'cmd_edit_cmd':
        if msg['key'] in config.bots[bot_name].commands:
            config.bots[bot_name].commands[msg['key']].cmd = msg['cmd']
            source.reply(tr('massage.{}.change_cmd_success').set_color(RColor.green))
        else:
            source.reply(tr('massage.{}.key_not_exist').set_color(RColor.red))
    if T == 'change_name':
        config.bots[msg['new_name']] = config.bots[bot_name]
        del config.bots[bot_name]
        source.reply(tr('massage.{}.change_name_success').set_color(RColor.green))
    save_config()


def reload(source: PlayerCommandSource):
    load_config()
    source.reply(tr('massage.{}.reload_success').set_color(RColor.green))


def fix_name(server: ServerInterface, name: str) -> str:
    api = server.get_plugin_instance('minecraft_data_api')
    amount, limit, player_list = api.get_server_player_list()
    for i in player_list:
        if i.upper() == name.upper():
            return i
    return name


@new_thread(PLUGIN_ID)
def run(source: PlayerCommandSource, msg):
    name = msg['name']
    key = msg['key']
    server = source.get_server()
    if msg['name'] in config.bots:
        if msg['key'] in config.bots[name].commands:
            if config.bots[name].commands[key].cmd == 'spawn':
                info = config.bots[name]
                server.execute(
                    f'execute as {source.player} run player {name} {config.bots[name].commands[key].cmd} at {info.pos[0]} {info.pos[1]} {info.pos[2]} facing {info.rotation[0]} {info.rotation[1]} in {info.dim}')
            else:
                bot_name = fix_name(source.get_server(), config.bot_prefix + name + config.bot_suffix)
                print(bot_name)
                server.execute(
                    f'execute as {source.player} run player {bot_name} {config.bots[name].commands[key].cmd}')
        else:
            source.reply(tr('massage.{}.key_not_exist').set_color(RColor.red))
    else:
        source.reply(tr('massage.{}.bot_not_exist').set_color(RColor.red))


def info(source: PlayerCommandSource, msg):
    bot_name = msg['name']
    if bot_name not in config.bots:
        source.reply(tr('massage.{}.bot_not_exist').set_color(RColor.red))
        return
    bot = config.bots[bot_name]
    source.reply(tr('info.{}.name', bot_name))
    source.reply(tr('info.{}.detail_pos', bot.dim, int(bot.pos[0]), int(bot.pos[1]), int(bot.pos[2])))
    source.reply(tr('info.{}.detail_rotation', int(bot.rotation[0]), int(bot.rotation[1])))


def register_command(server: PluginServerInterface):
    def get_literal_node(literal):
        lvl = config.command_perm.get(literal, 0)
        return Literal(literal).requires(lambda src: src.has_permission(lvl)). \
            on_error(RequirementNotMet,
                     lambda src: src.reply(
                         tr('massage.{}.permission_denied')),
                     handled=True)

    server.register_command(
        Literal(Prefix).
            runs(print_help_massage).
            then(
            get_literal_node('list').
                runs(show_list)
        ).
            then(
            get_literal_node('add').
                runs(lambda src: src.reply(tr('usage.{}.add', Prefix).set_color(RColor.gray))).
                then(
                Text('name').
                    at_min_length(1).
                    at_max_length(12).
                    runs(add_bot)
            )
        ).
            then(
            get_literal_node('remove').
                runs(lambda src: src.reply(tr('usage.{}.remove', Prefix).set_color(RColor.gray))).
                then(
                Text('name').
                    runs(remove)
            )
        ).
            then(
            get_literal_node('modify').
                runs(lambda src: src.reply(tr('usage.{}.modify', Prefix).set_color(RColor.gray))).
                then(
                Text('name').
                    then(
                    Literal('commands').
                        runs(lambda src: src.reply(tr('usage.{}.modify_commands', Prefix).set_color(RColor.gray))).
                        then(
                        Text('key').at_max_length(1).at_min_length(1).
                            then(
                            Literal('add').
                                then(
                                GreedyText('cmd').
                                    runs(lambda scr, msg: modifys(scr, msg, 'cmd_add', cmd=msg['cmd']))
                            )
                        ).
                            then(
                            Literal('remove').
                                runs(lambda src, msg: modifys(src, msg, 'cmd_remove'))
                        ).
                            then(
                            Literal('color').
                                then(
                                Text('color').
                                    runs(lambda src, msg: modifys(src, msg, 'cmd_edit_color'))
                            )
                        ).
                            then(
                            Literal('cmd').
                                then(
                                GreedyText('cmd').
                                    runs(lambda src, msg: modifys(src, msg, 'cmd_edit_cmd'))
                            )
                        )
                    )
                ).
                    then(
                    Literal('name').
                        runs(lambda src: src.reply(tr('usage.{}.modify_name', Prefix).set_color(RColor.gray))).
                        then(
                        Text('new_name').
                            runs(lambda src, msg: modifys(src, msg, 'change_name'))
                    )
                )
            )
        ).
            then(
            Literal('reload').
                runs(reload)
        ).
            then(
            Literal('run').
                runs(lambda src: src.reply(tr('usage.{}.run', Prefix).set_color(RColor.gray))).
                then(
                Text('name').
                    then(
                    Text('key').
                        runs(run)
                )
            )
        ).
            then(
            Literal('info').
            runs(lambda src: src.reply(tr('usage.{}.info', Prefix).set_color(RColor.gray))).
                then(
                Text('name').
                    runs(info)
            )
        )
    )


def on_load(server: PluginServerInterface, old_module):
    """
    Do some clean up when your plugin is being loaded
    Like migrating data, reading config file or adding help messages
    old_module is the previous plugin instance. If the plugin is freshly loaded it will be None
    """
    global plugin_server
    plugin_server = server
    load_config()
    register_command(server)


def on_unload(server: PluginServerInterface):
    """
    Do some clean up when your plugin is being unloaded. Note that it might be a reload
    """
    pass


def on_info(server: PluginServerInterface, info: Info):
    """
    Handler for general server output event
    Recommend to use on_user_info instead if you only care about info created by users
    """
    pass


def on_user_info(server: PluginServerInterface, info: Info):
    """
    Reacting to user input
    """
    pass


def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    """
    A new player joined game, welcome!
    """
    pass


def on_player_left(server: PluginServerInterface, player: str):
    """
    A player left the game, do some cleanup!
    """
    pass


def on_server_start(server: PluginServerInterface):
    """
    When the server begins to start
    """
    pass


def on_server_startup(server: PluginServerInterface):
    """
    When the server is fully startup
    """
    pass


def on_server_stop(server: PluginServerInterface, return_code: int):
    """
    When the server process is stopped, go do some clean up
    If the server is not stopped by a plugin, this is the only chance for plugins to restart the server, otherwise MCDR
    will exit too
    """
    pass


def on_mcdr_start(server: PluginServerInterface):
    """
    When MCDR just launched
    """


def on_mcdr_stop(server: PluginServerInterface):
    """
    When MCDR is about to stop, go do some clean up
    MCDR will wait until all on_mcdr_stop event call are finished before exiting
    """
    pass
