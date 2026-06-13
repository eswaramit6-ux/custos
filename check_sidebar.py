content = open('app.py', encoding='utf-8').read()
idx = content.find('API')
print(repr(content[idx-50:idx+300]))
