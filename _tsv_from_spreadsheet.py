import csv
import _settings
import _hidden_settings
import _worksheet_downloader

class TsvFromSpreadsheet(object):
    def __init__(self):
        super(TsvFromSpreadsheet, self).__init__()
        self.__downloader = _worksheet_downloader.WorksheetDownloader()

    def get_contests(self):
        return self.__get_content(_settings.CONTESTS_ID, 
                _settings.CONTESTS_GID, _settings.CONTESTS_HEADER_SIZE)
    
    def get_tasks(self):
        return self.__get_content(_settings.TASKS_ID,
                _settings.TASKS_GID, _settings.TASKS_HEADER_SIZE)

    def get_names(self):
        return self.__get_content(_settings.VALUES_ID, _settings.VALUES_GID,
                _settings.VALUES_HEADER_SIZE)

    def __get_content(self, content_id, content_gid, header_size):
        tsv_content = self.__downloader.download(content_id, content_gid)
        rows = list(csv.reader(tsv_content, delimiter='\t'))
        return rows[header_size:]
