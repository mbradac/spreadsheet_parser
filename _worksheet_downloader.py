import re, urllib, urllib2

class _Spreadsheet(object):
    def __init__(self, key, gid, file_format):
        super(_Spreadsheet, self).__init__()
        self.key = key
        self.gid = gid
        self.file_format = file_format

    def get_url(self):
        url_format = 'https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=%s&gid=%s'
        return url_format % (self.key, self.file_format, self.gid)


class WorksheetDownloader(object):
    def __init__(self):
        super(WorksheetDownloader, self).__init__()

    def download(self, spreadsheet_id, gid='0', file_format='tsv'):
        spreadsheet = _Spreadsheet(spreadsheet_id, gid, file_format)
        req = urllib2.Request(spreadsheet.get_url())
        return urllib2.urlopen(req)
