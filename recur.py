#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import logging
import argparse

TODO_DIR = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(format="%(asctime)-15s %(levelname)s %(module)s: %(message)s")
log = logging.getLogger(__name__)

TASK_RE = re.compile(
    r"- \[.]\s*(?P<priority>([A-Z]))? (?P<task_head>.* )t:(?P<date>[^ ]*)(?P<task_tail>.*)"
)
DESCRIPTION = """
Adds tasks from recur.txt that match today's date to todo file

Date format based on that used by remind:

{Wed} Take out trash
{Mon Wed Fri} backup filesystem
{29} pay rent check every month on the 29th
{1 15} do on 1st and 15th day of the month
{Nov 29} :email: birthday card every year to someone
{Nov 22 2007} Eat turkey
{Nov 27 *5} Keep adding task for 5 days after event
{Dec 01 +3} Add task 5 days before specified date
"""


def set_dirs(todo_dir):
    global RECUR_FILE, TODO_FILE

    RECUR_FILE = todo_dir + os.path.sep + "recur.txt"
    TODO_FILE = todo_dir + os.path.sep + "todo.md"
    log.info("using file for recurring records: %s" % RECUR_FILE)
    return True


def single_day(rem, today):
    """Single Day - recur every month on this date eg. {22}"""

    if rem.isdigit():
        event = time.strptime(rem, "%d")
        if event.tm_mday == today.tm_mday:
            log.debug('parsed %s as "single_day"' % rem)
            return True, True
        else:
            return True, False
    else:
        return False, False


def single_do_w(rem, today):
    """Single DayOfWeek - recur if day matches eg. {Mon}"""

    try:
        event = time.strptime(rem, "%a")
        log.debug(event)
        if event.tm_wday == today.tm_wday:
            log.debug('parsed %s as "single_do_w"' % rem)
            return True, True
        else:
            return True, False
    except ValueError:
        return False, False


def month_day(rem, today, warn=False, rep=False):
    """Month Day - add on this day every year eg. {Nov 22}"""

    try:
        event = time.strptime(rem, "%b %d")
        # new code to handle warnings 2007/07/22
        if warn:
            for i in range(1, warn):
                if event.tm_mon == today.tm_mon and event.tm_mday - i == today.tm_mday:
                    log.debug('parsed %s as "month_day"' % rem)
                    return True, True
        # new code to handle repeats 2007/07/22
        if rep:
            for i in range(1, rep):
                if event.tm_mon == today.tm_mon and event.tm_mday + i == today.tm_mday:
                    log.debug('parsed %s as "single_do_w" with repeats' % rem)
                    return True, True
        # end new code
        if event.tm_mon == today.tm_mon and event.tm_mday == today.tm_mday:
            return True, True
        else:
            return True, False
    except ValueError:
        return False, False


def month_day_year(rem, today, warn=False, rep=False):
    """Month Day Year - single event that doesn't recur eg. {Nov 22 2007}"""

    try:
        event = time.strptime(rem, "%b %d %Y")
        if (
            event.tm_year == today.tm_year
            and event.tm_mon == today.tm_mon
            and event.tm_mday == today.tm_mday
        ):
            log.debug('parsed %s as "month_day_year"' % rem)
            return True, True
        else:
            return True, False
    except ValueError:
        return False, False


def has_warning(rem, today):
    """Month Day Warning - add Warning days before the date eg. {Nov 22 +5}"""

    re_rem = re.compile(r" \+(\d+)$")
    match = re.search(re_rem, rem)
    if match:
        rem = re.sub(re_rem, "", rem)
        return match.group(1), rem
    else:
        return False, False


def has_repeat(rem, today):
    """Month Day Repeat - add for Repeat days after the date eg. {Nov 22 *5}"""

    re_rem = re.compile(r" \*(\d+)$")
    match = re.search(re_rem, rem)
    if match:
        rem = re.sub(re_rem, "", rem)
        return match.group(1), rem
    else:
        return False, False


def multi_do_w(rem, today):
    """Multiple DayOfWeek - recur each day that matches
    eg. {Mon Wed} or {Mon Tue Wed} or {Mon Tue Wed Thu Fri}"""

    words = rem.split()
    for day in words:
        type, now = single_do_w(day, today)
        if not type:
            # If one fails - they all fail
            return False, False
        if now:
            log.debug('parsed %s as "multi_do_w"' % rem)
            return True, True
    return True, False


def multi_day(rem, today):
    """Multiple Days - recur each day that matches eg. {1 14 28}"""

    words = rem.split()
    for day in words:
        type, now = single_day(day, today)
        if not type:
            # If one fails - they all fail
            return False, False
        if now:
            log.debug('parsed %s as "multi_day"' % rem)
            return True, True
    return True, False


def parse_rem(rem, today):
    """parses REM style date strings - returns True if event is today"""

    # 1st DayOfWeek after date
    # {Mon 15}

    # xth DayOfWeek after date
    # {Mon 15}

    # OMIT

    # ### Sub day --- no support planned
    # Times -- AT 5:00PM
    # {AT 5:00PM}

    log.debug('try to parse "%s"' % rem)

    warnDays, newrem = has_warning(rem, today)
    if warnDays:
        warnDays = int(warnDays)
        rem = newrem

    repeatDays, newrem = has_repeat(rem, today)
    if repeatDays:
        repeatDays = int(repeatDays)
        rem = newrem

    type, now = single_day(rem, today)
    if type and now:
        return True
    if type and not now:
        return False

    type, now = multi_day(rem, today)
    if type and now:
        return True
    if type and not now:
        return False

    type, now = single_do_w(rem, today)
    if type and now:
        return True
    if type and not now:
        return False

    type, now = multi_do_w(rem, today)
    if type and now:
        return True
    if type and not now:
        return False

    type, now = month_day(rem, today, warn=warnDays, rep=repeatDays)
    if type and now:
        return True
    if type and not now:
        return False

    type, now = month_day_year(rem, today, warn=warnDays, rep=repeatDays)
    if type and now:
        return True
    if type and not now:
        return False


def add_today_tasks(config_file):
    """Add tasks occuring today from the config file to the todo list"""

    today = time.localtime()
    today_date = time.strftime("%F", time.localtime())
    rem = get_dict(config_file)
    for k, v in list(rem.items()):
        log.info("processing item [%s] = %s" % (k, v))
        re_date = re.compile(r"{([^}]+)}")
        date = re.search(re_date, k)
        if date:
            isToday = parse_rem(
                date.group(1), today
            )  # date.group(1) = date in Remind format: Wed, 18 +3, Jan 26 +4
            if isToday:
                for task in v:
                    if task_exists(task, today_date):
                        log.info("task exists: %s" % task)
                        continue
                    log.info("adding task %s" % task)
                    add_task(task, today_date)
        else:
            log.info('unable to parse date from "%s %s"' % (k, v))


def task_exists(rem, date):
    """Check for existing task for a date in the TODO file"""

    tasks = get_tasks(date)
    log.debug("tasks found for %s: %s" % (date, tasks))
    log.debug("rem: %s" % rem)
    if rem in tasks:
        return True
    else:
        return False


def get_dict(config_file):
    config = {}
    if not os.path.isfile(config_file):
        log.error("config file {} does not exist".format(config_file))
        sys.exit(1)

    with open(config_file) as fd:
        for line in fd.readlines():
            pos = line.rfind("}")
            if pos == -1:
                log.error('unable to parse line "%s"' % line)
                continue
            date = line[: pos + 1].strip()
            task = line[pos + 1 :].strip()
            if date in list(config.keys()):
                config[date].append(task)
            else:
                config[date] = [task]
    return config


def add_task(task, date):
    with open(TODO_FILE, "r+") as fd:
        content = fd.read()
        fd.seek(0)
        fd.write("- [ ] %s t:%s\n%s" % (task, date, content))


def get_tasks(date):
    """get tasks from todo file for date"""

    tasks = []
    with open(TODO_FILE) as fd:
        for line in fd.read().splitlines():
            match = re.search(TASK_RE, line)
            if not match:
                continue
            match_dict = match.groupdict()
            if match_dict["date"] == date:
                # add task with and w/h priority tag to get also tasks where priority was added later
                task = "%s%s" % (match_dict["task_head"], match_dict["task_tail"])
                tasks.append(" ".join(task.split()))
                if match_dict["priority"]:
                    task = "%s %s" % (match_dict["priority"], task)
                    tasks.append(" ".join(task.split()))

    return tasks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-v", "--verbose", help="increase verbosity", action="count", default=0
    )
    parser.add_argument("-d", "--todo_dir", help="Specify TODO_DIR from command line")
    args = parser.parse_args()

    loglevel = logging.WARN
    if args.verbose == 1:
        loglevel = logging.INFO
    if args.verbose >= 2:
        loglevel = logging.DEBUG
    log.setLevel(loglevel)

    if args.todo_dir:
        TODO_DIR = args.todo_dir

    set_dirs(TODO_DIR)

    add_today_tasks(RECUR_FILE)
