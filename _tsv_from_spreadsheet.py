'''Contains class that provides list getters of data stored in spreadsheets.'''
import csv
import _settings
import _hidden_settings
import _worksheet_downloader

class TsvFromSpreadsheet(object):
    def __init__(self):
        '''Constructs object that uses google account with password and email
        stored in _hidden_settings for downloading google spreadsheets.
        '''
        super(TsvFromSpreadsheet, self).__init__()
        self.__downloader = _worksheet_downloader.WorksheetDownloader()

    def get_contests(self):
        '''Returns:
            list: List of strings representing contests from spreadsheet.
        '''
        return self.__get_content(_settings.CONTESTS_ID, 
                _settings.CONTESTS_GID, _settings.CONTESTS_HEADER_SIZE)

    def get_tasks(self):
        '''Returns:
            list: List of strings representing tasks from spreadsheet.
        '''
        return self.__get_content(_settings.TASKS_ID,
                _settings.TASKS_GID, _settings.TASKS_HEADER_SIZE)

    def get_names(self):
        '''Returns:
            list: List of strings representing names (of rounds, contests, ...)
                from spreadsheet.
        '''
        return self.__get_content(_settings.VALUES_ID, _settings.VALUES_GID,
                _settings.VALUES_HEADER_SIZE)

    def __get_content(self, content_id, content_gid, header_size):
        '''Args:
            content_id (str): Key of google spreadsheet (visible in url).
            content_gid (str): Gid of sheet of google spreadsheet
                (visible in url).
            header_size (int): Number of leading rows that will be discarded.
 
        Returns:
            list: List of strings from downloaded google spreadsheet.
        '''
        tsv_content = self.__downloader.download(content_id, content_gid)
        rows = list(csv.reader(tsv_content, delimiter='\t'))
        return rows[header_size:]
