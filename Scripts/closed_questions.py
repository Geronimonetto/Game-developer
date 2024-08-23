import sys
import tempfile
import os
import pygame
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, \
    QHBoxLayout, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap
from gtts import gTTS
from questions import load_questions_from_txt
from random import shuffle

class QuizApp(QWidget):
    def __init__(self):
        super().__init__()

        self.modules = load_questions_from_txt('questions.txt')
        self.questions = []
        self.current_question_index = 0
        self.lives = 5
        self.consecutive_errors = 0
        self.heart_icon_path = 'heart_icon.png'  # Salve a imagem nesse caminho antes de executar
        self.question_already_read = False  # Variável depyenv controle
        pygame.mixer.init()  # Inicializa o mixer do pygame
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.module_selection = QComboBox(self)
        self.module_selection.addItems(self.modules.keys())
        self.module_selection.setFont(QFont('Arial', 14))
        self.layout.addWidget(self.module_selection)

        self.start_button = QPushButton('Iniciar Quiz', self)
        self.start_button.setFont(QFont('Arial', 14))
        self.start_button.clicked.connect(self.start_quiz)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)

        self.setWindowTitle('Quiz App')
        self.setGeometry(100, 100, 800, 600)
        self.center_window()

    def center_window(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def start_quiz(self):
        selected_module = self.module_selection.currentText()
        self.questions = self.modules[selected_module]
        shuffle(self.questions)
        self.init_quiz_ui()
        self.display_question()

    def init_quiz_ui(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        self.lives_layout = QHBoxLayout()
        self.lives_label = QLabel("Vidas:", self)
        self.lives_label.setFont(QFont('Arial', 14))
        self.lives_layout.addWidget(self.lives_label)

        self.heart_labels = []
        for _ in range(5):
            heart_container = QWidget(self)
            heart_layout = QHBoxLayout(heart_container)
            heart_layout.setAlignment(Qt.AlignCenter)
            heart_label = QLabel(self)
            heart_label.setPixmap(QPixmap(self.heart_icon_path).scaled(32, 32, Qt.KeepAspectRatio))
            heart_layout.addWidget(heart_label)
            self.lives_layout.addWidget(heart_container)
            self.heart_labels.append(heart_label)

        self.lives_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.lives_layout)

        self.question_label = QLabel(self)
        self.question_label.setFont(QFont('Arial', 16))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)
        self.question_label.setMaximumWidth(750)
        self.layout.addWidget(self.question_label)

        self.remaining_questions_label = QLabel(self)
        self.remaining_questions_label.setFont(QFont('Arial', 14))
        self.remaining_questions_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.remaining_questions_label)

        self.answer_input = QLineEdit(self)
        self.answer_input.setFont(QFont('Arial', 14))
        self.answer_input.returnPressed.connect(self.check_answer)
        self.layout.addWidget(self.answer_input)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.setFont(QFont('Arial', 14))
        self.submit_button.clicked.connect(self.check_answer)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(240, 248, 255, 255), stop:1 rgba(173, 216, 230, 255));
            }
        """)

    def display_question(self):
        if self.lives <= 0:
            reply = QMessageBox.question(self, "Fim do Jogo", "Você perdeu todas as suas vidas! Deseja reiniciar o jogo?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.restart_game()
            else:
                self.close()
            return

        if self.current_question_index < len(self.questions):
            self.update_hearts()
            question = self.questions[self.current_question_index]
            self.question_label.setText(question["question"])
            self.question_label.adjustSize()
            self.answer_input.clear()

            self.correct_answer = question["correct_answer"].strip().lower()
            self.options = question["options"]
            self.update_remaining_questions()

            # Leia a questão em voz alta após um pequeno atraso para garantir que ela seja exibida na tela primeiro
            if not self.question_already_read:
                QTimer.singleShot(500, lambda: self.read_question_aloud(question["question"]))
                self.question_already_read = True  # Marcar como já lida
        else:
            QMessageBox.information(self, "Fim do Quiz", "Você concluiu todas as perguntas!")
            self.close()

    def read_question_aloud(self, question_text):
        tts = gTTS(text=question_text, lang='pt')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            temp_path = f.name
            tts.save(temp_path)
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()

    def update_hearts(self):
        for i in range(5):
            if i < self.lives:
                self.heart_labels[i].setPixmap(QPixmap(self.heart_icon_path).scaled(32, 32, Qt.KeepAspectRatio))
            else:
                self.heart_labels[i].clear()

    def update_remaining_questions(self):
        total_questions = len(self.questions)
        questions_left = total_questions - self.current_question_index
        self.remaining_questions_label.setText(f"Questões restantes: {questions_left}")

    def check_answer(self):
        user_answer = self.answer_input.text().strip().lower()
        if user_answer == self.correct_answer:
            QMessageBox.information(self, "Resposta Correta", "Parabéns, você acertou!")
            self.consecutive_errors = 0
            self.current_question_index += 1
            self.question_already_read = False  # Redefinir para a próxima pergunta
            self.display_question()
        else:
            self.lives -= 1
            self.consecutive_errors += 1
            self.update_hearts()
            if self.consecutive_errors >= 2:
                self.show_suggestion()
                self.consecutive_errors = 0
            if self.lives > 0:
                QMessageBox.warning(self, "Resposta Incorreta", "Resposta errada, tente novamente!")
            self.display_question()

    def show_suggestion(self):
        suggestion_text = "Sugestão: Considere uma das seguintes alternativas:\n"
        for option_key, option_text in self.options.items():
            suggestion_text += f"{option_key}: {option_text}\n"
        QMessageBox.information(self, "Sugestão de Resposta", suggestion_text)

    def restart_game(self):
        self.lives = 5
        self.current_question_index = 0
        self.question_already_read = False  # Redefinir para o reinício do jogo
        shuffle(self.questions)
        self.display_question()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    quiz = QuizApp()
    quiz.show()
    sys.exit(app.exec_())