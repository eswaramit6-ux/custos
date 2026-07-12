content = open('utils/custos_agent.py', encoding='utf-8').read()
content = content.replace('llama3-8b-8192', 'llama-3.3-70b-versatile')
open('utils/custos_agent.py', 'w', encoding='utf-8').write(content)
print('Fixed!')
