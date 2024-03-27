# vimwiki-todo

A command line tool based on and inspired by Gina Trapani's [todo.txt](http://todotxt.org/), reduced to only the essential commands and modified to work with [VimWiki](https://vimwiki.github.io/) todo lists in markdown mode.

## Why yet another todo list manager?
Todo list managers are a dime a dozen, so why another one? It's simple: I've tried many (great for procrastinating) and haven't found another one that has the exact features I wanted. So I wrote my own.

This tool is based on [todo.txt](http://todotxt.org/) simplifying some concepts for enhanced usability and task management:

- **Task prioritization**: is intuitively managed by rearranging tasks within the list — placing a task higher signals its importance.
- **Contexts**: For grouping tasks with contexts, [VimWiki tags](https://github.com/vimwiki/vimwiki/blob/69318e74c88ef7677e2496fd0a836446ceac61e8/doc/vimwiki.txt#L1575) are utilized, offering a robust tagging system.
- **Date and Context Filters**: Tasks can be filtered based on their due dates or associated contexts, making it easier to navigate and prioritize tasks.
- **Archive Functionality**: Provides a method to archive completed tasks, keeping the main task list clean and focused.
- **Recurring Tasks**: Inspired by [Graham Davies' todo.txt cron helper](https://github.com/abztrakt/ya-todo-py/blob/master/todo_cron.py), allowing for the creation and management of tasks that occur on a regular basis.

## Syntax
VimWiki todo lists have the following format:

```
- [X] implement 'archive' command :coding:
- [ ] add some more info to the README
    - [ ] add an intro
    - [ ] add some quick examples
- [ ] commit and push t:2022-05-01
```

In this example, the first task is completed, and is decorated with the context 'coding'. The second task has two sub-tasks and the third tasks has a due date set with 't:2022-05-01'.

## Usage
Here are some quick examples how to use `todo`:

- Add a task: `todo add take the car to the workshop`
- List all tasks: `todo ls`
- List tasks which contain the term 'car': `todo ls car`
- List tasks grouped by context: `todo context` (you can also filter by term)
- List tasks whose due date has past: `todo past`
- List tasks that are due tomorrow: `todo tomorrow`
- Edit the todo list with your default editor: `todo edit`
- Move all checked off tasks to the archive file: `todo archive`

Have a look at all available commands with `todo help`.

## Installation
Run `make install` to install `todo` into `TODO_DIR` (defaults to `~/vimwiki`).

## Recurring Tasks Helper
To automate the creation of recurring tasks, you can use the helper script `recur.py` as a daily cron job. This is best suited for people whose workstation runs at the same time every day anyway. For everyone else, [anacron](https://linux.die.net/man/8/anacron) might be the solution.

Run `make install-recur` to copy the script into `TODO_DIR` and create a configuration file `recur.txt` in the same directory.
The configuration syntax follows a format inspired by [remind](https://linux.die.net/man/1/remind):

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
