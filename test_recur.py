#!/usr/bin/env python

import time
import pytest
import tempfile
import shutil

import recur


class TestRecur:
    @pytest.fixture
    def todo_dir(self):
        todo_dir = tempfile.mkdtemp()
        yield recur.set_dirs(todo_dir)
        shutil.rmtree(todo_dir)

    @pytest.fixture
    def todo_file(self, todo_dir):
        content = '\n'.join(
            [
                '- [ ] backup filesystem t:2021-11-29',
                '- [ ] pay rent check every month on the 29th t:2021-11-29',
                '- [ ] :email: birthday card every year to someone t:2021-11-29',
                '- [x] plan summer vacation t:2024-06-01',
                '',
            ]
        )
        with open(recur.TODO_FILE, 'w+') as fh:
            fh.write(content)

        return content

    @pytest.fixture
    def recur_config_file(self, todo_dir):
        config = '\n'.join(
            [
                '{Mon Wed Fri} backup filesystem',
                '{29} pay rent check every month on the 29th',
                '{Nov 29} :email: birthday card every year to someone',
                '{Jun 01} plan summer vacation',
                '',
            ]
        )
        with open(recur.RECUR_FILE, 'w+') as fh:
            fh.write(config)

    def test_single_day(self):
        day = time.strptime('2022 01 01', '%Y %m %d')

        is_rem, is_today = recur.single_day('01', day)
        assert is_rem
        assert is_today

        is_rem, is_today = recur.single_day('02', day)
        assert is_rem
        assert not is_today

        is_rem, is_today = recur.single_day('x', day)
        assert not is_rem
        assert not is_today

    def test_has_warning(self):
        num_warning_days, day = recur.has_warning('Mar 01 +5')
        assert num_warning_days.isdigit()
        assert day == 'Mar 01'

        num_warning_days, day = recur.has_warning('Mar 01 +x')
        assert not num_warning_days

    def test_has_repeat(self):
        num_days, day = recur.has_repeat('Nov 27 *5')
        assert num_days.isdigit()
        assert num_days == '5'
        assert day == 'Nov 27'

    def test_single_do_w(self):
        # Today is a Monday
        day = time.strptime('2024 01 15', '%Y %m %d')

        is_rem, is_today = recur.single_do_w('Mon', day)
        assert is_rem
        assert is_today

        is_rem, is_today = recur.single_do_w('Tue', day)
        assert is_rem
        assert not is_today

        is_rem, is_today = recur.single_do_w('x', day)
        assert not is_rem
        assert not is_today

    def test_multi_do_w(self):
        # Today is a Monday
        day = time.strptime('2024 01 15', '%Y %m %d')

        is_rem, is_today = recur.multi_do_w('Mon Wed Fri', day)
        assert is_rem
        assert is_today

        is_rem, is_today = recur.multi_do_w('Tue Thu Sat', day)
        assert is_rem
        assert not is_today

        # If 'Mon' is first string that matches, it returns True, True
        # even if 'Invalid' follows. This test reflects that behavior.
        is_rem, is_today = recur.multi_do_w('Mon Invalid', day)
        assert is_rem
        assert is_today

    def test_multi_day(self):
        # Today is the 15th
        day = time.strptime('2024 01 15', '%Y %m %d')
        is_rem, is_today = recur.multi_day('1 15 30', day)
        assert is_rem
        assert is_today
        is_rem, is_today = recur.multi_day('2 16 25', day)
        assert is_rem
        assert not is_today

        # Same like for test_multi_do_w: If '15' is first and matches, it returns True, True.
        is_rem, is_today = recur.multi_day('15 x', day)
        assert is_rem
        assert is_today

    def test_parse_rem(self):
        day = time.strptime('2022 01 15', '%Y %m %d')

        assert recur.parse_rem('15', day)
        assert recur.parse_rem('Sat', day)
        assert recur.parse_rem('Jan 15 2022', day)
        assert recur.parse_rem('31 22 11 15 33', day)

        # Test cases for single_do_w via parse_rem
        day_mon = time.strptime('2024 01 15', '%Y %m %d')  # Monday
        assert recur.parse_rem('Mon', day_mon)
        assert not recur.parse_rem('Tue', day_mon)

        # Test cases for multi_do_w via parse_rem
        assert recur.parse_rem('Mon Wed Fri', day_mon)
        assert not recur.parse_rem('Tue Thu Sat', day_mon)
        # Test specific behavior where a valid match causes early return
        assert recur.parse_rem('Mon Invalid', day_mon)
        # Test cases for multi_day via parse_rem
        day_15 = time.strptime('2024 01 15', '%Y %m %d')  # 15th day
        assert recur.parse_rem('1 15 30', day_15)
        assert not recur.parse_rem('2 16 25', day_15)
        # Test specific behavior where a valid match causes early return
        assert recur.parse_rem('15 x', day_15)
        # Test cases for month_day with warning via parse_rem
        day_jan_20 = time.strptime('2024 01 20', '%Y %m %d')
        assert recur.parse_rem(
            'Jan 24 +5', day_jan_20
        )  # Event Jan 24, today Jan 20 (4 days before), +5 makes it true
        assert not recur.parse_rem(
            'Jan 26 +5', day_jan_20
        )  # Event Jan 26, today Jan 20 (6 days before), +5 makes it false

        # Test cases for month_day with repeat via parse_rem
        day_jan_15 = time.strptime('2024 01 15', '%Y %m %d')
        assert recur.parse_rem(
            'Jan 11 *5', day_jan_15
        )  # Event Jan 11, today Jan 15 (4 days after), *5 makes it true
        assert not recur.parse_rem(
            'Jan 10 *5', day_jan_15
        )  # Event Jan 10, today Jan 15 (5 days after), *5 makes it false

        # Test cases for month_day_year with warning via parse_rem
        day_dec_30 = time.strptime('2023 12 30', '%Y %m %d')
        assert recur.parse_rem(
            'Jan 01 2024 +3', day_dec_30
        )  # Event Jan 1 2024, today Dec 30 2023 (2 days before), +3 makes it true
        assert not recur.parse_rem(
            'Jan 01 2024 +1', day_dec_30
        )  # Event Jan 1 2024, today Dec 30 2023 (2 days before), +1 makes it false

        # Test cases for month_day_year with repeat via parse_rem
        day_jan_02 = time.strptime('2025 01 02', '%Y %m %d')
        assert recur.parse_rem(
            'Dec 31 2024 *3', day_jan_02
        )  # Event Dec 31 2024, today Jan 2 2025 (2 days after), *3 makes it true
        assert not recur.parse_rem(
            'Dec 30 2024 *3', day_jan_02
        )  # Event Dec 30 2024, today Jan 2 2025 (3 days after), *3 makes it false

        # Invalid format
        assert not recur.parse_rem('invalid format', day)

    def test_get_dict(self, recur_config_file):
        assert recur.get_dict(recur.RECUR_FILE) == {
            '{Mon Wed Fri}': ['backup filesystem'],
            '{29}': ['pay rent check every month on the 29th'],
            '{Nov 29}': [':email: birthday card every year to someone'],
            '{Jun 01}': ['plan summer vacation'],
        }

    def test_task_exists(self, todo_file):
        assert not recur.task_exists('backup filesystem', '2022-01-01')
        assert recur.task_exists('backup filesystem', '2021-11-29')
        assert recur.task_exists('plan summer vacation', '2024-06-01')

    def test_add_task(self, todo_file):
        recur.add_task('take out the trash', '2022-01-01')
        with open(recur.TODO_FILE) as fh:
            assert fh.read() == '- [ ] take out the trash t:2022-01-01\n' + todo_file

    def test_get_tasks(self, todo_file):
        assert recur.get_tasks('Mon') == []
        assert recur.get_tasks('2021-11-29') == [
            'backup filesystem',
            'pay rent check every month on the 29th',
            ':email: birthday card every year to someone',
        ]

    def test_add_today_tasks(self, todo_file):
        now = time.localtime()
        task = time.strftime('{%b %d} pick up milk\n', now)
        with open(recur.RECUR_FILE, 'w+') as fh:
            fh.write(task)

        recur.add_today_tasks(recur.RECUR_FILE)

        with open(recur.TODO_FILE) as fh:
            todos = fh.readlines()

        assert todos[0] == time.strftime('- [ ] pick up milk t:%F\n', now)

    def test_month_day(self):
        # Test cases for month_day function
        today = time.strptime('2024 01 15', '%Y %m %d')
        assert recur.month_day('Jan 15', today) == (True, True)
        assert recur.month_day('Jan 16', today) == (True, False)
        assert recur.month_day('Feb 29', today) == (
            True,
            False,
        )  # Non-leap year
        today = time.strptime('2024 02 29', '%Y %m %d')
        assert recur.month_day('Feb 29', today) == (
            True,
            True,
        )  # Leap year
        assert recur.month_day('invalid date', today) == (
            False,
            False,
        )

        # Test repeat feature
        today = time.strptime('2024 01 15', '%Y %m %d')
        assert recur.month_day('Jan 10', today, rep=5) == (
            True,
            False,
        )
        assert recur.month_day('Jan 11', today, rep=5) == (True, True)

        # Test warning feature
        today = time.strptime('2024 01 20', '%Y %m %d')
        assert recur.month_day('Jan 24', today, warn=5) == (
            True,
            True,
        )
        assert recur.month_day('Jan 25', today, warn=5) == (
            True,
            False,
        )

        # Edge case: Event is Jan 1, today is Dec 31 of previous year, warn=3
        today = time.strptime('2023 12 31', '%Y %m %d')
        assert recur.month_day('Jan 01', today, warn=3) == (
            True,
            True,
        )

        # Edge case: Event is Dec 31, today is Jan 1 of next year, repeat=3
        today = time.strptime('2025 01 01', '%Y %m %d')
        assert recur.month_day('Dec 31', today, rep=3) == (True, True)

        # Edge case: Event is Dec 28, today is Jan 1 of next year, repeat=3
        today = time.strptime('2025 01 01', '%Y %m %d')
        assert recur.month_day('Dec 28', today, rep=3) == (
            True,
            False,
        )

    def test_month_day_year(self):
        # Test cases for month_day_year function
        today = time.strptime('2024 01 15', '%Y %m %d')
        assert recur.month_day_year('Jan 15 2024', today) == (
            True,
            True,
        )
        assert recur.month_day_year('Jan 16 2024', today) == (
            True,
            False,
        )
        assert recur.month_day_year('Feb 29 2024', today) == (
            True,
            False,
        )
        assert recur.month_day_year('invalid date', today) == (
            False,
            False,
        )

        # Test repeat feature
        today = time.strptime('2024 01 15', '%Y %m %d')
        assert recur.month_day_year('Jan 10 2024', today, rep=5) == (
            True,
            False,
        )
        assert recur.month_day_year('Jan 11 2024', today, rep=5) == (
            True,
            True,
        )

        # Test warning feature
        today = time.strptime('2024 01 20', '%Y %m %d')
        assert recur.month_day_year('Jan 24 2024', today, warn=5) == (
            True,
            True,
        )
        assert recur.month_day_year('Jan 25 2024', today, warn=5) == (
            True,
            False,
        )

        # Edge case: Event is Jan 1, today is Dec 31 of previous year, warn=3
        today = time.strptime('2023 12 31', '%Y %m %d')
        assert recur.month_day_year('Jan 01 2024', today, warn=3) == (
            True,
            True,
        )

        # Edge case: Event is Dec 31, today is Jan 1 of next year, repeat=3
        today = time.strptime('2025 01 01', '%Y %m %d')
        assert recur.month_day_year('Dec 31 2024', today, rep=3) == (
            True,
            True,
        )

        # Edge case: Event is Dec 28, today is Jan 1 of next year, repeat=3
        today = time.strptime('2025 01 01', '%Y %m %d')
        assert recur.month_day_year('Dec 28 2024', today, rep=3) == (
            True,
            False,
        )
