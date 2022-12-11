"""
Project for Crawling Word Document and Producing XML Decipher Code

Documentation docx: https://buildmedia.readthedocs.org/media/pdf/python-docx/latest/python-docx.pdf
Python environment name: pythondocx"""

from __future__ import annotations
import classes.CC00_Helper as C00
import classes.CC01_Questionnaire as C01
# import re

# Preparing and Opening Working Files
helper = C00.CO0Helper
helper.preparation_of_temp_file()
helper.open_doc(helper)

# Processing
workingQuest = C01.CO1Questionnaire("Questionnaire")
workingQuest.docx_crawler(helper.docInput)
workingQuest.loop_and_find_orders()
# Printing of Questionnaire Below is Optional
# workingQuest.print_all_questionnaire()
workingQuest.print_xml(helper)
workingQuest.print_all_errors()

# Close Documents
helper.close_save_doc(helper)