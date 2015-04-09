import re, os, csv, urllib2
import _hidden_settings
import _settings
import _worksheet_downloader
import contest_names
import unicodedata

class Contest(object):
    def __init__(self, lst):
        super(Contest, self).__init__()
        self.key = lst[_settings.CONTESTS_KEY_COLUMN]
        self.short_name = lst[_settings.CONTESTS_SHORT_NAME_COLUMN]
        self.remaining = int(lst[_settings.CONTESTS_REMAINING_COLUMN])
        self.organizer = lst[_settings.CONTESTS_ORGANIZER_COLUMN]
        self.full_name = lst[_settings.CONTESTS_FULL_NAME_COLUMN].decode('utf-8')
        self.year = int(lst[_settings.CONTESTS_YEAR_COLUMN])
        self.round = lst[_settings.CONTESTS_ROUND_COLUMN]
        self.num_tasks = int(lst[_settings.CONTESTS_NUM_TASKS_COLUMN])
        self.url = lst[_settings.CONTESTS_URL_COLUMN]

    def full_name_plural(self):
        return contest_names.PLURALS[self.full_name]

class Task(object):
    def __init__(self, lst):
        super(Task, self).__init__()
        self.contests_key = lst[_settings.TASKS_CONTESTS_KEY_COLUMN]
        self.name = lst[_settings.TASKS_NAME_COLUMN].decode('utf-8')
        self.text_pdf_url = lst[_settings.TASKS_TEXT_URL_COLUMN]
        self.pages = map(int, lst[_settings.TASKS_PAGES_COLUMN].split(','))
        self.tests_zip_url = lst[_settings.TASKS_TESTS_ZIP_COLUMN]
        self.tests_in_path = lst[_settings.TASKS_TESTS_IN_PATH_COLUMN]
        self.tests_in_to_out = lst[_settings.TASKS_TESTS_IN_TO_OUT_COLUMN]
        self.tests_num_io = lst[_settings.TASKS_TESTS_NUM_IO_COLUMN]

    def key(self):
        return self.contests_key + '-' + unicodedata.normalize(
                'NFD', self.name).encode('ascii', 'ignore')

    def __hash__(self):
        return self.key().__hash__()

    def __write_to_file(self, input_stream, dst):
        ofile = open(dst, "wb")
        ofile.write(input_stream.read())
        ofile.close()

    def __download_url(self, url, dst):
        stub = _settings.CACHE_DIR + "/" + \
                re.sub(r'[^a-zA-Z0-9_]', '', url)
        if not os.path.isfile(stub):
            req = urllib2.Request(url)
            self.__write_to_file(urllib2.urlopen(req), stub);
        return self.__write_to_file(open(stub, "rb"), dst)

    def download_tests_zip(self, dst):
        return self.__download_url(self.tests_zip_url, dst)

    def download_text_pdf(self, dst):
        return self.__download_url(self.text_pdf_url, dst)


class DataManager(object):
    def __init__(self, read_cached=True, downloader=None):
        super(DataManager, self).__init__()
        self.__check_settings()
        if downloader == None :
            self.__downloader = _worksheet_downloader.WorksheetDownloader(
                    _hidden_settings.EMAIL, _hidden_settings.PASSWORD)
        else :
            self.__downloader = downloader
        self.read_cached = read_cached
        self.__contests = None
        self.__tasks = None
        self.__contest_tasks_dict = None
        self.__task_contest_dict = None

    def get_contests(self, read_cached=None):
        if read_cached == None:
            read_cached = self.read_cached
        if self.__contests == None or read_cached == False:
            self.__load_contests()
        return self.__contests[:]

    def get_tasks(self, read_cached=None):
        if read_cached == None:
            read_cached = self.read_cached
        if self.__tasks == None or read_cached == False:
            self.__load_tasks()
        return self.__tasks[:]

    def tasks_in_contest(self, contest, read_cached=None):
        if read_cached == None:
            read_cached = self.read_cached
        if self.__contest_tasks_dict == None or read_cached == False:
            self.__build_contest_tasks_dict(read_cached)
        return self.__contest_tasks_dict.get(contest.key, [])[:]

    def contest_of_task(self, task, read_cached=None):
        if read_cached == None:
            read_cached = self.read_cached
        if self.__task_contest_dict == None or read_cached == False:
            self.__build_task_contest_dict(read_cached)
        return self.__task_contest_dict.get(task, None)

    def __check_settings(self):
        try:
            os.mkdir(_settings.CACHE_DIR)
        except OSError:
            assert os.path.isdir(_settings.CACHE_DIR)

    def __load_contests(self):
        tsv_contests = self.__downloader.download(
                _settings.CONTESTS_ID, _settings.CONTESTS_GID)
        rows = list(csv.reader(tsv_contests, delimiter='\t'))
        rows = rows[_settings.CONTESTS_HEADER_SIZE:]
        self.__contests = []
        for row in rows:
            self.__contests.append(Contest(row))

    def __load_tasks(self):
        tsv_tasks = self.__downloader.download(
                _settings.TASKS_ID, _settings.TASKS_GID)
        rows = list(csv.reader(tsv_tasks, delimiter='\t'))
        rows = rows[_settings.TASKS_HEADER_SIZE:]
        self.__tasks = []
        for row in rows:
            self.__tasks.append(Task(row))

    def __build_contest_tasks_dict(self, read_cached):
        if read_cached == None:
            read_cached = self.read_cached
        self.get_contests(read_cached)
        self.get_tasks(read_cached)
        self.__contest_tasks_dict = {}
        for contest in self.__contests:
            self.__contest_tasks_dict[contest.key] = []
        for task in self.__tasks:
            self.__contest_tasks_dict[task.contests_key].append(task)

    def __build_task_contest_dict(self, read_cached=None):
        if read_cached == None:
            read_cached = self.read_cached
        self.get_contests(read_cached)
        self.get_tasks(read_cached)
        self.__task_contest_dict = {}
        for contest in self.__contests:
            tasks = self.tasks_in_contest(contest, True)
            for task in tasks:
                self.__task_contest_dict[task] = contest
