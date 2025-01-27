# Dataloop task

In this exercise, we will have two servers playing a pong game. The
servers can be coded using nodejs (express) or python (FasAPI).  During
the game, there are two instances of the same server code running, and a
pong CLI command line tool is used to start, pause, resume, and stop the
game.

The game:

The first instance (instance1) starts by sending a ping request
(endpoint "/ping") to instance2.  Once instance2 receives an HTTP ping
request, it will reply pong in the response body (with status 200).

Then instance2 (who received the ping) will wait for `pong_time_ms` and
then it will send a new HTTP ping request to the first instance.

The two servers will ping each other, where pong_time_ms milliseconds
pass between each ping.

For joint session debugging purposes, you can start the servers in any
method you wish.

The game will be controlled by a CLI tool (nodejs or python)

CLI usage:
node pong-cli.js <command: string> <param: number>

CLI commands:
node pong-cli.js start <pong_time_ms> : start the game with pong_time_ms as the interval between pongs
node pong-cli.js pause : pause the game
node pong-cli.js resume: resume the game from previous pause point. same pong_time_ms kept .
node pong-cli.js stop : stop the game. servers can stay up

example:

python pong-cli.py start 1000 : start pong game with 1 second between pongs.
