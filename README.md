# WebOSTv-Cli

Get easy cli access to your lg webos tv, ie:

`lg vol set 20`

This tool leverages the excellent [PyWebOSTV](https://github.com/supersaiyanmode/PyWebOSTV) library.

## Installation

This will soon be pushed to Pypi, but in the meantime:

```pip install git+https://github.com/eagleamon/webostv_cli.git```

## Usage

To start a listener for key/mouse input, use the command
`lg listen`
and then all key presses are forwarded to the tv, with the following effect:

table_map