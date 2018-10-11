#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2018 Raphael Hussung

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from twill.commands import *
from BeautifulSoup import BeautifulSoup
import re
from cStringIO import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import Charset
from email.generator import Generator

import configparser
config = configparser.ConfigParser()
config.read('cred.conf')

def get_url_from_text(link_text):
    links = showlinks()
    for i,l in enumerate(links):
        if link_text in l[0]:
           return l[1]

def get_url_from_title(link_title):
    soup = BeautifulSoup(show())
    for link in soup.findAll('a', attrs={'title': re.compile(link_title)}):
        url = link.get('href') 
        return url

def clean_str(string):
    ret_str = string.replace('\n', '')
    ret_str = ret_str.replace('\t', '')
    ret_str = ret_str.replace('  ', '')
    ret_str = ret_str.replace('&nbsp;', '')
    ret_str = re.sub('^ ', '', ret_str)
    return ret_str

def get_index_by_value(list, value):
    for i,l in enumerate(list):
        if l == value:
            return i
    return False
	    
	
qis_login = config['QIS']['matrikelnummer']
qis_pw = config['QIS']['password']
	
go('https://qis.verw.uni-kl.de')
fv("1", "asdf", qis_login)
fv("1", "fdsa", qis_pw)
submit('0')

go(get_url_from_text(u'Prüfungsverwaltung'))

go(get_url_from_text('Notenspiegel'))

# Get master grades
mode = config['QIS']['mode']
go(get_url_from_title(".*" + mode + ".*"))

table_html = show()
bs = BeautifulSoup(table_html)
grade_table = bs.findAll('table')[1]

values = []
# extract data
for i,row in enumerate(grade_table.findAll('tr')):
    # in row[0] is no data we're interested
    if i == 1:
        titles = [clean_str(title.string) for title in row.findAll('th')]
    if i > 1:
        lines = row.findAll('td', attrs={'class': re.compile(".*tabelle1.*")})
        if lines:
            values_i = [clean_str(line.string) for line in lines]
            values.append(values_i)
print values
results = {}
for i,t in enumerate(titles):
    results[t] = [v[i] for v in values]

print results
pruef_nr = results[u'Prüfungsnr.']

f = open('last_state.hist', 'r+')
old_pruef_nr = f.readlines()
for i,opn in enumerate(old_pruef_nr):
    old_pruef_nr[i] = clean_str(opn)
print pruef_nr
print old_pruef_nr
diffs = [pn for pn in pruef_nr if pn not in old_pruef_nr]
print diffs
new_indices = []
for d in diffs:
    new_indices.append(get_index_by_value(pruef_nr, d))

new_results = {}
for i,t in enumerate(titles):
    new_results[t] = [v[i] for j,v in enumerate(values) if j in range(len(values))]
print "New"
print new_results
for pn in diffs:
    f.write(pn + u'\n')
f.close()

head_css = u"""\
<html><body style="
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
.tg .tg-5kal{background-color:#3166ff;border-color:#3166ff;vertical-align:top}
.tg .tg-us36{border-color:inherit;vertical-align:top}
.tg .tg-mgml{font-weight:bold;background-color:#9698ed;color:#ffffff;border-color:#000000;vertical-align:top}
">
<table style="border-collapse:collapse;border-spacing:0;">
  <tr>"""
for t in titles:
     head_css += u"""<th class="tg-mgml">""" + t + u"""</th>"""
u"""</tr>"""
for i, d in enumerate(diffs):
    head_css += u"""<tr>"""
    for t in titles:
        head_css += u"""<td style="tg-yw4l">""" + new_results[t][i] + u"""</td>"""
    head_css += u"""</tr>"""
    
head_css += u"""</table></body></html>"""

# send mail
if diffs:
    import smtplib
    email_login = config['EMAIL']['email-address']
    email_pw = config['EMAIL']['password']
    email_smtp = config['EMAIL']['smtp']
    email_smtp_port = config['EMAIL']['port']
    server = smtplib.SMTP(email_smtp, email_smtp_port)
    server.starttls()
    server.login(email_login, email_pw)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "%s" % Header("Noten", 'utf-8')
    htmlpart = MIMEText(head_css, 'html', 'UTF-8')
    textpart = MIMEText("test", 'plain', 'UTF-8')
    msg.attach(htmlpart)
    #msg.attach(textpart)
    
    server.sendmail(email_login, email_login, msg.as_string())
    server.quit()
