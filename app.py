import logging
import os

from flask import Flask, request, jsonify

from chat.api import OpenAIAPI
from chat.qa import QA

logging.basicConfig(filename='record.log',
                    level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app = Flask(__name__)

openai_provider = OpenAIAPI(model="gpt-3.5-turbo", temperature=0.3, max_tokens=1024)
qa_instance = QA(api=openai_provider)


@app.route('/chat', methods=['POST'])
def answer_question():
    data = request.get_json()
    question = data.get('question')
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400

    app.logger.debug(f'Question: {question}')
    if question:
        answer_row = qa_instance.ask(question)
        app.logger.debug(f'Answer Meta: {answer_row.metadata}')
        app.logger.debug(f'Answer Response: {answer_row.response}')
        return jsonify({"answer": answer_row.response})

    return jsonify({"error": "Question missing"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
