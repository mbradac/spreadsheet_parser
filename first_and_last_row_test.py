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

print b[0].contest_short_name
print b[0].name
print b[0].text_url
print b[0].pages
print b[0].tests_zip
print b[0].tests_in_path
print b[0].tests_in_to_out
print b[0].tests_num_io
print ''

print b[-1].contest_short_name
print b[-1].name
print b[-1].text_url
print b[-1].pages
print b[-1].tests_zip
print b[-1].tests_in_path
print b[-1].tests_in_to_out
print b[-1].tests_num_io
print ''
