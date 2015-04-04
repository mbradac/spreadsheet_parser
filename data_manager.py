import csv
import _hidden_settings
import _settings
import _worksheet_downloader

class Contest(object):
    def __init__(self, lst):
        super(Contest, self).__init__()
        self.key = lst[_settings.CONTESTS_KEY_COLUMN]
        self.short_name = lst[_settings.CONTESTS_SHORT_NAME_COLUMN]
        self.remaining = int(lst[_settings.CONTESTS_REMAINING_COLUMN])
        self.organizer = lst[_settings.CONTESTS_ORGANIZER_COLUMN]
        self.full_name = lst[_settings.CONTESTS_FULL_NAME_COLUMN]
        self.year = int(lst[_settings.CONTESTS_YEAR_COLUMN])
        self.round = lst[_settings.CONTESTS_ROUND_COLUMN]
        self.num_tasks = int(lst[_settings.CONTESTS_NUM_TASKS_COLUMN])
        self.url = lst[_settings.CONTESTS_URL_COLUMN]

class Task(object):
    def __init__(self, lst):
        super(Task, self).__init__()
        self.contest_short_name = lst[_settings.TASKS_CONTESTS_SHORT_NAME_COLUMN]
        self.name = lst[_settings.TASKS_NAME_COLUMN]
        self.text_url = lst[_settings.TASKS_TEXT_URL_COLUMN]
        self.pages = map(int, lst[_settings.TASKS_PAGES_COLUMN].split(','))
        self.tests_zip = lst[_settings.TASKS_TESTS_ZIP_COLUMN]
        self.tests_in_path = lst[_settings.TASKS_TESTS_IN_PATH_COLUMN]
        self.tests_in_to_out = lst[_settings.TASKS_TESTS_IN_TO_OUT_COLUMN]
        self.tests_num_io = lst[_settings.TASKS_TESTS_NUM_IO_COLUMN]

class DataManager(object):
    def __init__(self, read_cached=True):
        super(DataManager, self).__init__()
        self.downloader = _worksheet_downloader.WorksheetDownloader(
                _hidden_settings.EMAIL, _hidden_settings.PASSWORD)
        self.read_cached = read_cached
        self.contests = None
        self.tasks = None

    def get_contests(self, read_cached=None):
        if read_cached == None:
            read_cached = self.read_cached
        if self.contests == None or read_cached == False:
            self.__load_contests()
        return self.contests

    def get_tasks(self, read_cached=None):
        if read_cached == None:
            read_cached = self.read_cached
        if self.tasks == None or read_cached == False:
            self.__load_tasks()
        return self.tasks

    def __load_contests(self):
        tsv_contests = self.downloader.download(_settings.CONTESTS_ID, _settings.CONTESTS_GID)
        rows = list(csv.reader(tsv_contests, delimiter='\t'))
        rows = rows[_settings.CONTESTS_HEADER_SIZE:]
        self.contests = []
        for row in rows:
            self.contests.append(Contest(row))

    def __load_tasks(self):
        tsv_tasks = self.downloader.download(_settings.TASKS_ID, _settings.TASKS_GID)
        rows = list(csv.reader(tsv_tasks, delimiter='\t'))
        rows = rows[_settings.TASKS_HEADER_SIZE:]
        self.tasks = []
        for row in rows:
            self.tasks.append(Task(row))
