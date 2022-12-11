from classes.CC00_Helper import CO0Helper as C00
from abc import ABC
import re


class Paragraph(ABC):
    replaceDictionary = {
        "& ": "&amp; ", " > ": "&gt;", " < ": "&lt;", "\t": " ",
        "’": "'", "“": "\"", "PIPE:": "pipe:",
        "_": "", '("<': '("&lt;', "('<": "('&lt;",
        '(">': '("&gt;', "('>": "('&gt;", "(‘": "(\"", "('": "(\"",
        "‘)": "\")", "')": "\")", "": "", "": ""
    }  # , "‘": "\"" , "'": "\""

    def __init__(self, word_paragraph_text):

        self.word_paragraph_text = word_paragraph_text
        self.first_word = ""
        self.first_word_fun()
        self.first_word_begin_question = False
        self.first_word_begin_question_fun()
        self.first_word_begin_answer = False
        self.first_word_begin_answer_number = 0
        self.first_word_begin_answer_fun()
        self.word_paragraph_text_html = word_paragraph_text

    def first_word_fun(self):

        try:
            self.first_word = self.word_paragraph_text.split()[0]
        except:
            self.first_word = self.word_paragraph_text

    def first_word_begin_question_fun(self):

        # New question condition equals:
        # First word: contains number and Dot at last place
        # (e.g. S1. or S1) or S1: or SA.)

        # isalpha()= True if all the characters are alphabet letters(a - z)
        # u1 = First Letter of first word is letter(isalpha
        # if needed below code count UPPERCASE in first_word
        # import re
        # REGEX = re.compile(r'[A-Z]')
        # len(REGEX.findall(self.first_word))

        # print("fw=", self.first_word)
        try:
            u1 = self.first_word[0].isalpha()
            u2 = any(char.isdigit() for char in self.first_word)
            # u3a = self.first_word[-1].find(".") != -1
            # u3b = self.first_word[-1].find(")") != -1
            # u3c = self.first_word[-1].find(":") != -1

            # OLD CODE: e.g. COUNTRY. should start question
            # u4 = self.first_word[0:-2].isupper()
            # u5 = self.first_word[0:-2].isalpha()

            if u1 and u2:  # and (u3a or u3b or u3c):
                self.first_word_begin_question = True
        except:
            pass

    def first_word_begin_answer_fun(self):

        candidate = self.first_word
        replace_strings = [".", ":", "\t", " ", ")", "(", ""]
        for key in replace_strings:
            candidate = candidate.replace(key, "")

        if candidate in C00.alphabet:
            candidate = str(C00.alphabet[candidate.lower()])

        if candidate.isnumeric():
            self.first_word_begin_answer = True
            self.first_word_begin_answer_number = candidate

    def replace_strings_fun(self):

        for key in Paragraph.replaceDictionary:
            tmp = Paragraph.replaceDictionary[key]
            self.word_paragraph_text_html = self.word_paragraph_text_html.replace(key, tmp)

    def email_format(self):

        text = self.word_paragraph_text_html
        # regex for email
        reg_pat = r'\S+@\S+\.\S+'
        emails = re.findall(reg_pat, text, re.IGNORECASE)

        for email in emails:
            email = email.strip()
            if email[-1] == "." or email[-1] == ",":
                email = email[:-1]
            text = text.replace(email,
                                '<a href="mailto:' + email.strip() + '" target="_blank" rel="noopener">'
                                                                     '<span style="color:blue;">' + email.strip() +
                                '</span></a>')

        # regex for html
        reg_pat = r'[https://]?[S+]?www.\S+'  #
        webs = re.findall(reg_pat, text, re.IGNORECASE)
        for web in webs:
            # print("web=", web)
            if web[-1] == "." or web[-1] == ",":
                web = web[:-1]
            https_text = ""
            if web.find("https://") == -1:
                https_text = "https://"
            text = text.replace(web,
                                '<a href="' + https_text + web.strip() + '" target="_blank" rel="noopener">'
                                                                         '<span style="color:blue;">' + web.strip()
                                + '</span></a>')
        self.word_paragraph_text_html = text


class WordParagraph(Paragraph):

    def __init__(self, word_paragraph, questionnaire):

        self.questionnaire = questionnaire
        self.word_paragraph = word_paragraph
        super().__init__(word_paragraph.text)
        self.paragraph_to_html()
        self.replace_strings_fun()
        self.email_format()

    def paragraph_to_html(self):

        # input: paragraph (type paragraph)
        # output: (bold_state: number, para_text: string)
        # para_text: Which is your <b><u>speciality</u></b>?

        debug = 0
        # not bolding if already contains tags <b> or <u>
        if any(substring in self.word_paragraph_text for substring in ["<b>", "<u>"]):
            return
        # not bolding termination and exec question
        if self.questionnaire.first_question_started and \
                not self.first_word_begin_question and \
                (self.questionnaire.question_tmp.pName.find('ter') > 0 or
                 self.questionnaire.question_tmp.pName.find('exec') > 0):
            return
        if self.questionnaire.first_question_started and \
                not self.first_word_begin_question and \
                (self.word_paragraph_text.find('[') >= 0 and
                 self.word_paragraph_text.find(']') >= 0):
            return

        if self.first_word_begin_question or self.first_word_begin_answer:
            shift_right = len(self.first_word)
        else:
            shift_right = 0

        bold_state = 0
        under_state = 0
        para_text = ""
        para_text_clean = ""
        run_count = 0
        for run in self.word_paragraph.runs:
            if debug:
                print(run.text)
            run_count = run_count + 1
            para_text_clean += run.text
            if (len(para_text_clean) <= len(self.first_word)) and run_count > 1:
                if debug:
                    print("usao")
                para_text += run.text
                continue
            post_html = ""
            pre_html = ""
            if run.bold:
                bold_state += 1
                pre_html = "<b>"
                post_html = "</b>"
            if run.underline:
                under_state += 1
                pre_html += "<u>"
                post_html = "</u>" + post_html
            if len(run.text.strip()) == 0:
                pre_html = ""
                post_html = ""
            if run_count == 1 and 0 < shift_right < len(run.text):
                if shift_right > 0:
                    shift_right += len(pre_html) + len(post_html)
                para_text += self.first_word + " " + pre_html + run.text[shift_right + 1:] + post_html
                shift_right = 0
            else:
                para_text += pre_html + run.text + post_html
        if run_count != bold_state:
            reg_pat = r'<b>( )*</b>|</b>( )*<b>'
            self.word_paragraph_text_html = re.sub(reg_pat, " ", para_text)
        # patch - it could be better solved
        # if first_word only in the paragraph add there is no space at the end
        # then add one space
        if self.first_word_begin_question or self.first_word_begin_answer:
            try:
                temp_first_word = self.word_paragraph_text_html.split()[0]
            except:
                temp_first_word = self.word_paragraph_text_html
            if len(temp_first_word) == len(self.word_paragraph_text_html):
                self.word_paragraph_text_html += " "
        # patch - it could be better solved
        patch_replace = ["<b>T</b>ERM", "<b>TE</b>RM", "<b>TER</b>M"]

        for keyTmp in patch_replace:
            self.word_paragraph_text_html = self.word_paragraph_text_html.replace(keyTmp, "TERM")

        patch_replace = ["<b>t</b>erm", "<b>te</b>rm", "<b>ter</b>m"]

        for keyTmp in patch_replace:
            self.word_paragraph_text_html = self.word_paragraph_text_html.replace(keyTmp, "term")

# It was not used
class TableParagraph(Paragraph):

    def __init__(self, word_paragraph_text):
        super().__init__(word_paragraph_text)
        self.replace_strings_fun()
        self.email_format()

    def paragraph_to_html(self):
        pass
