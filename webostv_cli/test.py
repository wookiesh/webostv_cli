import argparse
import json
import sys
import os
from collections import namedtuple
from wakeonlan import send_magic_packet
from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    ApplicationControl, MediaControl, InputControl, SourceControl, SystemControl, TvControl)


class Cmd():
    " NamedTuple like class to store commands "

    def __init__(self, aliases, fct, helpMsg, arg=None, argDefault=None):
        if isinstance(aliases, str):
            aliases = (aliases,)
        self.parser = S.subParsers.add_parser(
            aliases[0], aliases=aliases[1:] if len(aliases) > 1 else [], help=helpMsg)
        self.parser.set_defaults(func=fct)
        if arg:
            self.parser.add_argument(
                arg, default=argDefault, help=f'({argDefault})')


class S:
    " Storage object (don't like globals "
    base, app, sys, med, inp, tv, parsers = [None] * 7

    def init(args):
        if os.path.exists(os.path.expanduser(args.configFile)):
            with open(os.path.expanduser(args.configFile), 'r') as fp:
                S.config = json.load(fp)

            if 'host' in S.config:
                S.base = WebOSClient(S.config['host'])
                S.base.connect()
                assert(2 in S.base.register(S.config)), "Not registered yet"
                # S.app = ApplicationControl(S.base)
                # S.sys, S.tv = SystemControl(S.base), TvControl(S.base)
                # S.med, S.inp = MediaControl(S.base), InputControl(S.base)
                S.med = MediaControl(S.base)


def register(args):
    print(args)


def on(args):
    send_magic_packet(S.config.get('mac'), ip_address=args.broadcast)


def jp(fct):
    return print(json.dumps(fct()))


def main():
    parser = argparse.ArgumentParser(description="LG Web OS TV Cli (2012+)")
    parser.add_argument('-c', '--configFile', default='~/.config/lgtv')
    S.subParsers = parser.add_subparsers(help="sub-commands help")

    commands = (
        Cmd(('volume_up', 'vu'), lambda x: S.med.volume_up(), "Volume Up"),
        Cmd('vd', lambda x: S.med.volume_down(), "Volume Down"),
        Cmd('vget', lambda x: S.med.get_volume(), "Get Volume Info"),
        Cmd('vset', lambda v: S.med.set_volume(v), "Set Volume Value", 'value'),
        Cmd('info', lambda x: S.sys.info(), 'Software info'),
        Cmd('notify', lambda x: S.sys.notify(x),
            'Toast message on the screen', 'message'),
        Cmd('off', lambda x: S.sys.poweroff(), 'Go to sleep'),
        Cmd('on', lambda x: on(x), 'Wake On Lan featured',
            '--broadcast', '192.168.1.255'),
        Cmd('mute', lambda x: S.med.mute(True), 'Mute it'),
        Cmd('unmute', lambda x: S.med.mute(False), 'And the sound is back'),
        # Apps
        # Src
        # Mouse
        # key
        # keys

        Cmd('register', register,  'Register a new device', 'host'),

    )

    args = parser.parse_args()
    if hasattr(args, 'func'):
        try:
            if args.func == register:
                register(args)
            else:
                S.init(args)
                print(args.func(args) or 'Done')
        except AttributeError as E:
            parser.error(E)
    else:
        parser.print_help()


if __name__ == "__main__":
    # sys.argv.append('register')
    # sys.argv.append('ok')

    main()
