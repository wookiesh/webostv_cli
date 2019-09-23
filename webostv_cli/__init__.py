# import fire
# import click
import fire
import sys
import pynput
import json
import os
from pynput.keyboard import Key, Listener as KListener
from pynput.mouse import Listener as MListener
from wakeonlan import send_magic_packet
from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    ApplicationControl, MediaControl, InputControl, SourceControl, SystemControl, TvControl)


class S(object):
    " Store class to delay instantiation "
    config = None

    def __init__(self):
        self.ws = WebOSClient(S.config.get('host'))
        self.ws.connect()
        assert(2 in self.ws.register(S.config)), "Not registered to TV yet"
        self.ac = ApplicationControl(self.ws)
        self.ic = InputControl(self.ws)
        self.mc = MediaControl(self.ws)
        self.sc = SystemControl(self.ws)
        self.srcc = SourceControl(self.ws)
        self.tv = TvControl(self.ws)


class Cli(object):
    """ Communicate with a LG WebOS Tv (2012+) """

    def __init__(self, configFile="~/.config/lgtv"):
        if os.path.exists(os.path.expanduser(configFile)):
            with open(os.path.expanduser(configFile), 'r') as fp:
                S.config = json.load(fp)
        else:
            print('Register first ...')
            exit()

    def register(self):
        """ Request pairing with the TV """
        for status in S().ws.register(S.config):
            print (S.config)
            if status == WebOSClient.PROMPTED:
                print("Please accept the connect on the TV!")
            elif status == WebOSClient.REGISTERED:
                print("Registration successful!")

# TODO: automatically fill config file with discoverd ip and macs, and register them maybe ?

    def discover(self):
        """ Discover existing smart TV on the LAN and create config file """
        try: 
            while True:
                print(".", end="")
                a=WebOSClient.discover()            
                if a:
                    for res in a:
                        print(f"\n{res.host} found")
                    break
        except KeyboardInterrupt:
            print("\nLong enough..")
        
        

    def on(self, broadcast='192.168.1.255'):
        """ Wake on lan """
        send_magic_packet(S.config.get('mac'), ip_address=broadcast)

    def off(self):
        """ Go back to sleep """
        S().sc.power_off()

    def info(self):
        """ Surely important stuff """

        print(json.dumps(S().sc.info(), indent=4))

    def notify(self, message):
        """ Toast it on the screen """
        S().sc.notify(message)

    def app(self, cmd, appName=None):
        """ list, set, get or close """
        if cmd == 'list':
            print(json.dumps([x.data.get('title')
                              for x in S().ac.list_apps()], indent=4))
        elif cmd == 'set':
            app = list(filter(lambda x: appName in x.data['title'].lower(),
                              S().ac.list_apps()))
            if app:
                S().ac.launch(app[0])
            else:
                print(f"App <{appName}> not found")

        elif cmd == 'get':
            print(S().ac.get_current())
        elif cmd == 'close':
            S().ac.close(app)
        else:
            print("Wrong command !")

    def vol(self, value=None):
        """ no value: => display tv level, int => set value, +/- or up/down => increase/decrease """
        if value == None:
            print(json.dumps(S().mc.get_volume(), indent=4))
        elif value in ('+', 'up'):
            S().mc.volume_up()
        elif value in ('-', 'down'):
            S().mc.volume_down()
        else:
            try: 
                int(value)
                S().mc.set_volume(value)
            except:
                print("Wrong value !")

    def mute(self):
        """ Toggle mute """
        s = S()
        s.mc.mute(False) if s.mc.get_volume()['muted'] else s.mc.mute(True)

    def src(self, cmd, source=None):
        """ list or set """
        if cmd == 'list':
            print(S().srcc.list_sources())
        elif cmd == 'set':
            S().srcc.set_source(source)

    def key(self, key):
        """ Send key to TV """
        if key == 'enter':
            S().ic.enter()
        elif key in InputControl.INPUT_COMMANDS:
            s = S()
            s.ic.connect_input()
            getattr(s.ic, key)()
            s.ic.disconnect_input()

    def listen(self):
        " Listen and send keys and mouse event until CTRL LEFT is pressed "
        print('Press on CTRL LEFT to stop listening')
        s = S()
        s.ic.connect_input()

        keymap = {
            'esc': s.ic.exit,
            'enter': s.ic.click,
            'backspace': s.ic.back,
            '=': s.ic.volume_up,
            '-': s.ic.volume_down,
            'i': s.ic.info,
            'h': s.ic.home,
            'm': self.mute
        }

        def on_press(key):
            print(key)
            if key == pynput.keyboard.Key.ctrl_l:
                return False

            if hasattr(key, 'name'):
                if key.name in keymap:
                    keymap.get(key.name)()
                elif key.name in InputControl.INPUT_COMMANDS:
                    getattr(s.ic, key.name)()
            elif hasattr(key, 'char'):
                if key.char in keymap:
                    keymap.get(key.char)()
                elif key.char in InputControl.INPUT_COMMANDS:
                    getattr(s.ic, key.char)()

        def on_move(x, y):
            s.ic.move(x,y)
            print('Pointer moved to {0}'.format((x, y)))

        def on_click(x, y, button, pressed):
            s.ic.click()
            
        def on_scroll(x, y, dx, dy):
            print('Scrolled {0} at {1}'.format(
                'down' if dy < 0 else 'up',
                (x, y)))

        # Collect events until released
        m = MListener(on_move=on_move,
                      on_click=on_click, on_scroll=on_scroll)
        m.start()
        with KListener(on_press=on_press) as listener:
            listener.join()
        m.stop()
        s.ic.disconnect_input()


def main():
    fire.Fire(Cli)


if __name__ == "__main__":
    main()
