
def dnu_string_bracket_old(self, working_string, object):
    # print("oznaka4=", workingString)
    if len(object.errors) > 0 or working_string.strip() == "":
        return working_string  # self.replace_strings(working_string)
    left_bracket = [m.start() for m in re.finditer('\[', working_string)]
    right_bracket = [m.start() for m in re.finditer(']', working_string)]
    first_word = working_string.split()[0]
    right_bracket.insert(0, len(first_word))
    left_bracket.append(len(working_string))
    working_string = ''.join(
        [working_string[right_bracket[i - 1] + 1: left_bracket[i - 1]] for i, m in enumerate(left_bracket, 1)])
    # print("oznaka5=", workingString)

    return self.replace_strings_fun(working_string)


def dnu_string_bracket_pipe(self, working_string, object):
    # print("working_string=", working_string)
    if len(object.errors) > 0 or working_string.strip() == "":
        return self.replace_strings_fun(working_string).strip()
    first_word = working_string.split()[0]
    # start() function finds match in regular expressions
    left_bracket = [m.start() for m in re.finditer('\[', working_string) if
                    not working_string[m.start():m.start() + 6] == "[pipe:"]
    if len(left_bracket) == 0:
        # return self.replace_strings(working_string[len(first_word) + 1:99999]).strip()
        return (working_string[len(first_word) + 1:99999]).strip()
    beginning = working_string[len(first_word) + 1:left_bracket[0]]
    right_bracket = [m + working_string[m:].find("]") for m in left_bracket]

    # leftBracket.insert(0, len(first_word))
    # leftBracket.append(len(workingString))
    #
    left_bracket.pop(0)
    left_bracket.append(999999)
    working_string = ''.join(
        [working_string[right_bracket[i - 1] + 1: left_bracket[i - 1]] for i, m in enumerate(left_bracket, 1)])
    # return self.replace_strings(beginning + " " + working_string).strip()
    return (beginning + " " + working_string).strip()


# if block.style.name == 'List Paragraph':
#     print(block._p.xml)
#     exit()

# List Bullet Paragraph
# if block.style.name == "List Bullet":
#     docOutput.add_paragraph('List Bullet:' + block.text)
# elif block.style.name == 'List Paragraph':
#     # if len(block._element.xpath('./w:pPr/w:numPr')) > 0:
#     print('List Para:', block.text)
#     docOutput.add_paragraph('List Para:' + block.text)
# else:
#     print(block.text)
#     docOutput.add_paragraph(block.text)


# BOLD
# par_text = ""
# for run in block.runs:
#     if run.bold:
#         par_text += 'BOLD ' + run.text
#     else:
#         par_text += run.text
# docOutput.add_paragraph('PSN:' + block.style.name + ':EndPSN' + par_text)



# Search for the pattern "Brackets in Brackets" "[sz[sz]]"
workingString = '[test1] test [test2][wsz3] [test4]'

leftBracket = [m.start() for m in re.finditer('\[', workingString)]
rightBracket = [m.start() for m in re.finditer(']', workingString)]

print(leftBracket)
print(rightBracket)
betweenBrackets = [workingString[leftBracket[i - 1] + 1:rightBracket[i - 1]] for i, m in enumerate(leftBracket, 1)]
print(betweenBrackets)
# print(helper.find_orders(helper, workingString))



# DataFrame constructor after zipping
# both lists, with columns specified
ordersFunDF = pd.DataFrame(list(zip(ordersFunListKey, ordersFunListValue)),
                  columns=['answersAtributes', 'ordersContent'])

result = pd.merge(ordersFunDF, EOFFilterDF, on="answersAtributes")



def ordersDF(ORDERQues, fil):

    helper = c00.CO0Helper
    EOF = helper.elaborationOfFunctions
    EOFFilterDF = EOF
    exec("EOFFilterDF = EOF.loc[" + fil + "]")
    print(EOFFilterDF)
    print("EOFFilterDF = EOF.loc[" + fil + "]")
    exit()
    EOFFilterList = EOFFilterDF["answersAtributes"].tolist()

    ordersFunDict = {fun: ORDERQues[ord] for fun in EOFFilterList for ord in ORDERQues.keys() if ORDERQues[ord].lower().find(fun.lower().strip()) >= 0}
    ordersFunDict = {ord: ordersFunDict[ord].replace(ord, "").replace(":", "").strip() for ord in ordersFunDict.keys()}
    ordersFunListKey = [key for key in ordersFunDict.keys()]
    ordersFunListValue = [ordersFunDict[key] for key in ordersFunDict.keys()]

    EOFFilterDF = EOFFilterDF[EOFFilterDF.answersAtributes.isin(ordersFunListKey)]
    return EOFFilterDF

ORDERQues = {0: "numeric",
             1: "range: 0,99",
             2: "rowLegend: right",
             3: "insert states"
             }
ORDERAnswer = {1: "TEMINATE AT END",
               0: "EXCLUSIVE",
               2: "xdxdd"
               }
fil = "~(EOF['type'] == 'answersAtributes') & ~(EOF['type'] == 'questionTypesAddon')"
# fil = "(EOF['type'] == 'answersAtributes')"


def docxCrawler(self, docInput, helper):
    questionTmp = None
    # important in reading from tables
    Start = 0

    class State(Enum):
        StateNone = 1
        Question = 2
        Answer = 3

    firstQuestionStarted = False
    currentState = State.StateNone

    for block in fun.iter_block_items(docInput):

        if isinstance(block, Paragraph):

            numCharInPara = len(block.text)
            if numCharInPara > 0:
                # works also for space and tab
                first_word = block.text.split()[0]
            else:
                continue
            if block.text.lower().find("[start]") >= 0:
                Start = 1
            if block.text.lower().find("[end]") >= 0:
                Start = 0

            # First word and contains number and Dot last
            # u1=First Letter of first word is letter(isalpha)
            u1 = first_word[0].isalpha()
            u2 = any(char.isdigit() for char in first_word)
            u3 = first_word[-1].find(".") != -1
            # first_word[0:-2] = All except "." and "number"
            u4 = first_word[0:-2].isupper()
            u5 = first_word[0:-2].isalpha()
            u6 = first_word[-1].find(".") != -1

            if Start == 1 and ((u1 and u2 and u3) or (u4 and u5 and u6)):
                currentState = State.Question
                firstQuestionStarted = True
                qName = first_word.replace(".", "")
                questionTmp = C02.CO2Question(qName)
                self.quest_coll_append(qName, questionTmp, helper)

            if firstQuestionStarted and Start == 1:
                answerNumber = fun.number_candidate(first_word, helper)
                if answerNumber.isnumeric():
                    currentState = State.Answer
                    answerTmp = answ.CO3Answer(answerNumber, block)
                    questionTmp.answerCollAppend(answerNumber, answerTmp, helper)

            if currentState == State.Question:
                questionTmp.paraCollApp(block)
            if currentState == State.Answer:
                currentState = State.StateNone

        elif isinstance(block, Table):
            fun.table_print(block)
