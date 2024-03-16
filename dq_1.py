import telebot
from pymongo import MongoClient
# from config import BOT_TOKEN, MONGO

# bot = BOT_TOKEN
bot = telebot.TeleBot("6704490108:AAGscrT9P2AadTN20eH7vRNcjPqL8WNVNtE")



class DataBase:
	def __init__(self):
		# cluster = MONGO
		cluster = MongoClient("mongodb+srv://helikeel:2aCEOKLIMczzb17U@digo-1.bgjk2no.mongodb.net/?retryWrites=true&w=majority")

		self.db = cluster["QuizBot"]
		self.users = self.db["Users"]
		self.questions = self.db["Questions"]

		# Еше одна база упраэнений для платных подписчиков
		# self.course = self.db["Course"]

		self.questions_count = len(list(self.questions.find({})))

		# Получение номера урока в платном курсе
		# self.course_cont = len(list(self.course.find({})))

	def get_user(self, chat_id):
		user = self.users.find_one({"chat_id": chat_id})

		if user is not None:
			return user

		# Добавлние новых параметров пользователь: Оплачено и Номер/Ответ Платного урока
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
	# bot.send_message(message.from_user.id, "Начало работы")
	print("Начало работы")

	user = db.get_user(message.chat.id)
	# print("Создание нового пользователя")

	if user["is_passed"]:
		print("Если уэе прошел")
		bot.send_message(message.from_user.id, "Вы прошли бесплатную пробную версию курса по джаз-вокалу. Для получения доступа к полной версии необходимо оформить единоразовую подписку 👍😇 для этого переведите 30 евро на счет Eugenia Evy Anstal-Põld EE282200001109459014 и укажите в пояснении свой номер телефона")
		return

	if user["is_passing"]:
		print("Начало прохождения курса")
		return


	db.set_user(message.chat.id, {"question_index": 0, "is_passing": True})
	# print("установили пользователя")
	user = db.get_user(message.chat.id)
	# print("Получили пользователя")
	post = get_question_message(user)
	# print("Получили вопрос")
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
# 	# bot.send_message(query.from_user.id, "Вы прошли бесплатную пробную версию курса по джаз-вокалу. Для получения доступа к полной версии необходимо оформить единоразовую подписку 👍😇 для этого переведите 30 евро на счет Eugenia Evy Anstal-Põld EE282200001109459014 и укажите в пояснении свой номер телефона")

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


		text = f"Вы прошли бесплатную пробную версию курса по джаз-вокалу. Для получения доступа к полной версии необходимо оформить единоразовую подписку 👍😇 для этого переведите 30 евро на счет Eugenia Evy Anstal-Põld EE282200001109459014 и укажите в пояснении свой номер телефона"
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

	text = f"Вопрос №{user['question_index'] + 1}\n\n{question['text']}\n"

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
