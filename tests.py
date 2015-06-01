import os
from data_manager import DataManager

manager = DataManager()
a = manager.get_contests()
b = manager.get_tasks()

print a[0].key
print a[0].short_name
print a[0].remaining
print a[0].organizer
print a[0].full_name
print a[0].year
print a[0].round
print a[0].num_tasks
print a[0].url
print ''

print a[-1].key
print a[-1].short_name
print a[-1].remaining
print a[-1].organizer
print a[-1].full_name
print a[-1].year
print a[-1].round
print a[-1].num_tasks
print a[-1].url
print ''

print b[0].contests_key
print b[0].name
print b[0].text_pdf_url
print b[0].pages
print b[0].tests_zip_url
print b[0].tests_in_path
print b[0].tests_in_to_out
print b[0].tests_num_io
print ''

print b[-1].contests_key
print b[-1].name
print b[-1].text_pdf_url
print b[-1].pages
print b[-1].tests_zip_url
print b[-1].tests_in_path
print b[-1].tests_in_to_out
print b[-1].tests_num_io
print ''

b[0].download_text_pdf('0.pdf')
b[0].download_tests_zip('0.zip')
assert os.path.isfile('0.pdf')
assert os.path.isfile('0.zip')
os.remove('0.pdf')
os.remove('0.zip')

c = manager.tasks_in_contest(a[0])
print len(c)
print c[0].name

print manager.contest_of_task(b[0]).full_name
print b[6].name
print b[6].key()
print b[6].normalized_name()
print b[34].name
print b[34].key()
print b[34].normalized_name()

print manager.get_contest_full_name('skolsko')
print manager.get_contest_full_name('drzavno')
print manager.get_contest_full_name('hio')
print manager.get_contest_full_name('nepostoji')

print manager.get_contest_full_name('skolsko', True)
print manager.get_contest_full_name('drzavno', True)
print manager.get_contest_full_name('hio', True)
print manager.get_contest_full_name('nepostoji', True)

print manager.get_round_full_name('skolsko', 'ss_prva')
print manager.get_round_full_name('sir', 'vrhnje')
print manager.get_round_full_name('hio', '')
print manager.get_round_full_name('honi', 'kolo7')
print manager.get_round_full_name('studentsko', 'krug1')


print manager.contest_short_names()
print manager.round_short_names()
