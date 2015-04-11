import csv
import _settings
import _hidden_settings
import _worksheet_downloader

class TsvFromSpreadsheet(object):
    def __init__(self):
        super(TsvFromSpreadsheet, self).__init__()
        self.__downloader = _worksheet_downloader.WorksheetDownloader(
                _hidden_settings.EMAIL, _hidden_settings.PASSWORD)

    def get_contests(self):
        tsv_contests = self.__downloader.download(
                _settings.CONTESTS_ID, _settings.CONTESTS_GID)
        rows = list(csv.reader(tsv_contests, delimiter='\t'))
        rows = rows[_settings.CONTESTS_HEADER_SIZE:]
        return rows
    
    def get_tasks(self):
        tsv_tasks = self.__downloader.download(
                _settings.TASKS_ID, _settings.TASKS_GID)
        rows = list(csv.reader(tsv_tasks, delimiter='\t'))
        rows = rows[_settings.TASKS_HEADER_SIZE:]
        return rows

    def get_names(self):
        tsv_names = self.__downloader.download(
                _settings.VALUES_ID, _settings.VALUES_GID)
        rows = list(csv.reader(tsv_names, delimiter='\t'))
        rows = rows[_settings.VALUES_HEADER_SIZE:]
        return rows
