import re, os, csv, urllib2
import _hidden_settings
import _settings
import _worksheet_downloader
import contest_names
import unicodedata
import _tsv_from_spreadsheet

class Contest(object):
    def __init__(self, lst):
        super(Contest, self).__init__()
        self.key = lst[_settings.CONTESTS_KEY_COLUMN].strip()
        self.short_name = lst[_settings.CONTESTS_SHORT_NAME_COLUMN].strip()
        self.remaining = int(lst[_settings.CONTESTS_REMAINING_COLUMN])
        self.organizer = lst[_settings.CONTESTS_ORGANIZER_COLUMN].strip()
        self.full_name = lst[_settings.CONTESTS_FULL_NAME_COLUMN].decode('utf-8').strip()
        self.year = int(lst[_settings.CONTESTS_YEAR_COLUMN])
        self.round = lst[_settings.CONTESTS_ROUND_COLUMN].strip()
        self.num_tasks = int(lst[_settings.CONTESTS_NUM_TASKS_COLUMN])
        self.url = lst[_settings.CONTESTS_URL_COLUMN].strip()

    def full_name_plural(self):
        return contest_names.PLURALS[self.full_name]

class Task(object):
    def __init__(self, lst):
        super(Task, self).__init__()
        self.contests_key = lst[_settings.TASKS_CONTESTS_KEY_COLUMN].strip()
        self.name = lst[_settings.TASKS_NAME_COLUMN].decode('utf-8').strip()
        self.text_pdf_url = lst[_settings.TASKS_TEXT_URL_COLUMN].strip()
        self.pages = map(int, lst[_settings.TASKS_PAGES_COLUMN].split(','))
        self.tests_zip_url = lst[_settings.TASKS_TESTS_ZIP_COLUMN].strip()
        self.tests_in_path = lst[_settings.TASKS_TESTS_IN_PATH_COLUMN].strip()
        self.tests_in_to_out = lst[_settings.TASKS_TESTS_IN_TO_OUT_COLUMN].strip()
        try:
            self.tests_num_io = int(lst[_settings.TASKS_TESTS_NUM_IO_COLUMN])
        except:
            pass

    def normalized_name(self):
        return unicodedata.normalize('NFD', self.name).encode(
                'ascii', 'ignore').split()[0].lower()
    def key(self):
        return self.contests_key + '-' + self.normalized_name()

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

    def __eq__(self, other):
        return self.key() == other.key()


class DataManager(object):
    def __init__(self, read_cached=True, tsv_provider=None):
        super(DataManager, self).__init__()
        self.__check_settings()
        if tsv_provider == None:
            self.__tsv_provider = _tsv_from_spreadsheet.TsvFromSpreadsheet()
        self.read_cached = read_cached
        self.__contests = None
        self.__tasks = None
        self.__contest_tasks_dict = None
        self.__task_contest_dict = None
        self.__contest_names_dict = None

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
        rows = self.__tsv_provider.get_contests()
        self.__contests = []
        for row in rows:
            self.__contests.append(Contest(row))

    def __load_tasks(self):
        rows = self.__tsv_provider.get_tasks()
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

    def __build_name_dicts(self, read_cached=None):
        if(read_cached == None):
            read_cached = self.read_cached
        if self.__contest_names_dict == None or read_cached == False:
            names = self.__tsv_provider.get_names()
            self.__contest_names_dict = {}
            for row in names:
                short_name = row[_settings.VALUES_CONTEST_SHORT_NAME_COLUMN]
                full_name = row[_settings.VALUES_CONTEST_FULL_NAME_COLUMN]
                if short_name == '': 
                    continue
                if full_name == '': 
                    full_name = short_name
                self.__contest_names_dict[short_name] = full_name

    def get_contest_full_name(self, short_name, read_cached=None):
        if(read_cached == None):
            read_cached = self.read_cached
        self.__build_name_dicts(read_cached)
        if short_name in self.__contest_names_dict:
            return self.__contest_names_dict[short_name]
        else:
            return short_name
