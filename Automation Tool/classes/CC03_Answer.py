from classes.CC02_Question import CO2Question


class CO3Answer:

    fil = "(EOF['type'] == 'answersAtributes')"

    def __init__(self, answer_number, para_text):

        self.errors = []
        self.EOFFilterDF = None
        self.ordersFunListKey = None
        self.ordersFunListValue = None
        self.answerNumber = answer_number
        self.paragraph = para_text
        self.paraCollection = [para_text]
        self.orders = {}
        self.ordersLower = {}

    def other_answer_specify(self, p_name, answer, questionnaire, order_number):

        tmp_quest_test = questionnaire.questColl[str(p_name)]
        if any([key in tmp_quest_test.orders.values() for key in ["number", "running sum"]]):
            self.orders[order_number] = "othNumGrid"
            tmp_quest_test.orders[len(tmp_quest_test.orders) + 1] = \
                "validate:  \
                \nx=this.r" + answer + ".ival\
                \ny=this.r" + answer + ".open\
                \nif x&gt;0 and y=='':\
                \n\terror(res.otherx)\
                \nif y!='' and x==0:\
                \n\terror(res.othery);"
            questionnaire.orders_df(tmp_quest_test, CO2Question.fil)
        else:
            self.orders[order_number] = "other"


