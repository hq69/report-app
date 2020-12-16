# report-app

This is a repo to convert salesforce report to csv (xls) file.

Written using python, selenium, angular js.
Hosted with ubuntu, nginx, and chrome environment.

1. nginx listens for requests
2. request parameters are sent to back-end script
3. script launches browser and does what script say
4. result is parsed into csv and put into download folder
