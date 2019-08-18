# import fire
import click
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


@click.group()
@click.option('-c', '--configFile', default='~/.lgtv')
@click.pass_context
def main(ctx, configfile):
    ctx.ensure_object(dict)

    if os.path.exists(os.path.expanduser(configfile)):
        with open(os.path.expanduser(configfile), 'r') as fp:
            config = json.load(fp)

        client = WebOSClient(config['host'])
        client.connect()
        assert(2 in client.register(config)), "Not registered to TV yet"
        ctx.obj['client'] = client

    else:
        click.echo('Got to register first')
        config = {}

    ctx.obj['config'] = config
    ctx.obj['configfile'] = configfile


@main.command()
@click.argument('host')
@click.pass_context
def register(ctx, host):
    """ Start with this to get the pairing ok (key, host, mac) """

    config = ctx.obj.get('config')

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
                self.config['mac'] = SystemControl(
                    self.client).info().get('device_id', '')
                with open(os.path.expanduser(configFile), 'w+') as fp:
                    json.dump(self.config, fp)
                print(json.dumps(self.config, indent=4))

    except Exception as e:
        print(f"Something went wrong: {e}")


commands = set(sorted(
    list((item for sl in(getattr(x, 'COMMANDS') for x in (
        ApplicationControl, MediaControl, InputControl, SourceControl, SystemControl, TvControl)
    ) for item in sl)) +
    list(InputControl.INPUT_COMMANDS.keys())
))


def bind_function(name, c):
    def func(ctx):
        client = ctx.obj.get('client')

        if c in ApplicationControl.COMMANDS.keys():
            res = getattr(ApplicationControl(client), c)()
            print(res)
        elif c in MediaControl.COMMANDS.keys():
            res = getattr(MediaControl(client), c)()
            click.echo(json.dumps(res, indent=4))
        elif c in SystemControl.COMMANDS.keys():
            res = getattr(SystemControl(client), c)()
            click.echo(json.dumps(res, indent=4))
        else:
            print('boh')

        # if found create client here

    func.__name__ = name
    return func


for c in commands:
    f = click.pass_context(bind_function('_f', c))
    main.command(name=c)(f)

if __name__ == "__main__":
    import sys
    sys.argv.append('info')
    main()
