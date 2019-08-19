# import fire
# import click
import fire
import sys
import pynput
import json
import os
from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    ApplicationControl, MediaControl, InputControl, SourceControl, SystemControl, TvControl)


class Cli(object):
    """ Communicate with a LG WebOS Tv (2012+) """

    def __init__(self, configFile="~/.lgtv"):
        if os.path.exists(os.path.expanduser(configFile)):
            with open(os.path.expanduser(configFile), 'r') as fp:
                self._config = json.load(fp)

    @property
    def _client(self):
        if not hasattr(self, '_inner_client'):
            self._inner_client = WebOSClient(self._config['host'])
            self._inner_client.connect()
            assert(2 in self._inner_client.register(
                self._config)), "Not registered to TV yet"
        return self._inner_client

    @property
    def _ac(self):
        return ApplicationControl(self._client)

    @property
    def _sc(self):
        return SystemControl(self._client)

    @property
    def _mc(self):
        return MediaControl(self._client)

    @property
    def _srcc(self):
        if not hasattr(self, '_inner_srcc'):
            self._inner_srcc = SourceControl(self._client)
        return self._inner_srcc

    @property
    def _ic(self):
        if not hasattr(self, '_inner_ic'):
            self._inner_ic = InputControl(self._client)
        return self._inner_ic

    def register(self):
        """ Request pairing with the TV """
        raise

    def info(self):
        """ Surely important stuff """

        print(json.dumps(self._sc.info(), indent=4))

    def notify(self, message):
        """ Toast it on the screen """
        self._sc.notify(message)

    def app(self, cmd, appName=None):
        """ list, set, get or close """
        if cmd == 'list':
            print(json.dumps([x.data.get('title')
                              for x in self._ac.list_apps()], indent=4))
        elif cmd == 'set':
            app = list(filter(lambda x: appName in x.data['title'].lower(),
                              self._ac.list_apps()))
            if app:
                self._ac.launch(app[0])
            else:
                print(f"App <{appName}> not found")

        elif cmd == 'get':
            print(self._ac.get_current())
        elif cmd == 'close':
            self._ac.close(app)
        else:
            # raise ValueError("Not accepted!")
            print("Wrong command !")

    # @click.argument('cmd', type=click.Choice(['up', 'down', 'get', 'set']))
    def vol(self, cmd, value=None):
        """ get, set, up or down """

        if cmd == 'get':
            print(json.dumps(self._mc.get_volume(), indent=4))
        elif cmd == 'set':
            self._mc.set_volume(value)
        elif cmd == 'up':
            self._mc.volume_up()
        elif cmd == 'down':
            self._mc.volume_down()
        else:
            print("Wrong command !")

    def mute(self):
        """ Silence """

        self._mc.mute(True)

    def unmute(self):
        """ Enjoy the sound """

        self._mc.mute(False)

    def src(self, cmd, source=None):
        """ list or set """

        if cmd == 'list':
            print(self._srcc.list_sources())
        elif cmd == 'set':
            self._srcc.set_source(source)

    def key(self, key):
        """ Send key to TV """

        if key == 'enter':
            self._ic.enter()
        elif key in InputControl.INPUT_COMMANDS:
            self._ic.connect_input()
            getattr(self._ic, key)()
            self._ic.disconnect_input()

    def keys(self):
        """ Listen and send keys until CTRL LEFT is pressed """

        print('Press on CTRL LEFT to stop listening')
        self._ic.connect_input()
        from pynput.keyboard import Key, Listener

        keymap = {
            'esc': 'exit', 
            'enter': 'click',
            'backspace': 'back',
            '=': 'volume_up',
            '-': 'volume_down',
            'i': 'info'
        }
        def on_press(key):
            if key == pynput.keyboard.Key.ctrl_l:
                return False

            if hasattr(key, 'name'):
                if key.name in keymap:
                    getattr(self._ic, keymap.get(key.name))()                
                elif key.name in InputControl.INPUT_COMMANDS:
                    getattr(self._ic, key.name)()
            elif hasattr(key, 'char'): 
                if key.char in keymap:
                    getattr(self._ic, keymap.get(key.char))()
                elif key.char in InputControl.INPUT_COMMANDS:
                    getattr(self._ic, key.char)()

            print(f'{key} pressed ({dir(key)})')

        # Collect events until released
        with Listener(on_press=on_press) as listener:
            listener.join()

        self._ic.disconnect_input()


def main():
    fire.Fire(Cli)


if __name__ == "__main__":
    main()