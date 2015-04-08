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

print a[0].full_name_plural()

print manager.contest_of_task(b[0]).full_name
print b[6].name
