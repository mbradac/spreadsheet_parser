'''This module provides class for downloading google spreadsheet as tsv file.'''
import re
import urllib
import urllib2

class _Spreadsheet(object):
    '''One sheet from google spreadsheets.'''

    def __init__(self, key, gid, file_format):
        '''Constructs object representing google spreadsheet.

        Args:
            key (str): Key of google spreadsheet 
                (visible in spreadsheet's url).
            gid (str): Gid of sheet in spreadsheet
                (visible in spreadsheet's url).
            file_format (str): File format of spreadsheet (used by get_url
                when requested url of spreadsheet).
        '''
        super(_Spreadsheet, self).__init__()
        self.key = key
        self.gid = gid
        self.file_format = file_format

    def get_url(self):
        '''Returns:
            str: Url for download of google spreadsheet represented by self.
        '''
        url_format = ('https://spreadsheets.google.com/feeds/download/' + 
                'spreadsheets/Export?key=%s&exportFormat=%s&gid=%s')
        return url_format % (self.key, self.file_format, self.gid)


class WorksheetDownloader(object):
    '''Google spreadsheet downloader.'''

    def __init__(self):
        '''Constructs object for downloading spreadsheets.'''
        super(WorksheetDownloader, self).__init__()

    def download(self, spreadsheet_id, gid='0', file_format='tsv'):
        '''Downloads sheet from google spreadsheet.

        Args:
            spreadsheet_id (str): Key of google spreadsheet (visible in url).
            gid (str, optional): Gid of sheet in google spreadsheet 
                (visible in url of sheet), defaults to '0'.
            file_format (str, optional): Format in which downloaded file will
                be saved, defaults to 'tsv'.

        Returns:
            Downloaded sheet.
        '''
        spreadsheet = _Spreadsheet(spreadsheet_id, gid, file_format)
        req = urllib2.Request(spreadsheet.get_url())
        return urllib2.urlopen(req)
