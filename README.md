# vimwiki-todo

This here is a script based on and inspired by Gina Trapani's [todo.txt](http://todotxt.org/), reduced to only the essential commands and modified to work with [vimwiki](https://vimwiki.github.io/) todo lists in markdown mode.

## Why yet another todo list manager?
Todo list managers are a dime a dozen, so why another one? It's simple: I've tried many (great for procrastinating) and haven't found another one that has the exact features I wanted. So I wrote my own.

Some concepts from [todo.txt](http://todotxt.org/) such as projects are removed for simplicity, priorities can be expressed by moving tasks higher in the todo list ;), contexts have been implemented with vimwiki tags, and there is some additional functionality such as recurring tasks (based on [Graham Davies' todo.txt cron helper](https://github.com/abztrakt/ya-todo-py/blob/master/todo_cron.py)) and listing tasks based on their due date.

## Usage
Vimwiki todo list have following format:
```
- [X] implement 'archive' command
- [ ] add some more info to the README
    - [ ] add an intro
    - [ ] add some quick examples
- [ ] commit and push t:2022-05-01
```

Here are some quick examples how to use the CLI:

- Add a task: `todo add take the car to the workshop`
- List all tasks: `todo ls`
- List tasks which contain the term 'car': `todo ls car`
- List tasks grouped by context: `todo context` (you can also filter by term)
- List tasks whose due date has past: `todo past`
- List tasks that are due tomorrow: `todo tomorrow`
- Edit the todo list with your default editor: `todo edit`
- Move all checked off tasks to the archive file: `todo archive`

For all commands, use the `help` command.

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
