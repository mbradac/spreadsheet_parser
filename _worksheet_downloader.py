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


class _Client(object):
    def __init__(self, email, password):
        super(_Client, self).__init__()
        self.email = email
        self.password = password

    def __get_auth_token(self, email, password, source, service):
        url = 'https://www.google.com/accounts/ClientLogin'
        params = {
            'Email': email, 'Passwd': password,
            'service': service,
            'accountType': 'HOSTED_OR_GOOGLE',
            'source': source
        }
        req = urllib2.Request(url, urllib.urlencode(params))
        return re.findall(r'Auth=(.*)', urllib2.urlopen(req).read())[0]

    def get_auth_token(self):
        source = type(self).__name__
        return self.__get_auth_token(self.email, self.password, source, service='wise')


class WorksheetDownloader(object):
    def __init__(self, email, password):
        super(WorksheetDownloader, self).__init__()
        self.client = _Client(email, password)

    def download(self, spreadsheet_id, gid='0', file_format='tsv'):
        spreadsheet = _Spreadsheet(spreadsheet_id, gid, file_format)
        headers = {
            'Authorization': 'GoogleLogin auth=' + self.client.get_auth_token(),
            'GData-Version': '3.0'
        }
        req = urllib2.Request(spreadsheet.get_url(), headers=headers)
        return urllib2.urlopen(req)
