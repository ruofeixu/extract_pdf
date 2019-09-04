#!/usr/bin/env python3.5

import os
import re
import sys
import subprocess

from tqdm import tqdm
from joblib import Parallel, delayed
import argparse

from pdf2txtlib import convert_pdf_to_file

pdfbox = os.path.abspath(os.path.dirname(__file__))
pdfbox = os.path.join(pdfbox, 'pdfbox-app-2.0.4.jar')

import camelot
import json


def extract_tables(pdf_path):
    tables = camelot.read_pdf(pdf_path)
    table_list = []
    for table in tables:
        df = table.df
        table_json_obj = json.loads(df.to_json(orient='values'))
        # json_obj = {
        #     'page_num': table.page,
        #     'table_json': table_json_obj
        # }
        table_list.append(table_json_obj)
    return table_list


def convert_full(pdf_path, txt_path):
    json_path = txt_path.replace('.txt', '.json')
    cmd = 'java -jar "{}" ExtractText "{}" "{}"'
    c = cmd.format(pdfbox, pdf_path, txt_path)
    os.system(c)
    output_json = {
        'paragraphs': [],
        'tables': []
    }
    try:
        tables = extract_tables(pdf_path)
        output_json['tables'] = tables
        delimiter = " \n"
        with open(txt_path, "r") as paragraphs_file:
            all_content = paragraphs_file.read() #reading all the content in one step
            #using the string methods we split it
            paragraphs = all_content.split(delimiter)
            for paragraph in paragraphs:
                print('=================')
                print(paragraph)
                if paragraph == '':
                    continue
                output_json['paragraphs'].append(paragraph)
        
        print(output_json)
        with open(json_path, "w") as f:
            json.dump(output_json,f)

    except:
        cmd = 'rm {}'.format(txt_path)
        os.system(cmd)
    cmd = 'rm {}'.format(txt_path)
    os.system(cmd)

def listpdf(root, sub_path=[]):
    ret = []
    ppp = [root] + sub_path
    path = os.path.join(*ppp)
    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            file_path = os.path.join(path, f)
            if os.path.isdir(file_path):
                new_sub_path = sub_path.copy()
                new_sub_path.append(f)
                ret = ret + listpdf(root, new_sub_path)
            elif os.path.isfile(file_path):
                if f.endswith('.pdf'): # and re.match('\[600[12345]\d\d\]', f):
                    ret.append((sub_path, f))
    return ret

def main():
    parser = argparse.ArgumentParser(
        description='把某个文件夹的pdf转换到另一个文件夹'
    )
    parser.add_argument(
        '-s', '--source_dir',
        help='pdf文本文件源目录', type=str, required=True
    )
    parser.add_argument(
        '-d', '--dest_dir',
        help='输出的文件夹', type=str, required=True
    )
    parser.add_argument(
        '-n', '--n_threads',
        help='线程数', type=int, required=True, default=8
    )
    args = parser.parse_args()
    if not os.path.exists(args.source_dir):
        print('ERROR: pdf文件夹不存在', args.source_dir)
        exit(1)
    if not os.path.isdir(args.source_dir):
        print('ERROR: pdf文件夹不是文件夹', args.source_dir)
        exit(1)
    print('读取pdf文件')
    paths = listpdf(args.source_dir)
    print(len(paths), 'paths')
    full_paths = []
    for sub_path, f in paths:
        pdf_path = os.path.join(args.source_dir, *sub_path, f)
        txt_path = os.path.join(args.dest_dir, *sub_path, f.replace('.pdf', '.txt'))
        full_paths.append((pdf_path, txt_path))

    para_list = []
    full_para_list = []
    print(full_paths)
    for pdf_path, txt_path in full_paths:
        if os.path.exists(txt_path):
            continue
        dirpath = os.path.abspath(os.path.dirname(txt_path))
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        # para_list.append(delayed(convert)(pdf_path, txt_path))
        # full_para_list.append(delayed(convert_full)(pdf_path, txt_path.replace('.txt', '.full.txt')))
        para_list.append(delayed(convert_full)(pdf_path, txt_path))


    print('找到{}个转换任务'.format(len(para_list)))
    Parallel(n_jobs=args.n_threads, verbose=10)(para_list)
    Parallel(n_jobs=args.n_threads, verbose=10)(full_para_list)

if __name__ == '__main__':
    main()
