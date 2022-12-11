import functions.setting_test as sett
from docx import Document
import win32com.client as win32
import os
from shutil import copyfile
import shutil
import pandas as pd
import re
from enum import Enum


class CO0Helper:

    errorColl = []

    # Description of the Program (SW) Features
    elaborationOfFunctions = pd.read_excel(sett.fileRootProjects + "//" + sett.FileExcelName)
    EOF = elaborationOfFunctions

    # Dictionaries of US States and Alphabet
    EOF_other_sheets = pd.ExcelFile(sett.fileRootProjects + "//" + sett.FileExcelName)

    states_sheet = pd.read_excel(EOF_other_sheets, 'states')
    statesDict = dict(zip(states_sheet.number, states_sheet.label))  # {1: ' Alabama', 2: ' Alaska', ...

    alphabet_sheet = pd.read_excel(EOF_other_sheets, 'alphabet')
    alphabet = dict(zip(alphabet_sheet.number, alphabet_sheet.label))  # {'a': 1, 'b': 2, 'c': 3, 'd': 4,

    template_variables_sheet = pd.read_excel(EOF_other_sheets, 'template_variables')
    template_variables = dict(zip(template_variables_sheet.number, template_variables_sheet.variable))

    replaceDictionary = {
        "& ": "&amp; ", " > ": "&gt;", " < ": "&lt;", "\t": "",
        "’": "'", "“": "\"", "PIPE:": "pipe:",
        "_": "", '("<': '("&lt;', "('<": "('&lt;",
        '(">': '("&gt;', "('>": "('&gt;", "(‘": "(\"", "('": "(\"",
        "‘)": "\")", "')": "\")", "": "", "": ""
    }  # , "‘": "\"" , "'": "\""

    def __init__(self):

        self.f1 = None  # TEMP.docx file
        self.f2 = None  # not in use any more (it was OUTPUT.docx)
        self.f3 = None  # The Result as XML file = (PROJECT NAME)_programming.docx.xml
        self.docInput = None  # same as f1
        self.insertStatesXML = self.insert_states("choice")

    @staticmethod
    def preparation_of_temp_file():

        # preparation_of_temp_file: We will make a copy of the Word project file.
        # The name of the project file that we are working is like (PROJECT NUMBER)_programming
        # and we make copy "TEMP.docx" and than run Excel Macro that converts Word number list into
        # regular number. Python than works with "TEMP.docx" and original file is intact.

        # Opening an Word Macro File:
        # Intention is to ran Word Macro "ActiveDocument.ConvertNumberToText" at TEMP.docx file
        # Python can not read Word list numeration (that is way we have to run WORD Macro firstly)
        try:
            word_app = win32.gencache.EnsureDispatch("Word.Application")
        except:
            shutil.rmtree(sett.pythonTempFile)
            word_app = win32.gencache.EnsureDispatch("Word.Application")

        word_app.Visible = True
        doc_path_working_file = sett.fileRoot + "//" + sett.FileName
        doc_path_macro = sett.fileRoot + "//" + sett.FileNameMacro
        doc_path_temp = sett.fileRoot + "//" + sett.TempFIleName

        # Closing TEMP file if it is open
        try:
            doc_temp = word_app.Documents.Open(doc_path_temp)
            doc_temp.Close()
        except:
            pass

        # Removing TEMP file from the disk
        if os.path.exists(sett.fileRoot + "//" + sett.TempFIleName):
            os.remove(sett.fileRoot + "//" + sett.TempFIleName)

        # Opening Word Macro file
        doc_macro = None
        try:
            doc_macro = word_app.Documents.Open(doc_path_macro)
        except:
            exit("Word Macro could not open. Close all Microsoft Word Documents and try again.")

        # Opening and saving working file
        doc = None
        try:
            doc = word_app.Documents.Open(doc_path_working_file)
        except:
            print(doc_path_working_file)
            exit("Path to project folder or document is not good")
        doc.Save()

        # Copy of working file into TEMP.docx and opening of TEMP.docx
        copyfile(sett.fileRoot + "//" + sett.FileName, sett.fileRoot + "//" + sett.TempFIleName)
        doc_temp = word_app.Documents.Open(doc_path_temp)

        # Running Word Macro file on TEMP.docx
        word_app.Run("Normal.bbhelpFunctions.ConvertListToNumber")
        doc_temp.Save()
        doc_temp.Close()
        doc_macro.Close()

    def open_doc(self):

        file_path_out = sett.fileRoot + "//" + sett.FileName + ".xml"
        self.f1 = open(sett.fileRoot + "//" + sett.TempFIleName, 'rb')
        self.docInput = Document(self.f1)
        self.f3 = open(file_path_out, "w+", encoding='utf-8')

    def close_save_doc(self):

        self.f1.close()
        self.f3.close()
        if os.path.exists(sett.fileRoot + "//" + sett.TempFIleName):
            os.remove(sett.fileRoot + "//" + sett.TempFIleName)

    @staticmethod
    def number_candidate(candidate):

        replace_strings = [".", "\t", " ", ")", "(", ""]
        for key in replace_strings:
            candidate = candidate.replace(key, "")

        if candidate in CO0Helper.alphabet:
            candidate = str(CO0Helper.alphabet[candidate.lower()])

        return candidate

    @staticmethod
    def email_format(text):

        # regex for email
        reg_pat = r'\S+@\S+\.\S+'
        emails = re.findall(reg_pat, text, re.IGNORECASE)

        for email in emails:
            text = text.replace(email,
                                '<a href="mailto:' + email + '" target="_blank" rel="noopener">' + email + '</a>')

        # regex for html
        reg_pat = r'[S+]?www.\S+'
        webs = re.findall(reg_pat, text, re.IGNORECASE)
        for web in webs:
            text = text.replace(web,
                                '<a href="' + web + '" target="_blank" rel="noopener">' + web + '</a>')
        return text


class CrawlState(Enum):
    StateNone = 1
    Question = 2
    Answer = 3
