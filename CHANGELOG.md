# CHANGELOG

MvdP work on the service editor.

## 22-1-2026

- started integration xslt in FastAPI, uncertain yet how exactly 
- removed hooks from stalling

    http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3/action/history (does not work anymore)
    http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3/history

TODO 
- how to connect from stalling to this in the interface? 

## 21-1-2026

- add xslt transformation  json2xml and xml2html result: a history list in html

## 14-1-2026

- add endpoint: one record of a certain epoch output, html, json, xml, pdf

## 7-1-2026

- add endpoint: all history of a certain record, json output
