from pandas import isnull
from classes.CC00_Helper import CO0Helper
import functions.setting_test as sett
import re


class CC07XMLPrintGlobal:

    def __init__(self, questionnaire):

        self.term_number = sett.TerminateStarter - 1
        self.term_condition = ""
        self.term_row = ""
        self.xml_string = ""
        self.questionnaire = questionnaire

    def print_xml_initial_functions(self):

        # Open End Min Checking Function. Use example: [oemin: 5]
        self.xml_string += "\n<res label='errOEMin'>Please enter more text.</res>"
        self.xml_string += "\n<exec when='init'>"
        self.xml_string += "\n# Checking OE='Open End' Question Length"
        self.xml_string += "\n# [oemin: 5]"
        self.xml_string += "\ndef OEMinChk(strChk, maxOE):"
        self.xml_string += "\n	if len(str(strChk.val)) lt maxOE:"
        self.xml_string += "\n		error(res.errOEMin)"
        self.xml_string += "\n</exec>\n"

    @staticmethod
    def string_bracket_pipe(working_string, obj):

        # print("working_string=", working_string)
        if len(obj.errors) > 0 or working_string.strip() == "":
            return CC07XMLPrintGlobal.replace_strings(working_string).strip()
        first_word = working_string.split()[0]
        # start() function finds match in regular expressions
        left_bracket = [m.start() for m in re.finditer('\[', working_string) if
                        not working_string[m.start():m.start() + 6] == "[pipe:"]
        if len(left_bracket) == 0:
            return (working_string[len(first_word) + 1:99999]).strip()
        beginning = working_string[len(first_word) + 1:left_bracket[0]]
        right_bracket = [m + working_string[m:].find("]") for m in left_bracket]

        left_bracket.pop(0)
        left_bracket.append(999999)
        working_string = ''.join(
            [working_string[right_bracket[i - 1] + 1: left_bracket[i - 1]] for i, m in enumerate(left_bracket, 1)])
        # print("result=", (beginning + " " + working_string).strip())
        return (beginning + " " + working_string).strip()

    @staticmethod
    def replace_strings(working_string):

        for key in CO0Helper.replaceDictionary:
            tmp = CO0Helper.replaceDictionary[key]
            working_string = working_string.replace(key, tmp)
        working_string = CO0Helper.email_format(working_string)
        return working_string


class CC07XMLPrintQuest:

    classify_dic = ['tag as', 'classify as', 'code as', 'continue as', 'label as', 'define as']

    def __init__(self, q_name, prn_global, cond_value_previous):

        self.at_end_char = ""
        self.at_end_hid_state = ""  # " and (QHidStage.r1)"
        self.attributes_quest_to_print = ""
        if q_name.find('ter') > 0:
            self.cond_value = cond_value_previous
        else:
            self.cond_value = ""
        self.cond_value_py = ""
        self.exec_state = 0
        self.insert_states_xml = ""
        self.post_question = ""
        self.q_name = q_name
        self.prn_global = prn_global
        self.tag_add_print = ""
        self.tag_to_print = "radio"
        self.tag_row_to_print = "row"
        self.term_state = 0
        self.title_simple = ""
        self.title_simple_py = ""
        self.tmp_quest = prn_global.questionnaire.questColl[q_name]
        self.validate_xml = ""
        self.validate_xml_addon = ""
        self.xml_states = ""
        self.xml_exclusive = ""
        self.xml_print_title_simple()
        self.classify_text = ""

        # Looping Answers
        self.classify_remember_dic = {}
        self.group_set = False
        self.term_answer = ""
        self.term_at_end_answer = ""
        self.tag_row_to_print_state_remember = ""
        self.group_set_label = ""

    def xml_print_orders_goto(self):

        goto_cond = ""
        goto_target = ""
        for key, order in self.tmp_quest.orders.items():
            if order.find('cond') > -1:
                goto_cond = order[5:].strip()
            if order.find('target') > -1:
                goto_target = order[7:].strip()

        self.prn_global.xml_string += "\n<goto target = '" + goto_target + "' cond = '" + goto_cond + "'/>\n"

    def xml_print_tags_addition(self):

        for index, row in self.tmp_quest.EOFFilterDF.iterrows():

            # print("index, row:", index, row)
            left_bracket = ""
            right_bracket = ""
            answers_attributes = row['answersAtributes']
            if row['addTag'] != "" and not isnull(row['addTag']):
                indx = self.tmp_quest.ordersFunListKey.index(answers_attributes)
                add_tag_value = self.tmp_quest.ordersFunListValue[indx]
                self.tag_add_print += "\n\t<" + row['addTag'] + ">" + str(add_tag_value) + "</" + row['addTag'] + ">"

            if row['tag'] != "" and not isnull(row['tag']):
                self.tag_to_print = row['tag']

            if row['rowTag'] != "" and not isnull(row['rowTag']):
                self.tag_row_to_print = row['rowTag']

            if row['colon(:)'] == 1 and not isnull(row['colon(:)']) and not isnull(row['colonCommand']):
                answers_attributes = row['answersAtributes']
                indx = self.tmp_quest.ordersFunListKey.index(answers_attributes)
                do_not_know_yet = self.tmp_quest.ordersFunListValue[indx]
                colon_command = row['colonCommand']

                if colon_command == 'cond':
                    self.cond_value = "(" + do_not_know_yet + ") and "
                    self.cond_value_py = "" + do_not_know_yet + ""

                if colon_command == "verify":
                    left_bracket = "range("
                    right_bracket = ")"

                self.attributes_quest_to_print += ("\n\t" + str(colon_command) + "='" +
                                                   str(left_bracket) + str(do_not_know_yet) + str(right_bracket) + "'")

            sub = "validate"
            orders_list = self.tmp_quest.ordersLower.values()
            val_res = [s for s in orders_list if sub in s]
            if row['answersAtributes'] == "validate":
                indx = self.tmp_quest.ordersFunListKey.index(answers_attributes)
                add_tag_value_py = self.tmp_quest.ordersFunListValue[indx]
                add_tag_value_py = add_tag_value_py.replace("Py ", "")
                self.validate_xml += add_tag_value_py

            if row['attributes'] != "" and not isnull(row['attributes']):
                attributes = str(row['attributes']).split(";")
                attributes_value = str(row['attributesValue']).split(";")
                i = 0

                for attribute in attributes:
                    self.attributes_quest_to_print += ("\n\t" + attribute + "='" + attributes_value[i] + "'")
                    i = i + 1

    def xml_print_header_title_question(self):

        self.prn_global.xml_string += "\n<" + str(self.tag_to_print)
        self.prn_global.xml_string += "\n\tlabel='" + self.q_name + "'"
        self.prn_global.xml_string += self.attributes_quest_to_print
        self.prn_global.xml_string += ">"

        # attributes_quest_to_print = ""
        if self.title_simple != "" and self.tag_to_print.lower() != "pipe":
            if self.tag_to_print.lower() != "html":
                self.prn_global.xml_string += "\n\t<title>"

            title_to_print = CC07XMLPrintGlobal.string_bracket_pipe(self.title_simple, self.tmp_quest)
            reg_pat = r'<b>( )*</b>|</b>( )*<b>'
            title_to_print = re.sub(reg_pat, " ", title_to_print )

            if title_to_print == "":
                title_to_print = "Title is empty. I am printing default title, so please put correct one."

            self.prn_global.xml_string += "\n\t\t" + title_to_print + "\n\t"
            if self.tag_to_print.lower() != "html":
                self.prn_global.xml_string += "</title>"

    def xml_print_insert_states(self, row_choice):

        new_line1 = "\n" + "\t"
        new_line2 = new_line1 + "\t"

        if row_choice == "row":
            self.insert_states_xml = "<comment>Select all that apply</comment>"

        for key, value in CO0Helper.statesDict.items():
            xml_exclusive_tmp = ""
            if value.strip() == 'None of the above' and row_choice == "row":
                xml_exclusive_tmp = " exclusive='1' "

            self.insert_states_xml += new_line2 + '<' + row_choice + ' label="ch' + str(key) + '"' + \
                xml_exclusive_tmp + '>' + value + "</" + row_choice + ">"

        self.post_question = ""

        if row_choice == "row":
            self.post_question = "\n<exec sst='0'>"
            self.post_question += "\ncommaFlag=0"
            self.post_question += '\ntxtArr=""'
            self.post_question += "\nfor eachRow in " + self.q_name + ".rows:"
            self.post_question += "\n\tif eachRow.val==1:"
            self.post_question += "\n\t\tif commaFlag==0:"
            self.post_question += "\n\t\t\ttxtArr=txtArr+eachRow.text"
            self.post_question += "\n\t\t\tcommaFlag=1"
            self.post_question += "\n\t\telse:"
            self.post_question += '\n\t\t\ttxtArr=txtArr+", "+eachRow.text'
            self.post_question += '\n' + self.q_name + "StatesHid.val=txtArr"
            self.post_question += "\n</exec>"
            self.post_question += "\n\n<suspend/>\n"
            self.post_question += "\n<textarea"
            self.post_question += '\n\tlabel="' + self.q_name + 'StatesHid"'
            self.post_question += '\n\twhere="execute,survey,report">'
            self.post_question += '\n\t<title>' + self.q_name + ' countries textual.</title>'
            self.post_question += "\n</textarea>"
            self.post_question += "\n\n<suspend/>\n\n"

    def xml_print_question_terminate(self):

        if self.q_name.find('end') > 0 and (self.q_name.find('at') or self.q_name.find('@')) > 0:
            self.at_end_char = "@end"
            self.at_end_hid_state = " and (QHidStage.r2) "

        self.prn_global.term_number += 1
        self.term_state = 1
        # self.prn_global.term_row += '<' + self.tag_row_to_print + ' label="r' + str(self.prn_global.term_number) + \
        #                             '" value="' + str(self.prn_global.term_number) + '">' + \
        #                             self.q_name.replace("ter", "").replace("atend", "").strip() + \
        #                             self.at_end_char + ' </' + self.tag_row_to_print + '>\n'

    def xml_print_title_simple(self):

        len_list = len(self.tmp_quest.paraCollection)
        jj = 0
        # print("TS=", len_list)
        for para in self.tmp_quest.paraCollection:
            jj += 1
            # print(jj, "para=", para)
            if para.find("[") == -1:   # para.text.find("[")
                self.title_simple_py += para[3:] + "\n"

            self.title_simple += para
            if len_list > (jj) > 1:
                self.title_simple += "\n"
                if not para.startswith("<li"):
                    self.title_simple += "<br/><br/>"
        # print("TS=", self.title_simple)

    def print_xml_column(self):

        tmp_quest_col = self.prn_global.questionnaire.questColl[str(self.q_name) + 'col']
        for answerCol in tmp_quest_col.answersDic.keys():
            tmp_answer_col = tmp_quest_col.answersDic[answerCol]
            tmp_answer_col_text = tmp_answer_col.paragraph
            left_bracket_cond = tmp_answer_col_text.find("[cond:")
            right_bracket_cond = tmp_answer_col_text.find("]", left_bracket_cond)
            cond_column_text = ""

            if left_bracket_cond >= 0 and right_bracket_cond >= 0:
                quotation_marks = '"'
                cond_column_text = tmp_answer_col_text[left_bracket_cond + 6: right_bracket_cond]
                cond_column_text = "cond=" + quotation_marks + cond_column_text + quotation_marks

            self.prn_global.xml_string += "\n\t<col label='c" + str(answerCol) + "' " +\
                cond_column_text + ">" + CC07XMLPrintGlobal.string_bracket_pipe(
                        tmp_answer_col.paragraph, tmp_answer_col).strip() + "</col>"

    def xml_print_answer_terminate(self, term_number_tmp, at_end_hid_state, term_answer, at_end_char):

        obj_global = self.prn_global

        obj_global.xml_string += "\n<note> Original Cond=" + term_answer + "</note>\n"
        obj_global.xml_string += "<term label='Term" + str(term_number_tmp) + "' "
        obj_global.xml_string += 'cond="(' + self.cond_value + 'processTerms(' + "'Disp" + \
                                 str(term_number_tmp) + "') "
        obj_global.xml_string += at_end_hid_state + ')"> Terminate ' + self.q_name + ' </term>'
        obj_global.term_condition += '<condition ' + 'label="Disp' + str(term_number_tmp) + '" '
        obj_global.term_condition += "cond='" + term_answer.strip() + "'>"
        obj_global.term_condition += 'Conditional Disposition ' + str(term_number_tmp) + ' </condition>\n'
        q_name_prn = str(self.q_name)
        replace_strings = ["ter", "term", "atend"]
        for key in replace_strings:
            q_name_prn = q_name_prn.replace(key, "")
        obj_global.term_row += '<' + self.tag_row_to_print + ' label="r' + str(term_number_tmp) + '" value="' \
                               + str(term_number_tmp) + '">' + q_name_prn + at_end_char + ' </' \
                               + self.tag_row_to_print + '>\n'

    def xml_print_execute(self):

        self.prn_global.xml_string += "\n<exec sst='0'"
        if self.cond_value_py != "":
            self.prn_global.xml_string += ' cond="' + self.cond_value_py + '"'

        self.prn_global.xml_string += ">\n\n"
        self.prn_global.xml_string += CC07XMLPrintGlobal.string_bracket_pipe(self.title_simple_py, self.tmp_quest)
        self.prn_global.xml_string += "\n</exec>\n\n"

    def xml_print_classify(self):

        if self.classify_remember_dic:
            self.classify_text += "\n<suspend/>\n"
            self.classify_text += "\n<exec>\n\n"
            classify_index = 0
            for key, value in self.classify_remember_dic.items():
                classify_index += 1
                self.classify_text += "if "
                for key2 in value:
                    self.classify_text += self.q_name + ".r" + str(int(key2)) + " or "

                self.classify_text = self.classify_text[:-3] + ":\n"
                self.classify_text += "    " + self.q_name + "HID.val = " + self.q_name + "HID.r" + str(classify_index)\
                                      + ".index\n"

            self.classify_text += "\n</exec>\n"
            self.classify_text += "\n<suspend/>\n"
            classify_index = 0
            self.classify_text += "\n<radio\n"
            self.classify_text += '\tlabel = "' + self.q_name + 'HID"\n'
            self.classify_text += '\toptional = "1"\n'
            self.classify_text += '\twhere = "execute,survey,report">\n'
            self.classify_text += '\t<title>Recorded from question ' + self.q_name + '</title>\n'
            for key, value in self.classify_remember_dic.items():
                classify_index += 1
                self.classify_text += "\t  <row label = 'r" + str(classify_index)
                self.classify_text += "'>" + str(key).title() + '</row>\n'

            self.classify_text += "</radio>\n"
            self.classify_text += "\n<suspend/>\n"


class CC07XMLPrintAnswer:

    def __init__(self, prn_quest, answer_num):

        self.prn_quest = prn_quest
        self.tmp_answer = prn_quest.tmp_quest.answersDic[answer_num]
        self.answer_num = answer_num
        prn_quest.tag_row_to_print = prn_quest.tag_row_to_print_state_remember
        self.attributes_to_print = ""
        self.label_gr = "r"
        self.group_xml = ''
        self.classify_check()

    def classify_check(self):

        break_outer = False
        for keyClassify, valueClassify in self.tmp_answer.ordersLower.items():
            for look in CC07XMLPrintQuest.classify_dic:
                if look in valueClassify:
                    find_text = valueClassify[len(look) + 1:].strip()
                    if find_text not in self.prn_quest.classify_remember_dic.keys():
                        self.prn_quest.classify_remember_dic[find_text] = []
                    self.prn_quest.classify_remember_dic[find_text].append(self.answer_num)
                    break_outer = True
                    break
            if break_outer:
                break

        if 'group' in self.tmp_answer.ordersLower.values():
            self.label_gr = "g"
            self.prn_quest.group_set = True
            self.prn_quest.group_set_label = self.answer_num
            self.group_xml = ''

        if 'nogrp' in self.tmp_answer.ordersLower.values():
            self.prn_quest.group_set = False
            self.group_xml = ''
            self.label_gr = "r"

        if not ('group' in self.tmp_answer.ordersLower.values()) and self.prn_quest.group_set:
            self.group_xml = ' groups="g' + str(self.prn_quest.group_set_label) + '" '

    def print_answer_attributes(self):

        if self.tmp_answer.EOFFilterDF is not None:

            answers_attributes_list = self.tmp_answer.EOFFilterDF['answersAtributes'].to_list()
            terminate_at_end_in_list = "terminateatend" in answers_attributes_list

            for index, row in self.tmp_answer.EOFFilterDF.iterrows():
                left_bracket = ""
                right_bracket = ""
                if row['rowTag'] != "" and not isnull(row['rowTag']):
                    self.prn_quest.tag_row_to_print = row['rowTag']
                if row['answersAtributes'] == "terminate" and not terminate_at_end_in_list:
                    if self.prn_quest.term_answer == "":
                        self.prn_quest.prn_global.term_number += 1
                        self.prn_quest.term_answer += self.prn_quest.q_name + ".r" + str(int(self.answer_num))
                    else:
                        self.prn_quest.term_answer += " or " + self.prn_quest.q_name + ".r" + str(int(self.answer_num))
                elif row['answersAtributes'] == "terminateatend":
                    if self.prn_quest.term_at_end_answer == "":
                        self.prn_quest.prn_global.term_number += 1
                        self.prn_quest.term_at_end_answer += self.prn_quest.q_name + ".r" + str(int(self.answer_num))
                    else:
                        self.prn_quest.term_at_end_answer += " or " + self.prn_quest.q_name + ".r" + \
                                                             str(int(self.answer_num))
                elif row['attributes'] != "" and not isnull(row['attributes']):
                    attributes_split = str(row['attributes']).split(";")
                    attributes_value_split = str(row['attributesValue']).split(";")
                    i = 0
                    for attribute in attributes_split:
                        if self.attributes_to_print.find(attribute+"=") == -1:
                            self.attributes_to_print += (" " + attribute + "='" + attributes_value_split[i] + "' ")
                        i = i + 1
                if row['colon(:)'] == 1 and not isnull(row['colon(:)']) and not isnull(row['colonCommand']):
                    answers_attributes = row['answersAtributes']
                    indx = self.tmp_answer.ordersFunListKey.index(answers_attributes)
                    do_not_know_yet = self.tmp_answer.ordersFunListValue[indx]
                    colon_command = row['colonCommand']
                    if colon_command == "verify":
                        left_bracket = "range("
                        right_bracket = ")"
                    self.attributes_to_print += (
                            " " + str(colon_command) + "='" + str(left_bracket) + str(do_not_know_yet)
                            + str(right_bracket) + "'")
        self.prn_quest.prn_global.xml_string += "\n\t<" + self.prn_quest.tag_row_to_print + " label='" + \
            self.label_gr + "" + str(int(self.answer_num)) + "'" + self.group_xml + \
            self.attributes_to_print + ">" \
            + CC07XMLPrintGlobal.string_bracket_pipe(self.tmp_answer.paragraph, self.tmp_answer).strip() +\
            "</" + self.prn_quest.tag_row_to_print + ">"

