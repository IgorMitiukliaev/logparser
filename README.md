# logparser
ODBC log / trace parser 

Парсер предназначен для извлечения SQL-запросов из ODBC-лога или трассы и подстановки параметров.
Для работы нужно скопировать фрагмент лога/трассы в файл log.txt и запустить скрипт (необходим Python 3.11)


### Формат ODBC-лога:

`[2023-Nov-17 17:13:54.323608] <NOTE>  NSQL:` исходный запрос который приходит из прикладного кода. (NATIVE_SQL)  
`[2023-Nov-17 17:13:54.408382] <NOTE>  PHSQL:` запрос обработанный конвертером, там пронумерованы placeholder. (PLACEHOLDER_SQL)  
`[2023-Nov-17 17:13:54.416360] <NOTE>  bind map:` карта placeholder  
`[2023-Nov-17 17:13:54.416360] <NOTE>  SQL:` запрос pgsql из конвертера, обработанный “перестановщиком placeholder”, все placeholder заменены на ‘?’   
`[2023-Nov-17 17:13:54.417357] <NOTE>  to RECORD:` строка, содержащая параметр  

 ### Формат трассы:

Строка с параметром определяется по наличию 'Parameter'  
`#1, type RSDSHORT, value: -32768                       RsdCmdSp.cpp (line 1561)         Parameter\Input `  

Запрос считывается со строки, следующей за последним параметром:  
`RSDODBC               Parameter\Input                  #15, type RSDDATE, value: 8.12.2025                      4  `  
`RSDODBC               SQL\Execute                      select   t.t_infoid,  t.t_direct,  t.t_trn,  t.t_r       1  `  

Запрос считывается до строки, содержащей Result=  
`RSDODBC               SQL\Execute                      Result=  `  

