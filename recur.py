#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import logging
import argparse
import datetime

TODO_DIR = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(format='%(asctime)-15s %(levelname)s %(module)s: %(message)s')
log = logging.getLogger(__name__)

TASK_RE = re.compile(
    r'- \[.]\s*(?P<priority>([A-Z]))? (?P<task_head>.* )t:(?P<date>[^ ]*)(?P<task_tail>.*)'
)
REMINDER_RE = re.compile(r'{([^}]+)}')
WARNING_RE = re.compile(r' \+(\d+)$')
REPEAT_RE = re.compile(r' \*(\d+)$')
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
    """Set global paths for recurrence and todo files."""
    global RECUR_FILE, TODO_FILE

    RECUR_FILE = os.path.join(todo_dir, 'recur.txt')
    TODO_FILE = os.path.join(todo_dir, 'todo.md')
    log.info(f'Using file for recurring records: {RECUR_FILE}')
    return True


def single_day(reminder_str, today):
    """Check if a single day reminder matches today's time struct. Eg. {22}"""

    if reminder_str.isdigit():
        reminder_day = int(reminder_str)
        if reminder_day == today.tm_mday:
            log.debug(f'Parsed "{reminder_str}" as "single_day"')
            return True, True
        else:
            return True, False
    else:
        return False, False


def single_weekday(reminder_str, today):
    """Check if a single day of week reminder matches today's time struct. Eg. {Mon}"""

    try:
        reminder_weekday = time.strptime(reminder_str, '%a')
        log.debug(reminder_weekday)
        if reminder_weekday.tm_wday == today.tm_wday:
            log.debug(f'Parsed "{reminder_str}" as "single_weekday"')
            return True, True
        else:
            return True, False
    except ValueError:
        return False, False


def month_day(reminder_str, today, warning_days=0, repeat_days=0):
    """Check if a month-day reminder matches today's time structs, with optional warning or repeat. Eg. {Nov 22}"""
    try:
        reminder_time = time.strptime(
            f'{reminder_str} {today.tm_year}',
            '%b %d %Y',
        )
        current_date = datetime.date(
            today.tm_year,
            today.tm_mon,
            today.tm_mday,
        )

        if warning_days:
            # Check if the event date falls within the warning period (days before)
            for i in range(1, warning_days):
                future_date = current_date + datetime.timedelta(days=i)
                event_date = datetime.date(
                    future_date.year,
                    reminder_time.tm_mon,
                    reminder_time.tm_mday,
                )
                if event_date == future_date:
                    log.debug(f'Parsed "{reminder_str}" as "month_day" with warnings')
                    return True, True

        if repeat_days:
            # Check if the event date falls within the repeat period (days after)
            for i in range(1, repeat_days):
                past_date = current_date - datetime.timedelta(days=i)
                event_date = datetime.date(
                    past_date.year,
                    reminder_time.tm_mon,
                    reminder_time.tm_mday,
                )
                if event_date == past_date:
                    log.debug(f'Parsed "{reminder_str}" as "month_day" with repeats')
                    return True, True

        # Check if the event month and day match today's month and day
        if (
            reminder_time.tm_mon == today.tm_mon
            and reminder_time.tm_mday == today.tm_mday
        ):
            return True, True
        else:
            return True, False
    except ValueError:
        return False, False


def month_day_year(reminder_str, today, warning_days=0, repeat_days=0):
    """Check if a specific month-day-year event matches today's time struct, with optional warning or repeat. Eg. {Nov 22 2007}"""

    try:
        reminder_time = time.strptime(reminder_str, '%b %d %Y')
        reminder_date = datetime.date(
            reminder_time.tm_year,
            reminder_time.tm_mon,
            reminder_time.tm_mday,
        )
        current_date = datetime.date(
            today.tm_year,
            today.tm_mon,
            today.tm_mday,
        )

        if warning_days:
            for i in range(1, warning_days):
                future_date = reminder_date - datetime.timedelta(days=i)
                if future_date == current_date:
                    log.debug(
                        f'Parsed "{reminder_str}" as "month_day_year" with warnings'
                    )
                    return True, True

        if repeat_days:
            for i in range(1, repeat_days):
                past_date = reminder_date + datetime.timedelta(days=i)
                if past_date == current_date:
                    log.debug(
                        f'Parsed "{reminder_str}" as "month_day_year" with repeats'
                    )
                    return True, True

        if reminder_date == current_date:
            log.debug(f'Parsed "{reminder_str}" as "month_day_year"')
            return True, True
        else:
            return True, False
    except ValueError:
        return False, False


def has_warning(reminder_str):
    """Extract warning days from a reminder. Eg. {Nov 22 +5}"""

    match = re.search(WARNING_RE, reminder_str)
    if match:
        remainder_reminder_str = re.sub(WARNING_RE, '', reminder_str)
        return match.group(1), remainder_reminder_str
    else:
        return False, False


def has_repeat(reminder_str):
    """Extract repeat days from a reminder. Eg. {Nov 22 *5}"""

    match = re.search(REPEAT_RE, reminder_str)
    if match:
        remainder_reminder_str = re.sub(REPEAT_RE, '', reminder_str)
        return match.group(1), remainder_reminder_str
    else:
        return False, False


def multi_weekday(reminder_str, today):
    """Check if any day of week in a multi-day reminder  matches today's time struct. Eg. {Mon Wed Fri}"""

    days = reminder_str.split()
    for day in days:
        is_parsed_ok, is_today_match = single_weekday(day, today)
        if not is_parsed_ok:
            # If any part fails to parse, the whole multi-day string is considered invalid.
            return False, False
        if is_today_match:
            log.debug(f'Parsed "{reminder_str}" as "multi_weekday"')
            return True, True
    return True, False


def multi_day(reminder_str, today):
    """Check if any day number in a multi-day reminder  matches today. Eg. {1 14 28}"""

    days = reminder_str.split()
    for day in days:
        is_parsed_ok, is_today_match = single_day(day, today)
        if not is_parsed_ok:
            # If any part fails to parse, the whole multi-day string is considered invalid.
            return False, False
        if is_today_match:
            log.debug(f'Parsed "{reminder_str}" as "multi_day"')
            return True, True
    return True, False


def parse_rem(reminder_str, today):
    """Parses REM style date strings - returns True if event is today."""

    log.debug(f'Trying to parse "{reminder_str}"')

    warning_days = 0
    repeat_days = 0

    # Extract warning days if present
    warning_days_str, processed_reminder_str = has_warning(reminder_str)
    if warning_days_str:
        warning_days = int(warning_days_str)
        reminder_str = processed_reminder_str

    # Extract repeat days if present
    repeat_days_str, processed_reminder_str = has_repeat(reminder_str)
    if repeat_days_str:
        repeat_days = int(repeat_days_str)
        reminder_str = processed_reminder_str

    # Attempt to parse the reminder string using various date formats
    is_parsed_ok, is_today_match = single_day(reminder_str, today)
    if is_parsed_ok and is_today_match:
        return True
    if is_parsed_ok and not is_today_match:
        return False

    is_parsed_ok, is_today_match = multi_day(reminder_str, today)
    if is_parsed_ok and is_today_match:
        return True
    if is_parsed_ok and not is_today_match:
        return False

    is_parsed_ok, is_today_match = single_weekday(reminder_str, today)
    if is_parsed_ok and is_today_match:
        return True
    if is_parsed_ok and not is_today_match:
        return False

    is_parsed_ok, is_today_match = multi_weekday(reminder_str, today)
    if is_parsed_ok and is_today_match:
        return True
    if is_parsed_ok and not is_today_match:
        return False

    is_parsed_ok, is_today_match = month_day(
        reminder_str, today, warning_days=warning_days, repeat_days=repeat_days
    )
    if is_parsed_ok and is_today_match:
        return True
    if is_parsed_ok and not is_today_match:
        return False

    is_parsed_ok, is_today_match = month_day_year(
        reminder_str, today, warning_days=warning_days, repeat_days=repeat_days
    )
    if is_parsed_ok and is_today_match:
        return True
    if is_parsed_ok and not is_today_match:
        return False


def add_today_tasks(config_file):
    """Add tasks occurring today from the config file to the todo list."""

    today = time.localtime()
    today_date_str = time.strftime('%F', today)
    reminders_config = get_dict(config_file)

    for date_pattern_str, tasks in reminders_config.items():
        log.info(f'Processing item [{date_pattern_str}] = {tasks}')

        matched_date_group = re.search(REMINDER_RE, date_pattern_str)
        if matched_date_group:
            # matched_date_group.group(1) is the date in Remind format (e.g., Wed, 18 +3, Jan 26 +4)
            is_match_today = parse_rem(matched_date_group.group(1), today)
            if is_match_today:
                for task in tasks:
                    if task_exists(task, today_date_str):
                        log.info(f'Task already exists: {task}')
                        continue
                    log.info(f'Adding task: {task}')
                    add_task(task, today_date_str)
        else:
            log.info(f'Unable to parse date from "{date_pattern_str} {tasks}"')


def task_exists(task, date_str):
    """Check for an existing task for a given date in the TODO file."""

    tasks = get_tasks(date_str)
    log.debug(f'Tasks found for {date_str}: {tasks}')
    log.debug(f'Checking for task: {task}')
    if task in tasks:
        return True
    else:
        return False


def get_dict(config_file):
    """Parse the recurrence config file into a dictionary."""
    recurrence_config = {}
    if not os.path.isfile(config_file):
        log.error(f'Config file {config_file} does not exist')
        sys.exit(1)

    with open(config_file) as fd:
        for line in fd.readlines():
            pos = line.rfind('}')
            if pos == -1:
                log.error(f'Unable to parse line "{line.strip()}"')
                continue
            date = line[: pos + 1].strip()
            task = line[pos + 1 :].strip()
            if date in recurrence_config:
                recurrence_config[date].append(task)
            else:
                recurrence_config[date] = [task]
    return recurrence_config


def add_task(task, date_str):
    """Add a new task to the TODO file."""
    with open(TODO_FILE, 'r+') as fd:
        content = fd.read()
        fd.seek(0)
        fd.write(f'- [ ] {task} t:{date_str}\n{content}')


def get_tasks(date_str):
    """Get tasks from todo file for a specific date."""

    tasks = []
    with open(TODO_FILE) as fd:
        for line in fd.read().splitlines():
            match = re.search(TASK_RE, line)
            if not match:
                continue
            match_dict = match.groupdict()
            if match_dict['date'] == date_str:
                # Add task with and without priority tag to also get tasks where priority was added later.
                task = ' '.join(
                    f'{match_dict["task_head"]}{match_dict["task_tail"]}'.split()
                )

                tasks.append(task)
                if match_dict['priority']:
                    tasks.append(f'{match_dict["priority"]} {task}')

    return tasks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help='increase verbosity',
        action='count',
        default=0,
    )
    parser.add_argument(
        '-d',
        '--todo_dir',
        help='Specify TODO_DIR from command line',
    )
    args = parser.parse_args()

    log_level = logging.WARN
    if args.verbose == 1:
        log_level = logging.INFO
    if args.verbose >= 2:
        log_level = logging.DEBUG
    log.setLevel(log_level)

    if args.todo_dir:
        TODO_DIR = args.todo_dir

    set_dirs(TODO_DIR)

    add_today_tasks(RECUR_FILE)
