#!/usr/bin/env python3

import os
import re
import json
import uuid
import time
import shutil
import tempfile
import subprocess

def convert_pdf(path, first=0, last=9999):
    tempdir = tempfile.gettempdir()
    temp_path = os.path.join(tempdir, str(uuid.uuid4()))
    pdf_path = os.path.join(temp_path, 'a.pdf')
    html_path = os.path.join(temp_path, 'a-html.html')

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    shutil.copy(path, pdf_path)

    cmd = [
        'pdftohtml',
        '-f', # 起始页面
        '{}'.format(first),
         '-l', # 结束页面
         '{}'.format(last),
         '-wbt', # 空格宽度，40%个字符宽度
         '40',
         '-c', # 复杂html
         '-s', # 单个html
         '-i', # 不要图片
         '-q', # 安静模式，不输出错误
         '"{}"'.format(pdf_path)
    ]
    try:
        subprocess.check_output(
            ' '.join(cmd),
            shell=True
        )
        content = ''
        wait = 0
        while not os.path.exists(html_path):
            time.sleep(0.01)
            wait += 1
            if wait > 1000:
                return ''
        with open(html_path) as fp:
            content = fp.read()
    except:
        content = ''
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    return content

def read_styles(raw_content):
    styles_list = re.findall(r'\s+\.([^\{]+)\{([^\}]+)\}', raw_content)
    ret = {}
    for name, content in styles_list:
        # if len(name) > 10:
        #     continue
        obj = {}
        m = re.match(r'.*font-size:([\-\d]+)px.*', content)
        if m:
             obj['size'] = int(m.group(1))
        m = re.match(r'.*font-family:([^;]+);.*', content)
        if m:
             obj['family'] = m.group(1)
        m = re.match(r'.*color:(#[^;]+);.*', content)
        if m:
             obj['color'] = m.group(1)
        if 'transform' in content:
            obj['transform'] = True
        else:
            obj['transform'] = False
        ret[name] = obj
    return ret

def read_paragraphs(raw_content, styles):
    ret = []
    each_pages = [x for x in raw_content.split('<!DOCTYPE html>') if len(x) > 1]
    base_height = 0
    for page_index, each_page in enumerate(each_pages):
        m = re.findall(r'<div id="page[^>]+>', each_page)
        page_height = None
        page_width = None
        if m:
            m = m[0]
            mm = re.match(r'.*height:([\-\d]+)px.*', m)
            if mm:
                page_height = int(mm.group(1))
            mm = re.match(r'.*width:([\-\d]+)px.*', m)
            if mm:
                page_width = int(mm.group(1))
        else:
            continue
        if not page_height or not page_width:
            continue
        paragraph_list = re.findall(
            r'<p style="([^"]+)" class="([^"]+)">(.+)</p>',
            each_page
        )
        for para_style, para_class, content in paragraph_list:
            obj = {}
            m = re.match(r'.*top:([\-\d]+)px.*', para_style)
            if m:
                obj['top'] = int(m.group(1)) + base_height
            m = re.match(r'.*left:([\-\d]+)px.*', para_style)
            if m:
                obj['left'] = int(m.group(1))
            if para_class and para_class in styles:
                for k, v in styles[para_class].items():
                    obj[k] = v

            content = content.replace('<b>', ' ')
            content = content.replace('</b>', ' ')
            content = content.replace('<i>', ' ')
            content = content.replace('</i>', ' ')
            content = content.replace('<br/>', ' ')
            content = content.replace('&#160;', ' ')
            obj['content'] = content
            obj['base_height'] = base_height
            obj['page'] = page_index
            obj['page_height'] = page_height
            obj['page_width'] = page_width

            ret.append(obj)
        base_height += page_height
    return ret

def convert_pdf_to_content(path, first=0, last=9999):
    raw_content = convert_pdf(path, first=first, last=last)
    styles = read_styles(raw_content)
    paragraphs = read_paragraphs(raw_content, styles)
    def is_visible(para):
        if 'size' in para and para['size'] <= 0:
            return False
        if 'color' in para and para['color'] == '#ffffff':
            return False
        if 'transform' in para and para['transform']:
            return False
        return True
    visible_paragraphs = []
    for para in paragraphs:
        if is_visible(para):
            visible_paragraphs.append(para)
    lines = []
    last_para = None
    for para in visible_paragraphs:
        if last_para is None:
            last_para = [para]
        else:
            if abs(last_para[-1]['top'] - para['top']) <= 3:
                last_para.append(para)
            else:
                lines.append(' '.join([x['content'] for x in last_para]))
                last_para = [para]
    if last_para:
        lines.append(' '.join([x['content'] for x in last_para]))
    return '\n'.join(lines)

def convert_pdf_to_file(path, output_path, first=0, last=9999):
    content = convert_pdf_to_content(path, first=first, last=last)
    with open(output_path, 'w') as fp:
        fp.write(content)

def main():
    path = 'a.pdf'
    content = convert_pdf_to_content(path)
    print(content)

if __name__ == '__main__':
    main()
