
## Setup
clone this repo into your vimwiki's folder, create a `recur.txt` file like this:
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

If you like, you can also symlink the todo script into your `$PATH`:

```
sudo ln -s $PWD/todo /usr/local/bin/
```

