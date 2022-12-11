# from classes.CC00_Helper import CO0Helper as c00
from classes.CC00_Helper import CrawlState
import classes.CC02_Question as C02
import classes.CC03_Answer as C03
# import functions.function_test as fun
import classes.CC05a_WordParagraph as C05a


class WordTable:

    def __init__(self, word_table, questionnaire, question_tmp):

        self.questionnaire = questionnaire
        self.word_table = word_table
        self.question_tmp = question_tmp
        self.loop_table()

    def loop_table(self):
        question_tmp_column = None
        row_number = 0
        column_number = -1
        zx80 = [[cell.text for cell in row.cells] for row in self.word_table.rows]
        # print("zx80=", zx80)
        for row_i, row in enumerate(self.word_table.rows):

            row_number += 1
            # print("row:", row_i)
            join_row = ""
            cell_number = 0
            remember_cell = {}
            column_state = 0
            for col_j, cell in enumerate(row.cells):

                join_para = ""
                cell_number += 1
                # print("col:", col_j)
                paragraph_count = 1
                new_line = ""
                for paragraph in cell.paragraphs:
                    # print("paragraph", paragraph.text)
                    word_paragraph = C05a.WordParagraph(paragraph, self.questionnaire)

                    if paragraph_count > 1 and len(paragraph.text.strip()) > 0:
                        if self.questionnaire.current_state == CrawlState.Answer:
                            new_line = "<br/>"
                        if self.questionnaire.current_state == CrawlState.Question:
                            new_line = "<br/><br/>"
                    join_para += new_line + word_paragraph.word_paragraph_text_html

                    # HERE I NEED A CHECK WEATHER JOINED PARAGRAPH STARTS A NEW QUESTION
                    # ONLY IF IT IS A FIRST CELL IN
                    if word_paragraph.first_word_begin_question and paragraph_count > 1:
                        join_para = word_paragraph.word_paragraph_text_html
                        word_paragraph.first_word_begin_question = False
                    # print("para_count:", paragraph_count)
                    # print("join_para", join_para)
                    paragraph_count += 1

                if column_state == row_number and join_para.strip() != "":

                    column_number += 1
                    answer_column_tmp = C03.CO3Answer(column_number, " x " + join_para)
                    question_tmp_column.answer_coll_append(column_number, answer_column_tmp, self)

                if cell_number == 1 and (join_para.strip().startswith("[column]") or
                                         join_para.strip().startswith("[columns]")):
                    question_tmp_column = C02.CO2Question(self.question_tmp.pName + "col")
                    self.questionnaire.quest_coll_append(question_tmp_column)
                    column_state = row_number
                    column_number = 0

                if cell_number > 2:
                    if join_para.find("]") == -1 and join_para.find("\[") == -1:
                        join_para = " [" + join_para + "]"
                remember_cell[cell_number] = join_para
                if not (cell_number > 1 and remember_cell[cell_number] == remember_cell[cell_number - 1])\
                        and column_state == 0:
                    join_row += join_para + " "
                elif not join_row.strip().isnumeric():
                    cell_number -= 1
                if cell_number == 2:

                    # OVDJE SAM DOSAO
                    # replace_strings = [".", "", ":", ""]
                    # print("x1=", remember_cell[1])
                    # print("x2=", remember_cell[2])

                    try:
                        cell2_fist_word = remember_cell[2].strip().split()[0]
                        cell1_fist_word = remember_cell[1].strip().split()[0]

                        replace_strings = [".", "", ":", ""]
                        for key in replace_strings:
                            cell2_fist_word = cell2_fist_word.replace(key, "")
                            cell1_fist_word = cell1_fist_word.replace(key, "")

                        if cell2_fist_word.isnumeric() and not cell1_fist_word.isnumeric():
                            join_row = remember_cell[2] + " " + remember_cell[1]
                    except:
                        pass
                # if we have for example:
                # 1	   	 Primary Care / Family Medicine
                if (join_para.strip() == "" or join_para.strip() == "") and cell_number == 2:
                    cell_number -= 1

            join_row = join_row.strip()
            # print(join_row)
            if len(join_row) > 0:

                self.questionnaire.set_working_paragraph(C05a.TableParagraph(join_row))
                self.questionnaire.crawl_conditions()  # (join_row)
