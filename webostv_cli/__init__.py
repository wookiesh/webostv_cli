import fire
import json
import os
from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    ApplicationControl, MediaControl, InputControl, SourceControl, SystemControl, TvControl)


class LG(object):
    """ Control a LG tv from CLI """

    def __init__(self, config='~/.lgtv'):
        """ Set config path """

        if os.path.exists(os.path.expanduser(config)):
            with open(os.path.expanduser(config), 'r') as fp:
                self.config = json.load(fp)

            self.client = WebOSClient(self.config['host'])
            self.client.connect()
            assert(2 in self.client.register(self.config)
                   ), "Not registered to TV yet"
        else:
            print('Got to register first')
            self.config = {}

    def register(self, host, configFile='~/.lgtv'):
        """ Start with this to get the pairing ok (key, host, mac) """

        # client = WebOSClient.discover()
        try:
            client = WebOSClient(host)
            client.connect()
            for status in client.register(self.config):
                if status == WebOSClient.PROMPTED:
                    print("Please accept the connect on the TV!")
                elif status == WebOSClient.REGISTERED:
                    print("Registration successful!")

                    self.config['host'] = host
                    self.config['mac'] = SystemControl(self.client).info().get('device_id', '')
                    with open(os.path.expanduser(configFile), 'w+') as fp:
                        json.dump(self.config, fp)
                    print(json.dumps(self.config, indent=4))

        except Exception as e:
            print(f"Something went wrong: {e}")

    def mute(self):
        """ No more sound"""

        MediaControl(self.client).mute(True)

    def unmute(self):
        """ The sound is back"""

        MediaControl(self.client).mute(False)

    def info(self):
        """ Get Software info """

        print(json.dumps(SystemControl(self.client).info(), indent=2))

    def notify(self, message):
        """ Toast on the screen """

        SystemControl(self.client).notify(message)

    def up(self):
        """ Send up """

        a = ApplicationControl(self.client)
        a.list_apps()


def main():
    fire.Fire(LG)


if __name__ == "__main__":
    import sys
    sys.argv.append('info')
    main()
