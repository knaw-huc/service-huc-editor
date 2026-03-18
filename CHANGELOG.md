# CHANGELOG

MvdP work on the service editor.

## 4-2-2026

After work on the stallings editor, integrate it in service-huc-editor. For now in the branch dev-history

## 22-1-2026

- failed addition of datatable listrecs.xsl should be helping
- TODO to make it work in Oxygen.. DONE
- TODO en discuss html does not change when you click on different links. 

test:

    http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3/history/1753883036
    http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3/history/1768393812

are all the same. But:
    http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3.xml/history/1753883036
    http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3.xml/history/1768393812

are not the same. in protected.py a html record is created on the basis of nr, prof and app. So that will be naturaly the most recent one.

    elif form == RecForm.html or "text/html" in request.headers.get("accept", ""):
        html = rec_html(app,prof,nr)
        call_record_hook("read_post",app,prof,nr,user)
        return HTMLResponse(content=html)

To test http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/1/history and click on records

- link in created html to single record
- Dockerfile optimization:copy dependency files first, code last
- content negotiation 
- table view, adapted xslt more suitable for PySaxonProcessor && Oxygen (parameters, named template, json2xml integrated in hitory2html)
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
