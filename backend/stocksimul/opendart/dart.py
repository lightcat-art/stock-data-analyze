# -*- coding:utf-8 -*-
# 2020 FinanceData.KR http://financedata.kr fb.com/financedata

import requests
import zipfile
import os
import io
import glob
import json
import pandas as pd
import warnings
import xml.etree.ElementTree as ET
from datetime import datetime
from . import dart_search
from . import dart_report
from . import dart_finstate
from . import dart_share
from . import _utils

try:
    from pandas import json_normalize
except ImportError:
    from pandas.io.json import json_normalize


class OpenDartReader():
    # init corp_codes (회사 고유번호 데이터)
    def __init__(self, api_key):
        # create cache directory if not exists
        docs_cache_dir = 'docs_cache'
        if not os.path.exists(docs_cache_dir):
            os.makedirs(docs_cache_dir)

        # read and return document if exists
        fn = 'opendartreader_corp_codes_{}.pkl'.format(datetime.today().strftime('%Y%m%d'))
        fn_cache = os.path.join(docs_cache_dir, fn)
        for fn_rm in glob.glob(os.path.join(docs_cache_dir, 'opendartreader_corp_codes_*')):
            if fn_rm == fn_cache:
                continue
            os.remove(fn_rm)
        if not os.path.exists(fn_cache):
            df = dart_search.corp_codes(api_key)
            df.to_pickle(fn_cache)

        self.corp_codes = pd.read_pickle(fn_cache)
        self.api_key = api_key

    # 2. 사업보고서
    def report(self, corp, key_word, bsns_year, reprt_code='11011'):
        corp_code = self.find_corp_code(corp)
        return dart_report.report(self.api_key, corp_code, key_word, bsns_year, reprt_code)

    # 3-1. 상장기업 재무정보 (단일회사)
    # 3-2. 상장기업 재무정보 (다중회사)
    def finstate(self, corp, bsns_year, reprt_code='11011'):
        if ',' in corp:
            code_list = [self.find_corp_code(c.strip()) for c in corp.split(',')]
            corp_code = ','.join(code_list)
        else:
            corp_code = self.find_corp_code(corp)
        return dart_finstate.finstate(self.api_key, corp_code, bsns_year, reprt_code)

    # 3-3. 재무제표 원본파일(XBRL)
    def finstate_xml(self, rcp_no, save_as):
        return dart_finstate.finstate_xml(self.api_key, rcp_no, save_as=save_as)

    # 3-4. 단일회사 전체 재무제표
    def finstate_all(self, corp, bsns_year, reprt_code='11011', fs_div='CFS'):
        corp_code = self.find_corp_code(corp)
        return dart_finstate.finstate_all(self.api_key, corp_code, bsns_year, reprt_code=reprt_code, fs_div=fs_div)

    # 3-5. XBRL 표준계정과목체계(계정과목)
    def xbrl_taxonomy(self, sj_div):
        return dart_finstate.xbrl_taxonomy(self.api_key, sj_div=sj_div)

    # 4-1. 지분공시 - 대량보유 상황보고
    def major_shareholders(self, corp):
        corp_code = self.find_corp_code(corp)
        return dart_share.major_shareholders(self.api_key, corp_code)

    # 4-2. 지분공시 - 임원ㆍ주요주주 소유보고
    def major_shareholders_exec(self, corp):
        corp_code = self.find_corp_code(corp)
        return dart_share.major_shareholders_exec(self.api_key, corp_code)

    # utils: list_date 특정 날짜의 공시보고서 전체 (deprecated)
    def list_date(self, date=None, final=True, cache=True):
        warnings.warn('list_date() is deprecated. list_date_ex()를 사용하세요')

    # utils: list_date_ex 특정 날짜의 공시보고서 전체 데이터프레임 (시간포함)
    def list_date_ex(self, date=None, cache=True):
        return _utils.list_date_ex(date, cache=cache)

    # utils: attach files file list: 첨부파일 목록정보를 데이터프레임
    def attach_file_list(self, s):
        return _utils.attach_file_list(s)

    # utils: attach document list: 첨부문서의 목록정보(제목, URL)을 데이터프레임
    def attach_doc_list(self, s, match=None):
        return _utils.attach_doc_list(s, match=match)

    # utils: subdocument list: 하위 문서 목록정보(제목, URL)을 데이터프레임
    def sub_docs(self, s, match=None):
        return _utils.sub_docs(s, match=match)

    # utils: url 을 fn 으로 저장
    def retrieve(self, url, fn):
        return _utils.retrieve(url, fn)
