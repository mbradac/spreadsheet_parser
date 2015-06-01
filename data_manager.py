'''Provides classes representing contests and tasks and class used for
accessing and parsing contests and tasks.
'''
import re
import os
import csv
import urllib2
import _hidden_settings
import _settings
import _worksheet_downloader
import unicodedata
import _tsv_from_spreadsheet

class Contest(object):
    def __init__(self, lst):
        '''Constructs contest from list of values.

        Args:
            lst (list): List with values used for constructing object,
                see constants in _settings.py for list specification.
        '''
        super(Contest, self).__init__()
        self.key = lst[_settings.CONTESTS_KEY_COLUMN].strip()
        self.short_name = lst[_settings.CONTESTS_SHORT_NAME_COLUMN].strip()
        self.remaining = int(lst[_settings.CONTESTS_REMAINING_COLUMN])
        self.organizer = lst[_settings.CONTESTS_ORGANIZER_COLUMN].strip()
        self.full_name = lst[_settings.CONTESTS_FULL_NAME_COLUMN].decode(
                'utf-8').strip()
        self.year = int(lst[_settings.CONTESTS_YEAR_COLUMN])
        self.round = lst[_settings.CONTESTS_ROUND_COLUMN].strip()
        self.num_tasks = int(lst[_settings.CONTESTS_NUM_TASKS_COLUMN])
        self.url = lst[_settings.CONTESTS_URL_COLUMN].strip()


class Task(object):
    def __init__(self, lst):
        '''Constructs task from list of values.

        Args:
            lst (list): List with values used for constructing object,
                see constants in _settings.py for list specification.
        '''
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
        '''Returns:
            Task's normalized name ([a-z0-9_]).
        '''
        return unicodedata.normalize('NFD', self.name).encode(
                'ascii', 'ignore').split()[0].lower()
    def key(self):
        '''Returns:
            Unique key of task composed of contests_key and normalized_name
        '''
        return self.contests_key + '-' + self.normalized_name()

    def __hash__(self):
        return self.key().__hash__()

    def __write_to_file(self, input_stream, dst):
        '''Writes data from input_stream to dst.

        Args:
            input_stream : Input data (usually a file).
            dst: Path of destination file.
        '''
        ofile = open(dst, "wb")
        ofile.write(input_stream.read())
        ofile.close()

    def __download_url(self, url, dst):
        '''Downloads data from given url and saves it to file with path dst.
        If file already exsists in cache dir it is not downloaded again.

        Args:
            url (str): Url from which data is downloaded.
            dst (str): Path of destination file.
        '''
        stub = _settings.CACHE_DIR + "/" + re.sub(r'[^a-zA-Z0-9_]', '', url)
        if not os.path.isfile(stub):
            req = urllib2.Request(url)
            self.__write_to_file(urllib2.urlopen(req), stub);
        return self.__write_to_file(open(stub, "rb"), dst)

    def download_tests_zip(self, dst):
        '''Downloads zip with task's tests.

        Args:
            dst (str): Path of destination file.
        '''
        return self.__download_url(self.tests_zip_url, dst)

    def download_text_pdf(self, dst):
        '''Downloads task's text.

        Args:
            dst (str): Path of destination file.
        '''
        return self.__download_url(self.text_pdf_url, dst)

    def __eq__(self, other):
        return self.key() == other.key()


class DataManager(object):
    '''Provides methods for accessing contests and tasks given by tsv_provider.
    Read doc for __init__ for details.
    '''

    def __init__(self, read_cached=True, tsv_provider=None):
        '''Constructs object which parses contests and tasks given by
        tsv_provider.

        Args:
            read_cached (bool): If True other function tries to read cached
                data, otherwise they retrieve it everytime from tsv_provider.
                read_cached can be oveeridden by every function call.
                read_cached doesn't affect cache of download_text_pdf
                and download_tests_zip. Defaults to True.

            tsv_provider : Provider of tsv data. This class uses methods
               get_contests, get_tasks, get_names of tsv_provider. tsv_provider
               defaults to TsvFromSpreadsheet.
        '''
        super(DataManager, self).__init__()
        self.__create_cache_dir()
        if tsv_provider == None:
            self.__tsv_provider = _tsv_from_spreadsheet.TsvFromSpreadsheet()
        self.read_cached = read_cached
        self.__contests = None
        self.__tasks = None
        self.__contest_tasks_dict = None
        self.__task_contest_dict = None
        self.__contest_names_dict = None
        self.__round_names_dict = None
        self.__contest_short_names_list = None
        self.__round_short_names_list = None

    def get_contests(self, read_cached=None):
        '''Args:
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.

        Returns:
            list: List of Contest objects.
        '''
        self.__update(read_cached, self.__contests, self.__load_contests)
        return self.__contests[:]

    def get_tasks(self, read_cached=None):
        '''Args:
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.

        Returns:
            list: List of Task objects.
        '''
        self.__update(read_cached, self.__tasks, self.__load_tasks)
        return self.__tasks[:]

    def tasks_in_contest(self, contest, read_cached=None):
        '''Args:
            constest (Contest): Contest that is queried for tasks.
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.

        Returns:
            list: List of Task objects.
        '''
        self.__update(read_cached, self.__contest_tasks_dict, 
                self.__build_contest_tasks_dict, read_cached)
        return self.__contest_tasks_dict.get(contest.key, [])[:]

    def contest_of_task(self, task, read_cached=None):
        '''Args:
            task (Task): Task that is queried for contest.
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.
        Returns:
            Contest: Contest in which given task was used.
        '''
        self.__update(read_cached, self.__task_contest_dict,
                self.__build_task_contest_dict, read_cached)
        return self.__task_contest_dict.get(task, None)

    def contest_short_names(self, read_cached=None):
        '''Args:
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.
        Returns:
            list: Short names of contests.
        '''
        self.__update(read_cached, self.__contest_short_names_list,
                self.__build_name_dicts)
        return self.__contest_short_names_list[:]

    def round_short_names(self, read_cached=None):
        '''Args:
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.
        Returns:
            list: Short names of rounds.
        '''
        self.__update(read_cached, self.__round_short_names_list,
                self.__build_name_dicts)
        return self.__round_short_names_list

    def get_contest_full_name(self, short_name, plural=False, read_cached=None):
        '''Args:
            short_name (str): contest's short name
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.

        Returns:
            str: Full name of contest whose short_name is given.
        '''
        self.contest_short_names(read_cached)
        if short_name in self.__contest_names_dict:
            t = 1 if plural else 0
            return self.__contest_names_dict[short_name][t]
        else:
            return short_name

    def get_round_full_name(self, contest_name, round_name, read_cached=None):
        '''Args:
            contest_name (str): contest's short name
            round_name (str): contest's round name
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.

        Returns:
            str: Full name of round whose short name and round name is given.
        '''
        self.round_short_names(read_cached)
        key = (contest_name, round_name)
        if key in self.__round_names_dict:
            return self.__round_names_dict[key]
        else:
            return '%s-%s' % key

    def __create_cache_dir(self):
        '''Creates cache dir if it doesn't exist. Path of cache dir is defined
        by CACHE_DIR in _settings.py. Cache dir is never deleted by program.
        Cache dir is used for storing downloaded task pdf and task test data
        zip. Cache dir is always used, i. e. read_cached doesn't effect 
        behavior of pdf and zip download.
        '''
        try:
            os.mkdir(_settings.CACHE_DIR)
        except OSError:
            assert os.path.isdir(_settings.CACHE_DIR)

    def __update(self, read_cached, content, update_function, *args):
        '''Checks for cached data, if cached data doesn't exist or read_cached
        is False update_function is called with args.

        Args:
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.

            content: Content that is checked for existence. Usually content
                that is calculated by update_function. If None update_function
                is called regardless of read_cached.

            update_function: Function that is called to update content. Its
                return value is not used.

            args: Arguments passed to update_function.
        '''
        if read_cached == None:
            read_cached = self.read_cached
        if content == None or read_cached == False:
            update_function(*args)

    def __load_contests(self):
        '''Constructs list of Contest object. Uses _tsv_provider as source of
        data used to create those objects. Those objects are stored in
        __contests.
        '''
        rows = self.__tsv_provider.get_contests()
        self.__contests = []
        for row in rows:
            self.__contests.append(Contest(row))

    def __load_tasks(self):
        '''Constructs list of Task object. Uses _tsv_provider as source of
        data used to create those objects. Those objects are stored in
        __tasks.
        '''
        rows = self.__tsv_provider.get_tasks()
        self.__tasks = []
        for row in rows:
            self.__tasks.append(Task(row))

    def __build_contest_tasks_dict(self, read_cached=None):
        '''Builds dictionary that is used by tasks_in_contest. Key is
        contest.key and value is list of tasks.

        Args:
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.
        '''
        self.get_contests(read_cached)
        self.get_tasks(read_cached)
        self.__contest_tasks_dict = {}
        for contest in self.__contests:
            self.__contest_tasks_dict[contest.key] = []
        for task in self.__tasks:
            self.__contest_tasks_dict[task.contests_key].append(task)

    def __build_task_contest_dict(self, read_cached=None):
        '''Builds dictionary that is used by contest_of_task. Key is
        task and value is contest.

        Args:
            read_cached (bool, optional): If provided overrides read_cached
                given to constructor. Read constructor doc for details.
        '''
        self.get_contests(read_cached)
        self.get_tasks(read_cached)
        self.__task_contest_dict = {}
        for contest in self.__contests:
            tasks = self.tasks_in_contest(contest, True)
            for task in tasks:
                self.__task_contest_dict[task] = contest

    def __build_name_dicts(self):
        '''Builds dicts and lists used by functions that return names of
        contests and rounds.
        '''
        names = self.__tsv_provider.get_names()
        self.__contest_names_dict = {}
        self.__round_names_dict = {}
        self.__contest_short_names_list = []
        self.__round_short_names_list = []

        for row in names:
            short_name = row[_settings.VALUES_CONTEST_SHORT_NAME_COLUMN]
            full_name = row[_settings.VALUES_CONTEST_FULL_NAME_COLUMN]
            full_name_plural = row[_settings.VALUES_CONTEST_FULL_NAME_PLURAL_COLUMN]
            contest_name = row[_settings.VALUES_ROUND_NAME_CONTEST_COLUMN]
            round_name = row[_settings.VALUES_ROUND_NAME_ROUND_COLUMN]
            round_short_name = row[_settings.VALUES_ROUND_NAME_ROUND_SHORT_COLUMN]
            round_full_name = row[_settings.VALUES_ROUND_NAME_ROUND_FULL_COLUMN]

            if short_name != '':
                if full_name == '':
                    full_name = short_name
                self.__contest_names_dict[short_name] = (full_name, full_name_plural)
            if contest_name != '' or round_name != '':
                self.__round_names_dict[(contest_name, round_name)] = round_full_name
            if short_name != '':
                self.__contest_short_names_list.append(short_name)
            if round_short_name != '':
                self.__round_short_names_list.append(round_short_name)
