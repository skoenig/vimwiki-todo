This is a subset of [todo.txt](http://todotxt.org/) modified to work together with [vimwiki](https://vimwiki.github.io/) task lists in markdown mode and some features like recurring tasks and future / past views.

## Setup
Clone this repo into your vimwiki folder, and symlink the `todo` script into your `$PATH`:

```
sudo ln -s $PWD/todo /usr/local/bin/
```

`todo` is your command line tool to interact with a file named `todo.md`, have a look at it's commands with `todo help`.


To automate the creation of recurring tasks, create a `recur.txt` file in the same directory like this:
```
{Wed} Take out trash
{Mon Wed Fri} backup filesystem
{29} pay rent check every month on the 29th
{1 15} do on 1st and 15th day of the month
{Nov 29} @email birthday card every year to someone
{Nov 22 2007} Eat turkey
{Nov 27 *5} Keep adding task for 5 days after event
{Dec 01 +3} Add task 5 days before specified date
```
...and setup the `recur.py` script for cron:
```
sudo ln -s $PWD/recur.py /etc/cron.daily/add_recurring_todos
```
