class CO2Question:

    fil = "~(EOF['type'] == 'answersAtributes') & ~(EOF['type'] == 'questionTypesAddon')"

    def __init__(self, p_name):

        self.errors = []
        self.EOFFilterDF = None
        self.ordersFunListKey = None
        self.ordersFunListValue = None
        self.answersDic = {}
        self.questText = ""
        self.pName = p_name
        self.paraCollection = []
        self.orders = {}
        self.ordersLower = {}

    def para_coll_app(self, para):

        self.paraCollection.append(para)
        self.questText += "\n\r<br/><br/>" + para

    def answer_coll_append(self, answer_number, answer_tmp, questionnaire):

        if answer_number not in self.answersDic:
            self.answersDic[answer_number] = answer_tmp
        else:
            questionnaire.errorColl.append("Error in question:" + self.pName + " double answers:" + answer_number)
