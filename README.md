This is a subset of [todo.txt](http://todotxt.org/) modified to work together with [vimwiki](https://vimwiki.github.io/) task lists in markdown mode and some features like recurring tasks and future / past views.

## Installation
Run `make install` to install `todo` into `TODO_DIR` (defaults to `~/vimwiki`).

`todo` is your command line tool to interact with a file named `todo.md`, have a look at it's commands with `todo help`.

To automate the creation of recurring tasks, you will need to setup `recur.py` as a daily cron job. This is best suited for people who work with their workstation every day anyhow. For everyone else, [anacron](https://linux.die.net/man/8/anacron) might be the solution.

Run `make install-recur` to copy the script into `TODO_DIR` and create a `recur.txt` file in the same directory.
Content of the `recur.txt` follows a format based on that used by remind:
```
{Wed} Take out trash
{Mon Wed Fri} backup filesystem
{29} pay rent check every month on the 29th
{1 15} do on 1st and 15th day of the month
{Nov 29} :email: birthday card every year to someone
{Nov 22 2007} Eat turkey
{Nov 27 *5} Keep adding task for 5 days after event
{Dec 01 +3} Add task 5 days before specified date
```

## Tests
```
make test
```

## License

[GNU General Public License v3.0](LICENSE)
