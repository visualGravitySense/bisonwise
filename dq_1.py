import telebot
from pymongo import MongoClient
# from config import BOT_TOKEN, MONGO

# bot = BOT_TOKEN
bot = telebot.TeleBot("BOT_TOKEN")



class DataBase:
	def __init__(self):
		# cluster = MONGO
		cluster = MongoClient("MONGO_URL")

		self.db = cluster["QuizBot"]
		self.users = self.db["Users"]
		self.questions = self.db["QuestionsUX"]

		
		# self.course = self.db["Course"]

		self.questions_count = len(list(self.questions.find({})))

		
		# self.course_cont = len(list(self.course.find({})))

	def get_user(self, chat_id):
		user = self.users.find_one({"chat_id": chat_id})

		if user is not None:
			return user

		
		user = {
			"chat_id": chat_id,
			"is_passing": False,
			"is_passed": False,
			"paid": False,
			"question_index": None,
			"answers": [],
			"course_index": None,
			"course_answers": []
		}

		self.users.insert_one(user)

		return user


	def set_user(self, chat_id, update):
		self.users.update_one({"chat_id": chat_id}, {"$set": update})

	def get_question(self, index):
		return self.questions.find_one({"id": index})

db = DataBase()


@bot.message_handler(commands=["start"])
def start(message):
	# bot.send_message(message.from_user.id, "Привет! Я нашел увлекательное задание о создании высококачественного интерфейса чеклиста качества в фармацевтической отрасли. Я решил создать курс в телеграм-боте, который будет показывать полный процесс выполнения этого задания. Присоединяйтесь, чтобы узнать о всех шагах, начиная от анализа требований и исследования конкурентов до создания дизайна и прототипа интерфейса. Давайте вместе исследуем этот захватывающий процесс проектирования!")
	# print("Начало работы")

	user = db.get_user(message.chat.id)
	# print("Создание нового пользователя")

	if user["is_passed"]:
		# print("Если уэе прошел")
		bot.send_message(message.from_user.id, "Спасибо, что воспользовались нашим мини-ботом по вопросам на собеседование UX/UI! Желаем вам успешного прохождения собеседования и достижения ваших целей в области UX/UI дизайна! 👍😇")
		return

	if user["is_passing"]:
		# print("Начало прохождения курса")
		return


	db.set_user(message.chat.id, {"question_index": 0, "is_passing": True})
	
	user = db.get_user(message.chat.id)
	
	post = get_question_message(user)
	
	if post is not None:
		bot.send_message(message.from_user.id, post["text"], reply_markup=post["keyboard"])

@bot.callback_query_handler(func=lambda query: query.data.startswith("?ans"))
def answered(query):
	user = db.get_user(query.message.chat.id)

	if user["is_passed"] or not user["is_passing"]:
		return

	user["answers"].append(int(query.data.split("&")[1]))
	db.set_user(query.message.chat.id, {"answers": user["answers"]})

	post = get_answered_message(user)
	if post is not None:
		bot.edit_message_text(post["text"], query.message.chat.id, query.message.id,
						 reply_markup=post["keyboard"])

@bot.callback_query_handler(func=lambda query: query.data == "?next")
def next(query):
	user = db.get_user(query.message.chat.id)

	if user["is_passed"] or not user["is_passing"]:
		return

	user["question_index"] += 1
	db.set_user(query.message.chat.id, {"question_index": user["question_index"]})

	post = get_question_message(user)
	if post is not None:
		bot.edit_message_text(post["text"], query.message.chat.id, query.message.id,
						 reply_markup=post["keyboard"])

# # Написать новый Callback	для перехода к боту оплаты
# @bot.callback_query_handler(func=lambda query: query.data == "?pay")
# def pay(query):
# 	user = db.get_user(query.message.chat.id)
#
# 	# Здесь вы можете сгенерировать ссылку на бот №2 с параметрами, если это необходимо
# 	# payments_bot = "https://web.telegram.org/k/#@JazzVocalClassesBot"
# 	payments_bot = "https://web.telegram.org/k/#@msnsgerBot"
# 	# bot.send_message(message.from_user.id, f"Для оплаты перейдите по ссылке: {payments_bot}")
# 	bot.send_message(query.from_user.id, f"Для оплаты перейдите по ссылке: {payments_bot}")
# 	# bot.send_message(message.from_user.id, f"Для оплаты перейдите по ссылке: {payments_bot}")


def get_question_message(user):
	if user["question_index"] == db.questions_count:
		count = 0
		for question_index, question in enumerate(db.questions.find({})):

			if question["correct"] == user["answers"][question_index]:
				count += 1
		percents = round(100 * count / db.questions_count)

		if percents < 40:
			smile = "😥"
		elif percents < 60:
			smile = "😐"
		elif percents < 90:
			smile = "😀"
		else:
			smile = "😎"


		text = f"Congratulations! You have successfully completed all the lessons on creating a prototype for a quality checklist. Your UI design skills have improved significantly, and we are sure that you are ready to put them into practice. However, this is not the end of our journey together! Soon we will prepare new lessons and projects for you to help you continue your development in the field of design. Stay tuned and get ready for new challenges and achievements! 👍😇"
		# Встраивание новой кнопки "К оплате" >> функция запуска нового бота
		# keyboard2 = telebot.types.InlineKeyboardMarkup()
		# keyboard2.row(telebot.types.InlineKeyboardButton("Оплатить Курс 'Джаз-Вокал'", callback_data="?pay"))

		db.set_user(user["chat_id"], {"is_passed": False, "is_passing": False})

		return {
			"text": text,
			"keyboard": None
		}

	question = db.get_question(user["question_index"])

	if question is None:
		return

	keyboard = telebot.types.InlineKeyboardMarkup()
	for answer_index, answer in enumerate(question["answers"]):
		keyboard.row(telebot.types.InlineKeyboardButton(f"{chr(answer_index + 97)}) {answer}",
														callback_data=f"?ans&{answer_index}"))

	text = f"Урок №{user['question_index'] + 1}\n\n{question['text']}"

	return {
		"text": text,
		"keyboard": keyboard
	}


def get_answered_message(user):
	question = db.get_question(user["question_index"])

	text = f"Question №{user['question_index'] + 1}\n\n{question['text']}\n"

	for answer_index, answer in enumerate(question["answers"]):
		text += f"{chr(answer_index + 97)}) {answer}"

		if answer_index == question["correct"]:
			text += " ✅"
		elif answer_index == user["answers"][-1]:
			text += " ❌"

		text += "\n"

	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row(telebot.types.InlineKeyboardButton("Далее", callback_data="?next"))

	return {
		"text": text,
		"keyboard": keyboard
	}


bot.polling()
