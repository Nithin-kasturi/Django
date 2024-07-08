
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    
    '''
    if current_question_id is None:
        return False, "There is no current question to answer."
    try:
        current_question = PYTHON_QUESTION_LIST[current_question_id]
    except IndexError:
        return False, "Invalid question ID."
    if "answers" not in session:
        session["answers"] = {}
    
    session["answers"][current_question_id] = answer
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        # Starting the quiz, so return the first question
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
        return next_question, next_question_id
    else:
        # No more questions left
        return None, None
    # return "dummy question", -1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    correct_answers = 0
    total_questions = len(PYTHON_QUESTION_LIST)

    for question_id, answer in session.get("answers", {}).items():
        correct_answer = PYTHON_QUESTION_LIST[question_id]["answer"]
        if answer == correct_answer:
            correct_answers += 1

    score_percentage = (correct_answers / total_questions) * 100

    result_message = (
        f"You have completed the quiz. "
        f"Your score is {correct_answers} out of {total_questions} ({score_percentage:.2f}%)."
    )

    # Optionally, you can add a performance message based on the score
    if score_percentage == 100:
        result_message += " Excellent job! You got all the answers right!"
    elif score_percentage >= 80:
        result_message += " Great job! You have a strong understanding of Python."
    elif score_percentage >= 50:
        result_message += " Good effort! You have a decent understanding of Python."
    else:
        result_message += " It looks like you need to work on your Python skills. Keep practicing!"

    return result_message

    # return "dummy result"
