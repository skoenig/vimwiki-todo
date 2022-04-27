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

        content = "\n".join(
            [
                "- [ ] backup filesystem t:2021-11-29",
                "- [ ] pay rent check every month on the 29th t:2021-11-29",
                "- [ ] :email: birthday card every year to someone t:2021-11-29",
                "",
            ]
        )
        with open(recur.TODO_FILE, "w+") as fh:
            fh.write(content)

        return content

    @pytest.fixture
    def recur_config_file(self, todo_dir):

        config = "\n".join(
            [
                "{Mon Wed Fri} backup filesystem",
                "{29} pay rent check every month on the 29th",
                "{Nov 29} :email: birthday card every year to someone",
                "",
            ]
        )
        with open(recur.RECUR_FILE, "w+") as fh:
            fh.write(config)

    def test_single_day(self):
        day = time.strptime("2022 01 01", "%Y %m %d")

        is_rem, is_today = recur.single_day("01", day)
        assert is_rem
        assert is_today

        is_rem, is_today = recur.single_day("02", day)
        assert is_rem
        assert not is_today

        is_rem, is_today = recur.single_day("x", day)
        assert not is_rem
        assert not is_today

    def test_has_warning(self):
        num_warning_days, day = recur.has_warning("Mar 01 +5", True)
        assert num_warning_days.isdigit()
        assert day == "Mar 01"

        num_warning_days, day = recur.has_warning("Mar 01 +x", True)
        assert not num_warning_days

    def test_has_repeat(self):
        num_days, day = recur.has_repeat("Nov 27 *5", True)
        assert num_days.isdigit()
        assert num_days == "5"
        assert day == "Nov 27"

    def test_parse_rem(self):
        day = time.strptime("2022 01 15", "%Y %m %d")

        assert recur.parse_rem("15", day)
        assert recur.parse_rem("Sat", day)
        assert recur.parse_rem("Jan 15 2022", day)
        assert recur.parse_rem("31 22 11 15 33", day)

    def test_get_dict(self, recur_config_file):
        assert recur.get_dict(recur.RECUR_FILE) == {
            "{Mon Wed Fri}": ["backup filesystem"],
            "{29}": ["pay rent check every month on the 29th"],
            "{Nov 29}": [":email: birthday card every year to someone"],
        }

    def test_task_exists(self, todo_file):
        assert not recur.task_exists("backup filesystem", "2022-01-01")
        assert recur.task_exists("backup filesystem", "2021-11-29")

    def test_add_task(self, todo_file):
        recur.add_task("take out the trash", "2022-01-01")
        with open(recur.TODO_FILE) as fh:
            assert fh.read() == "- [ ] take out the trash t:2022-01-01\n" + todo_file

    def test_get_tasks(self, todo_file):
        assert recur.get_tasks("Mon") == []
        assert recur.get_tasks("2021-11-29") == [
            "backup filesystem",
            "pay rent check every month on the 29th",
            ":email: birthday card every year to someone",
        ]

    def test_add_today_tasks(self, todo_file):
        now = time.localtime()
        task = time.strftime("{%b %d} pick up milk\n", now)
        with open(recur.RECUR_FILE, "w+") as fh:
            fh.write(task)

        recur.add_today_tasks(recur.RECUR_FILE)

        with open(recur.TODO_FILE) as fh:
            todos = fh.readlines()

        assert todos[0] == time.strftime("- [ ] pick up milk t:%F\n", now)
