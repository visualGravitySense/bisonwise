# UXUI QuizBot interview Bot for Telegram

This project is a Telegram bot designed to conduct quizzes and courses focused on UX/UI design. The bot interacts with users by providing them with various questions and exercises to help improve their skills in interface design.

## Key Features

- **Interactive Lessons and Quizzes**: The bot offers lessons on interface design in the form of multiple-choice questions. Depending on the user's answers, the bot guides them through the course, offering new lessons or summarizing their learning progress.
- **User Progress Tracking**: The bot keeps track of each user's progress, including the number of completed lessons and correct answers.
- **Integration with MongoDB**: MongoDB is used to store information about users and quiz questions. This allows for scalability and efficient data management.
- **Paid Courses**: The bot supports paid courses for advanced users. Payment options and access to additional materials can be configured within the bot.

## Installation and Setup

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/visualGravitySense/bisonwise
   cd bisonwise
   ```

2. Install the required dependencies:
   ```bash
   pip install pyTelegramBotAPI pymongo
   ```

3. Set up environment variables or replace the values in the code for `BOT_TOKEN` and `MongoClient`:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN"
   MONGO_URI = "YOUR_MONGO_CONNECTION_STRING"
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

## Usage

- **`/start` Command**: Begins interaction with the bot. The user is prompted to start the first lesson, followed by subsequent questions.
- **Answering Questions**: The user selects an answer by clicking the corresponding button.
- **Proceeding to the Next Question**: After answering the current question, the bot allows the user to proceed to the next one.
- **Course Completion**: Upon completing all lessons, the bot summarizes the results and offers additional paid courses.

## Code Structure

- **`DataBase`**: A class for interacting with the MongoDB database. It contains methods for retrieving and updating user data, as well as for fetching quiz questions.
- **Message and Callback Handlers**: Methods that handle user commands and responses, update data in the database, and send appropriate messages.
- **Message Generation Methods**: `get_question_message` and `get_answered_message` generate text messages and keyboards for user interaction.

## Requirements

- Python 3.x
- `pyTelegramBotAPI`
- `pymongo`
- A valid Telegram bot token and access to a MongoDB database.
