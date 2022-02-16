import json, re, text2num

def load_knowledge(department):
    with open("knowledge.json", "r", encoding='utf-8') as file:
        knowledge = json.load(file)[department]
    return knowledge

def load_rules(department):
    with open("rules.json", "r", encoding='utf-8') as file:
        rules = json.load(file)['RULE_'+department]
    return rules

def load_docs(department):
    with open("docs.json", "r", encoding='utf-8') as file:
        docs = json.load(file)['DOCS_'+department]
    return docs

def get_serviceID(department, speech):
    rules = load_rules(department)
    SID = ''
    QSID = ''
    parent_rule, deep, closein = get_parent_rule(speech, rules) # получаем родительское правило
    if parent_rule != '': #если найдено родительское правило
        if deep != 'END':
            response = get_closer(speech, deep, closein)
            while response[0] == '': #вызываем "функцию приближения" до тех пор пока нам не вернется подсервис
                speech = speech + ' -> ' + input(response[2] + ': -')
                response = get_closer(speech, deep, response[2])
            else:
                SID = parent_rule + response[0]
        else:
            SID = parent_rule
        if '/' in SID:
            SID = SID[SID.find('//') + 2:]
        print('SPEECH :: ' + speech)
        return department + SID
    else:
        return 'Не найдено' # goto 0

def get_serviceName(SID, department):
    knowledge = load_knowledge(department)
    if SID[-1] == '.':
        serviceName = knowledge[SID]['PARENT']
        if 'SInfo' in knowledge[SID]:
            SInfo = knowledge[SID]['SInfo']
            return serviceName, SInfo
    else:
        serviceName = knowledge[SID[:-1]][SID]
        if 'SInfo' in knowledge[SID[:-1]]:
            SInfo = knowledge[SID[:-1]]['SInfo']
            return serviceName, SInfo
    return serviceName

def get_serviceDocs(SID, department):
    docs = load_docs(department)
    serviceDocs = docs[SID]
    return serviceDocs

def get_parent_rule(speech, rules): # Поиск "родительского правила"
    parent_rule = ''
    deep = ''
    closein = 'END'
    for rule in rules:
        if (re.search(rule, speech, re.IGNORECASE)):
            parent_rule = rules[rule]['PARENT']
            deep = rules[rule]['deep']
            if 'closein' in rules[rule]:
                closein = rules[rule]['closein']
            break
    return parent_rule, deep, closein

def get_closer(speech, deep, closein): # Рекурсивная "функция приближения" к конкретной услуге
    subservice = ''
    eval_rule = False # Проверка истинности выражения для случаев когда нужно сверить возраст для дальнейшго определения подсервиса
    try:
        speech_num = int(text2num.extract(speech))
    except:
        speech_num = 0
    for rule in deep:
        try:
            eval_rule = eval(rule)
        except:
            eval_rule = False
        if (re.search(rule, speech, re.IGNORECASE)) or eval_rule == True: # ищем совпадения в правилах
            if isinstance(deep[rule], dict) and 'deep' in deep[rule].keys(): # совпадения есть но это не конечный уровень вложенности - вызываем сами себя
                return get_closer(speech, deep[rule]['deep'], deep[rule]['closein'])
            else: # уровень вложенности последний
                if (re.search(rule, speech, re.IGNORECASE)) or eval_rule == True: # ищем совпадения в правилах
                    subservice = deep[rule]
                    return subservice, deep, closein
    if subservice == '':
        return subservice, deep, closein

def get_serviceAll(speech, department):
    SID = get_serviceID(department, speech)
    if SID != 'Не найдено' and SID != 'Оператор':
        try:
            serviceName, SInfo = get_serviceName(SID, department)
        except:
            SInfo = '-'
            serviceName = get_serviceName(SID, department)
        serviceDocs = get_serviceDocs(SID, department)
        return f'''
        // REPORT //
        SID :: {SID}
        SERVICE :: {serviceName}    
        DOCS :: {serviceDocs}
        SINFO :: {SInfo}
        // REPORT //
        '''
    else:
        return SID

print(get_serviceAll( input('Услуга: '), 'MVD_'))
# print(get_serviceID('MVD_', 'по поводу прописки'))