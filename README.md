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

As a side note, output of each of the two servers can be tailed from `first.log` and `second.log`, respectively:

```bash
tail -f first.log
tail -f second.log
```

# Solution

The solution is implemented in Python using FastAPI. The code is
structured as follows:

- `pong-cli.py` handles server invocation, spawning two server instances
  with separate arguments and keeping track of the server PID values in
  order to implement the commands
- `server.py` contains the FastAPI server implementation

Start and stopping the game simply spawns, respectively kills the
servers.  Pausing and resuming the game is implemented by suspending,
respectively resuming the two server processes, by sending a SIGSTOP and
SIGCONT signal to the processes.

This was done given the time constraints - an alternative implementation
might e.g. both handle the server processes in-process in Python
directly, while keeping a supervisor process running with which the CLI
would then communicate.  This would simplify the bookkeeping, as there'd
be no need keep track of PIDs and various failure states, which might
not be handled so well in the submitted solution.

The suspending and resuming of the game could also be implemented by new
endpoints on the server process, e.g. `/suspend` and `/resume`, which
would in turn suspend and resume the background task queue - due to time
constraints I wasn't sure I would be able to implement this in the given
time, though I highly suspect it would be the better solution long-term,
as it would allow us to keep various other endpoints running.

The problem here would be that the background task queue would both need
to be suspended, as well as the `time.sleep` call would ideally be
solved differently, e.g. by having tasks with a specified execution
time.  Again, this would allow for a better implementation long-term.
