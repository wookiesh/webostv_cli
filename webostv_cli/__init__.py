# import fire
import click
import json
import os
from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    ApplicationControl, MediaControl, InputControl, SourceControl, SystemControl, TvControl)


# commands = set(sorted(
#     list((item for sl in(getattr(x, 'COMMANDS') for x in (
#         ApplicationControl, MediaControl, InputControl, SourceControl, SystemControl, TvControl)
#     ) for item in sl)) +
#     list(InputControl.INPUT_COMMANDS.keys())
# ))

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
    configfile = ctx.obj.get('configfile')

    # client = WebOSClient.discover()
    try:
        client = WebOSClient(host)
        client.connect()
        for status in client.register(config):
            if status == WebOSClient.PROMPTED:
                click.echo("Please accept the connect on the TV!")
            elif status == WebOSClient.REGISTERED:
                click.echo("Registration successful!")

                self.config['host'] = host
                self.config['mac'] = SystemControl(
                    client).info().get('device_id', '')
                with open(os.path.expanduser(configfile), 'w+') as fp:
                    json.dump(config, fp)
                click.echo(json.dumps(config, indent=4))

    except Exception as e:
        click.echo(f"Something went wrong: {e}")


def bind_function(name, c):
    def func(ctx, payload=None):
        client = ctx.obj.get('client')

        if c in ApplicationControl.COMMANDS.keys():
            res = getattr(ApplicationControl(client), c)(payload)
            click.echo(res)

        elif c in MediaControl.COMMANDS.keys():
            res = getattr(MediaControl(client), c)(payload)
            click.echo(json.dumps(res, indent=4))

        elif c in SystemControl.COMMANDS.keys():
            res = getattr(SystemControl(client), c)(payload)
            click.echo(json.dumps(res, indent=4))

        elif c in InputControl.COMMANDS.keys():
            res = getattr(InputControl(client), c)(payload)
            click.echo(json.dumps(res, indent=4))

        elif c in TvControl.COMMANDS.keys():
            res = getattr(TvControl(client), c)(payload)
            click.echo(json.dumps(res, indent=4))
            
        elif c in SourceControl.COMMANDS.keys():
            res = getattr(SourceControl(client), c)(payload)
            click.echo(res)

        else:
            click.echo('boh')

    func.__name__ = name
    return func


@main.command()
def key(): pass

@main.command()
@click.argument('cmd', type=click.Choice(['list', 'set']))
def src(cmd): print(cmd)

@main.command()
@click.argument('cmd', type=click.Choice(['info', 'notify', 'on', 'off']))
def sys(cmd):
    pass

@main.command()
@click.argument('cmd', type=click.Choice(['up', 'down', '+', '-']))
def tv(cmd):
    pass

@main.command()
@click.argument('cmd', type=click.Choice(['up', 'down', '+', '-', 'get', 'set']))
def vol(cmd, value=None): pass

@main.command()
@click.argument('state', type=click.Choice(['true', 'false', 'on', 'off', '1', '0']), default='true')
def mute(state):
    print(state)

@main.command()
def play(): pass

@main.command()
def pause(): pass

@main.command()
def stop(): pass

@main.command()
def rew(): pass

@main.command()
def ff(): pass


if __name__ == "__main__":
    import sys
    sys.argv.append('list_sources')
    main()