#!/usr/bin/env python3
import re


def read_file(path):
    try:
        with open(path, 'r') as logobj:
            lines = logobj.readlines()
            return lines
    except EnvironmentError as err:
        return [err,]


def save_req(type, data):
    req = find_req(type, data)
    filename = "req_" + type
    save_file(filename, req)


def save_file(filename, data):
    try:
        filename += ".sql"
        with open(filename, 'w') as f:
            for line in data:
                f.write(line)
    except EnvironmentError as err:
        pass


def find_req(type, data):
    for line in data:
        if type in line:
            req = line.partition(type)[2][2:]
            if type == "NSQL":
                req = req[:-1:] + ';'
            return req


def find_req_trace(data):
    shift = (4, 8)
    pattern = r'^(.*?)#(\d+).+?type (\S+), value: (.+?)(\s{2,})(.+)?$'
    req = ''
    check_r = False
    check_p = False
    pos_beg = 0
    pos_end = 0
    for line in data:
        print('\n{0}\n{1}\n{2}'.format(check_p, check_r, line))
        match = re.search(pattern, line)
        if match and (not check_p) and (not check_r):
            _beg, i, t, v, _sp, _end = match.groups()
            pos_beg = len(_beg)
            pos_end = len(line) - len(_end) - shift[0]
            # print('------------>\n{0}\t{1}\n{2}\t{3}\n'.format(pos_beg, _beg, pos_end, _end))
            check_p = True
        elif not match:
            if check_p and not check_r:
                check_r = True
                check_p = False
            if line.find('Result=') >= 0:
                return req
            if check_r and not check_p:
                req += line[pos_beg:pos_end]
    print(req)
    return req + ';'


def read_binds(data):
    bind_map = []
    for line in data:
        if 'bind map' in line:
            pattern = r'(\d+) -> (\d+)'
            for match in re.finditer(pattern, line):
                bind_map.append((int(match[1]) - 1, int(match[2])-1))
    return bind_map


def read_params(data):
    params = []
    for line in data:
        if 'to RECORD:' in line:
            pattern = r'to RECORD: (\d+).+?type: (\S+) = \w+? - (\S+)'
            match = re.search(pattern, line)
            if match:
                print(match.groups())
                params.append(
                    (int(match.group(1)), match.group(2), match.group(3)))
    return params


def read_params_trace(data):
    params = []
    i = 0
    t = ''
    v = ''
    pos_beg = 0
    pos_end = 0
    for line in data:
        if 'Parameter' in line:
            pattern = r'^(.*?)#(\d+).+?type (\S+), value: (.+?)(\s{2,})(.+)?$'
            match = re.search(pattern, line)
            if match:
                _beg, i, t, v, _sp, _end = match.groups()
                pos_beg = len(_beg)
                pos_end = len(line) - len(_end)
                params.append((int(i), t, v))
        elif t.find('RSDLPSTR') == 0:
            params.pop()
            v = v + line[pos_beg:pos_end].strip()
            params.append((int(i), t, v))

    return params


def make_pg(params):
    p_pg = []
    for el in params:
        match el[1]:
            case 'RSDPT_CHAR':
                if el[2].isdigit():
                    p_pg.insert(int(el[0]), 'glob_func.chr({0})'.format(el[2]))
                else:
                    p_pg.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_SHORT':
                p_pg.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_LPSTR':
                p_pg.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_LONG':
                p_pg.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_NUMERIC':
                p_pg.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_TIMESTAMP':
                p_pg.insert(
                    int(el[0]), 'to_date(\'{0}\',\'DD:MM:YYYY\')'.format(format_date(el[2])))
            case 'RSDPT_DATE':
                p_pg.insert(
                    int(el[0]), 'to_date(\'{0}\',\'DD:MM:YYYY\')'.format(format_date(el[2])))
            case 'RSDPT_TIME':
                p_pg.insert(
                    int(el[0]), 'glob_func.to_timestamp_immutable(\'{0}\',\'HH24:MI:SS\')'.format(format_date(el[2])))
            case _:
                raise Exception('unknown type {0}'.format(el[1]))
    return p_pg
    # return sorted(params, key=lambda el: el[0])


def format_date(data):
    data = re.sub(r'^(\d):', r'0\1:', data)
    data = re.sub(r':(\d):', r':0\1:', data)
    return data


def make_ora(params):
    p_or = []
    for el in params:
        match el[1]:
            case 'RSDPT_CHAR':
                if el[2].isdigit():
                    p_or.insert(int(el[0]), 'chr({0})'.format(el[2]))
                else:
                    p_or.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_SHORT':
                p_or.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_LONG':
                p_or.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_LPSTR':
                p_or.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_NUMERIC':
                p_or.insert(int(el[0]), '{0}'.format(el[2]))
            case 'RSDPT_TIMESTAMP':
                p_or.insert(
                    int(el[0]), 'to_date(\'{0}\',\'DD:MM:YYYY\')'.format(el[2]))
            case 'RSDPT_DATE':
                p_or.insert(
                    int(el[0]), 'to_date(\'{0}\',\'DD:MM:YYYY\')'.format(el[2]))
            case 'RSDPT_TIME':
                p_or.insert(
                    int(el[0]), 'to_date(\'{0}\',\'HH24:MI:SS\')'.format(el[2]))
            case _:
                raise Exception('unknown type {0}'.format(el[1]))
    return p_or


def make_tr(params, isPG=True):
    p_tr = []
    if isPG:
        for el in params:
            match el[1]:
                case 'RSDLONG':
                    p_tr.insert(int(el[0]), '\'{0}\''.format(el[2]))
                case 'RSDCHAR':
                    if el[2].isdigit():
                        p_tr.insert(
                            int(el[0]), 'glob_func.chr({0})'.format(el[2]))
                    else:
                        p_tr.insert(int(el[0]), '{0}'.format(el[2]))
                case 'RSDTIMESTAMP':
                    p_tr.insert(
                        int(el[0]), 'glob_func.to_timestamp_immutable(\'{0}\',\'DD.MM.YYYY HH:MM:SS\')'.format(el[2]))
                case 'RSDSHORT':
                    p_tr.insert(int(el[0]), '{0}'.format(el[2]))
                case 'RSDLPSTR':
                    p_tr.insert(int(el[0]), '\'{0}\''.format(el[2]))
                case 'RSDDATE':
                    p_tr.insert(
                        int(el[0]), 'to_date(\'{0}\',\'DD.MM.YYYY\')'.format(el[2]))
                case _:
                    raise Exception('unknown type {0}'.format(el[1]))
    else:
        for el in params:
            match el[1]:
                case 'RSDLONG':
                    p_tr.insert(int(el[0]), '\'{0}\''.format(el[2]))
                case 'RSDCHAR':
                    if el[2].isdigit():
                        p_tr.insert(int(el[0]), 'chr({0})'.format(el[2]))
                    else:
                        p_tr.insert(int(el[0]), '{0}'.format(el[2]))
                case 'RSDTIMESTAMP':
                    p_tr.insert(
                        int(el[0]), 'to_timestamp(\'{0}\',\'DD.MM.YYYY HH:MM:SS\')'.format(el[2]))
                case 'RSDSHORT':
                    p_tr.insert(int(el[0]), '{0}'.format(el[2]))
                case 'RSDLPSTR':
                    p_tr.insert(int(el[0]), '\'{0}\''.format(el[2]))
                case 'RSDDATE':
                    p_tr.insert(
                        int(el[0]), 'to_date(\'{0}\',\'DD.MM.YYYY\')'.format(el[2]))
                case _:
                    raise Exception('unknown type {0}'.format(el[1]))
    return p_tr


def bind_pg(req, params, bind_map):
    pattern = r'\?\?(\d+)'
    p_pg = make_pg(params)
    new_req = ''
    start = 0
    index = 0
    for match in re.finditer(pattern, req):
        end, newstart = match.span()
        new_req += req[start:end]
        # index = bind_map[int(match.group(1))][0]
        par = p_pg[index]
        index += 1
        new_req += par
        start = newstart
    new_req += req[start:]
    new_req = new_req.replace('\"', '\'')
    return new_req


def bind_trace(req, params, isPG=True):
    pattern = r'\?'
    p_tr = make_tr(params, isPG)
    print(p_tr)
    new_req = ''
    start = 0
    index = 0
    for match in re.finditer(pattern, req):
        end, newstart = match.span()
        new_req += req[start:end]
        # index = bind_map[int(match.group(1))][0]
        par = p_tr[index]
        index += 1
        new_req += par
        start = newstart
    new_req += req[start:]
    new_req = new_req.replace('\"', '\'')
    return new_req


def bind_ora(req, params, bind_map):
    pattern = r'\?'
    p_ora = make_ora(params)
    bind_map_ora = sorted(bind_map, key=lambda el: el[1])
    new_req = ''
    start = 0
    count = 0
    for match in re.finditer(pattern, req):
        end, newstart = match.span()
        new_req += req[start:end]
        index = bind_map_ora[count][0]
        par = p_ora[index]
        count += 1
        new_req += par
        start = newstart
    new_req += req[start:]
    new_req = new_req.replace('\"', '\'')
    new_req = new_req.replace('{', '')
    new_req = new_req.replace('}', '')
    return new_req


def process_log(res):
    bind_map = read_binds(res)
    params = read_params(res)
    req_pg = find_req("PHSQL", res)
    if len(params) == 0:
        print('\t ---> No parameters found')
    else:
        req_pg_bound = bind_pg(req_pg, params, bind_map)
        save_file("req_PG_PARAMS", (req_pg_bound,))
        if len(bind_map) > 0:
            req_ora = find_req("NSQL", res)
            req_ora_bound = bind_ora(req_ora, params, bind_map)
            save_file("req_OR_PARAMS", (req_ora_bound,))
        else:
            print(
                '\t ---> No bind map available, unable to place parameters to ORACLE request')
    save_req("NSQL", res)
    save_req("PHSQL", res)
    save_req("SQL", res)


def process_trace(res, isPG=True):
    params = read_params_trace(res)
    req_trace = find_req_trace(res)
    req_bound = bind_trace(req_trace, params, isPG)
    save_file("req_TRACE_PARAMS", (req_bound,))


def main():
    res = read_file('log.txt')
    try:
        if res[0].startswith('['):
            process_log(res)
        elif res[0].startswith('OR'):
            process_trace(res, False)
        else:
            process_trace(res, True)
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    main()
