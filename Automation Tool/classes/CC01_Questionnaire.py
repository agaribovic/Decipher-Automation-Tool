import functions.function_test as fun
import classes.CC00_Helper as C00
import classes.CC02_Question as C02
import classes.CC05a_WordParagraph as WP
import classes.CC05b_WordTable as WT
from classes.CC07_xml_print import CC07XMLPrintQuest as C07Quest
from classes.CC07_xml_print import CC07XMLPrintGlobal as C07Global
from classes.CC07_xml_print import CC07XMLPrintAnswer as C07Answer
from classes.CC00_Helper import CO0Helper

from classes.CC03_Answer import CO3Answer as C03
from classes.CC00_Helper import CrawlState
from docx.text.paragraph import Paragraph
from docx.table import Table

import unicodedata
import re


class CO1Questionnaire:

    def __init__(self, name):

        self.EOFFilterDF = None
        self.name = name
        self.questColl = {}
        self.errorColl = []
        self.helper = C00.CO0Helper

        # Crawling Variables
        self.question_tmp = None
        self.start_crawl = False
        self.first_question_started = False
        self.block_text = None
        # What part we currently read: StateNone = 1 or Question = 2 or Answer = 3
        self.current_state = CrawlState.StateNone
        self.working_paragraph = None

    def set_working_paragraph(self, working_paragraph):

        self.working_paragraph = working_paragraph

    def docx_crawler(self, doc_input):

        for block in fun.iter_block_items(doc_input):

            if isinstance(block, Paragraph):

                if len(block.text.strip()) > 0:

                    if block.text.lower().find("[start]") >= 0:
                        self.start_crawl = True
                    if block.text.lower().find("[end]") >= 0:
                        self.start_crawl = False

                    if self.start_crawl:
                        self.working_paragraph = WP.WordParagraph(block, self)
                        self.crawl_conditions()

            elif isinstance(block, Table):

                if self.start_crawl:
                    WT.WordTable(block, self, self.question_tmp)

            else:

                print("Not a table, not a paragraph found")

    def crawl_conditions(self):

        first_word_begin_question = self.working_paragraph.first_word_begin_question
        first_word = self.working_paragraph.first_word
        word_paragraph_text_html = self.working_paragraph.word_paragraph_text_html
        first_word_begin_answer = self.working_paragraph.first_word_begin_answer
        first_word_begin_answer_number = self.working_paragraph.first_word_begin_answer_number

        if first_word_begin_question and self.start_crawl:
            self.current_state = CrawlState.Question
            self.first_question_started = True
            q_name = first_word
            replace_strings = [".", ":", ")", "("]
            for key in replace_strings:
                q_name = q_name.replace(key, "")
            self.question_tmp = C02.CO2Question(q_name)
            self.quest_coll_append(self.question_tmp)

        if first_word_begin_answer and self.start_crawl and self.first_question_started:
            answer_number = first_word_begin_answer_number
            self.current_state = CrawlState.Answer
            answer_tmp = C03(answer_number, word_paragraph_text_html)
            self.question_tmp.answer_coll_append(answer_number, answer_tmp, self)

        if self.current_state == CrawlState.Question:
            self.question_tmp.para_coll_app(word_paragraph_text_html)

        if self.current_state == CrawlState.Answer:
            self.current_state = CrawlState.StateNone

    def loop_and_find_orders(self):

        # Get Orders
        for q_name in self.questColl.keys():
            # print("quest=", pName)
            tmp_quest = self.questColl[q_name]
            self.find_orders(tmp_quest, q_name, 0, "question")
            for answer_loop in tmp_quest.answersDic.keys():
                # print("answer=", answer_loop)
                tmp_quest_answer = self.questColl[q_name].answersDic[answer_loop]
                self.find_orders(tmp_quest_answer, q_name, answer_loop, "answer")

        # Orders to DataFrame (call orders orders_df)
        for pName in self.questColl.keys():

            tmp_quest = self.questColl[pName]
            cnt_answers = len(tmp_quest.answersDic)
            self.orders_df(tmp_quest, tmp_quest.fil)
            tmp_quest.ordersLower = {key: value.lower() for key, value in tmp_quest.orders.items()}
            cnt_quest_orders = len(tmp_quest.orders)
            if "number" in tmp_quest.ordersLower.values() or "running sum" in tmp_quest.ordersLower.values():
                if cnt_answers > 1:
                    tmp_quest.orders[cnt_quest_orders + 1] = "display"
                    tmp_quest.orders[cnt_quest_orders + 2] = "rowLegend: left"
                else:
                    tmp_quest.orders[cnt_quest_orders + 1] = "rowLegend: right"
            cnt_quest_orders = len(tmp_quest.orders)
            if "amount" in tmp_quest.ordersLower.values() and "running sum" in tmp_quest.ordersLower.values():
                tmp_quest.orders[cnt_quest_orders + 1] = "prefill"
            tmp_quest.ordersLower = {key: value.lower() for key, value in tmp_quest.orders.items()}
            self.orders_df(tmp_quest, tmp_quest.fil)

            for answer_loop in tmp_quest.answersDic.keys():
                tmp_answer = tmp_quest.answersDic[answer_loop]
                self.orders_df(tmp_answer, tmp_answer.fil)
                tmp_answer.ordersLower = {key: value.lower() for key, value in tmp_answer.orders.items()}

    def find_orders(self, tmp_quest, q_name, answer, kind):

        # Search for the pattern "Brackets in Brackets" "[sz[sz]]"
        # working_string = '[test] test [test[]][wsz] ][[test]'
        # print(helper.find_orders(helper, working_string))

        working_string = ""
        for para in tmp_quest.paraCollection:
            working_string += "\n" + para  # para.text
        cnt_left = working_string.count('[')
        cnt_right = working_string.count(']')
        if cnt_left != cnt_right:
            tmp = "Number of left and right square brackets is not equal:: " + q_name + "::answerNumber::" + str(answer)
            self.errorColl.append(tmp)
            tmp_quest.errors.append(tmp)
            # quit("xd=" + working_string)
            return
        if cnt_left == 0:
            if working_string.lower().find('specify') > 0 and kind == "answer":
                tmp_quest.other_answer_specify(q_name, answer, self, 0)
                self.orders_df(tmp_quest, C03.fil)
            return

        # Check Brackets [] Inside Brackets []
        left_bracket = [m.start() for m in re.finditer('\[', working_string)]
        left_bracket_for_check = [m.start() for m in re.finditer('\[', working_string)]
        right_bracket = [m.start() for m in re.finditer(']', working_string)]
        left_bracket_for_check.pop(0)
        left_bracket_for_check.append(999999)
        brackets_in_brackets = any([(m - right_bracket[i - 1]) < 0 for i, m in enumerate(left_bracket_for_check, 1)])
        if brackets_in_brackets:
            tmp = "Brackets [] Inside Brackets []::Pitanje::" + q_name
            self.errorColl.append(tmp)
            tmp_quest.errors.append(tmp)
        if cnt_left != cnt_right or brackets_in_brackets:
            return
        between_brackets = [working_string[left_bracket[i - 1] + 1:right_bracket[i - 1]] for i, m in
                            enumerate(left_bracket, 1)]
        i = 0
        for potential_orders in between_brackets:
            potential_orders_orginal = potential_orders
            potential_orders = potential_orders.lower()
            i += 1
            term_tmp = ""
            if potential_orders.find('term') > -1:
                term_tmp = "terminate"
                if potential_orders.find('end') > 0 and (
                        potential_orders.find('at') > 0 or potential_orders.find('@') > 0):
                    term_tmp = "terminateatend"
            if term_tmp == "":
                tmp_quest.orders[i] = potential_orders_orginal
            else:
                tmp_quest.orders[i] = term_tmp

        if working_string.lower().find('specify') > 0 and kind == "answer":
            # print(q_name, answer, self, (i + 1))
            try:
                tmp_quest.other_answer_specify(q_name, answer, self, (i + 1))
            except:
                pass
        # self.orders_df(tmp_quest, fil)
        # tmp_quest.ordersLower = {key: value.lower() for key, value in tmp_quest.orders.items()}

    def print_all_errors(self):

        if len(self.errorColl) > 0:
            print()
            print("#########################")
            print("##### ERROR LIST #####")
            print()
        for text in self.errorColl:
            print(text)

    def orders_df(self, tmp_quest, fil):

        orders = tmp_quest.orders
        helper = C00.CO0Helper
        EOF = helper.elaborationOfFunctions
        self.EOFFilterDF = EOF
        exec("self.EOFFilterDF = EOF.loc[" + fil + "]")

        eof_filter_list = self.EOFFilterDF["answersAtributes"].tolist()

        orders_fun_dict = {fun_l: orders[ord_l] for fun_l in eof_filter_list for ord_l in orders.keys() if
                           orders[ord_l].lower().startswith(
                               str(fun_l).lower().strip())}  # .startswith(fun.lower().strip()) >= 0 # (Promjenu pratiti)
        orders_fun_dict = {ord_l: orders_fun_dict[ord_l].replace(ord_l, "").
            replace(ord_l.upper(), "").replace(ord_l.title(), "").replace(":", " ", 1).strip()
                           for ord_l in orders_fun_dict.keys()}
        orders_fun_list_key = [key for key in orders_fun_dict.keys()]
        orders_fun_list_value = [orders_fun_dict[key] for key in orders_fun_dict.keys()]

        self.EOFFilterDF = self.EOFFilterDF[self.EOFFilterDF.answersAtributes.isin(orders_fun_list_key)]
        tmp_quest.EOFFilterDF = self.EOFFilterDF

        tmp_quest.ordersFunListKey = orders_fun_list_key
        tmp_quest.ordersFunListValue = orders_fun_list_value

    def print_xml(self, helper):

        prn_global = C07Global(self)
        prn_global.print_xml_initial_functions()

        for q_name in self.questColl.keys():

            # print(q_name)
            # patch
            if not isinstance(q_name, str):
                continue

            if q_name.find('col') > 0:
                continue

            try:
                cond_value_previous = prn_quest.cond_value
            except:
                cond_value_previous = ""

            prn_quest = C07Quest(q_name, prn_global, cond_value_previous)

            orders_list = prn_quest.tmp_quest.ordersLower.values()
            if 'insert states' in orders_list or 'insert state' in orders_list:
                prn_quest.xml_print_insert_states("choice")
                prn_quest.tag_to_print = "select"

            if 'insert multi states' in orders_list or 'insert multi state' in orders_list:
                prn_quest.xml_print_insert_states("row")
                prn_quest.tag_to_print = "checkbox"

            sub = "vmax"
            max_res = [s for s in orders_list if sub in s]
            sub = "vmin"
            min_res = [s for s in orders_list if sub in s]
            max_min_value = ""
            sign = ""
            message = ""
            if max_res:
                print("answer.count=")
                print(prn_quest.tmp_quest.answersDic)
                max_min_value = max_res[0].replace("vmax:", "").capitalize()
                sign = " gt "
                message = "'Sum of all values can not be greater of: '"
            if min_res:
                max_min_value = min_res[0].replace("vmin:", "").capitalize()
                sign = " lt "
                message = "'Sum of all values can not be less then: '"
            if max_res or min_res:
                sub = "validate"
                val_res = [s for s in orders_list if sub in s]
                length = len(prn_quest.tmp_quest.ordersLower)
                if not val_res:  # prn_quest.tmp_quest.ordersLower.values():
                    prn_quest.tmp_quest.ordersLower[length+1] = "validate"

                prn_quest.validate_xml_addon = "if this.sum " + sign + max_min_value + ":"
                prn_quest.validate_xml_addon += "\n    error(" + message + " + str(" + max_min_value + "))"
                # self.tmp_quest = prn_global.questionnaire.questColl[q_name]

            if q_name.find('goto') > 0:
                prn_quest.xml_print_orders_goto()
                continue

            if q_name.find('exec') > 0:
                prn_quest.exec_state = 1

            if q_name.find('ter') > 0 and (not q_name[-1].isnumeric()):
                prn_quest.xml_print_question_terminate()
            else:
                prn_quest.cond_value = ""
            prn_quest.cond_value_py = ""

            # QUESTION attributes
            if prn_quest.tmp_quest.EOFFilterDF is not None:
                prn_quest.xml_print_tags_addition()

            # LOOPING ANSWERS
            if prn_quest.term_state == 0 and prn_quest.exec_state == 0:

                prn_quest.xml_print_header_title_question()
                if prn_quest.validate_xml_addon != "" or prn_quest.validate_xml != "":
                    prn_global.xml_string += "\n\t<validate>\n"
                    prn_global.xml_string += "\n" + prn_quest.validate_xml_addon
                    prn_global.xml_string += prn_quest.validate_xml
                    prn_global.xml_string += "\n\t</validate>"
                prn_global.xml_string += prn_quest.tag_add_print
                prn_quest.tag_row_to_print_state_remember = prn_quest.tag_row_to_print

                for answer_loop in prn_quest.tmp_quest.answersDic.keys():
                    prn_answer = C07Answer(prn_quest, answer_loop)
                    prn_answer.print_answer_attributes()

                if (str(q_name) + 'col') in self.questColl:
                    prn_quest.print_xml_column()

                prn_global.xml_string += prn_quest.insert_states_xml
                prn_global.xml_string += "\n</" + str(prn_quest.tag_to_print) + ">\n\n"

                at_end_hid_state = ""  # " and (QHidStage.r1)"
                term_number_tmp = prn_global.term_number
                at_end_char = ""
                if prn_quest.term_answer != "":
                    if prn_quest.term_at_end_answer != "":
                        term_number_tmp -= 1
                    prn_quest.xml_print_answer_terminate(term_number_tmp, at_end_hid_state, prn_quest.term_answer,
                                                         at_end_char)
                if prn_quest.term_at_end_answer != "":
                    at_end_char = "@end"
                    term_number_tmp = prn_global.term_number
                    at_end_hid_state = " and (QHidStage.r2)"  # " and (QHidStage.r1(2))"
                    prn_quest.xml_print_answer_terminate(term_number_tmp, at_end_hid_state, prn_quest.term_at_end_answer
                                                         , at_end_char)
            elif prn_quest.term_state == 1:

                tmp0 = prn_quest.tmp_quest.answersDic
                tmp1 = list(tmp0.keys())
                try:
                    tmp2 = tmp0[tmp1[0]]
                except:
                    tmp2 = ""
                    print(q_name + ": Terminate tag is not list")
                prn_quest.xml_print_answer_terminate(prn_global.term_number, prn_quest.at_end_hid_state,
                                                     C07Global.string_bracket_pipe(tmp2.paragraph, tmp2),
                                                     prn_quest.at_end_char)
            elif prn_quest.exec_state == 1:

                prn_quest.xml_print_execute()
            prn_quest.xml_print_classify()

            prn_global.xml_string += "\n<suspend/>\n"
            prn_global.xml_string += prn_quest.classify_text
            prn_global.xml_string += prn_quest.post_question

        helper.f3.write("\n  ------------  \n")
        helper.f3.write(prn_global.term_condition)
        helper.f3.write("\n  ------------  \n\n")
        helper.f3.write(prn_global.term_row)
        helper.f3.write("\n  ------------  \n\n")

        prn_global.xml_string = "".join([char for char in prn_global.xml_string if not CO1Questionnaire.is_pua(char)])
        # print(xml_print)
        helper.f3.write(prn_global.xml_string)

    @staticmethod
    def replace_strings_fun(working_string):

        for key in CO0Helper.replaceDictionary:
            tmp = CO0Helper.replaceDictionary[key]
            working_string = working_string.replace(key, tmp)
        working_string = CO0Helper.email_format(working_string)
        return working_string

    def print_all_questionnaire(self):

        for pName in self.questColl.keys():
            tmp_quest = self.questColl[pName]
            for paraText in tmp_quest.paraCollection:
                print("TITLE=", paraText)
            for order in tmp_quest.orders.keys():
                pass
                # print("ORDER=", tmp_quest.orders[order])
            # print("DF=", tmp_quest.EOFFilterDF)
            for answer_loop in tmp_quest.answersDic.keys():
                tmp_answer = tmp_quest.answersDic[answer_loop]
                print("ANSWER=", answer_loop + "=" + tmp_answer.paragraph)
                # for order in tmp_answer.orders.keys():
                #     print("ORDER=", tmp_answer.orders[order])
                # print("DF=", tmp_answer.EOFFilterDF)

    def quest_coll_append(self, question_tmp):

        if question_tmp.pName not in self.questColl:
            self.questColl[question_tmp.pName] = question_tmp
        else:
            self.errorColl.append("Duplicate question name:" + question_tmp.pName)

    @staticmethod
    def is_pua(c):
        return unicodedata.category(c) == 'Co'
