import sys
import os
import pandas as pd
from datetime import datetime
from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class Habit:
    def __init__(self, name, base_xp=4):
        self.name = name
        self.base_xp = base_xp  # XP por atividade
        self.current_progress = 0  # Progresso atual

    def perform_habit(self):
        self.current_progress += 1
        return self.base_xp


class FitnessTracker:
    def __init__(self):
        self.habits = []
        self.daily_data = []

    def add_habit(self, habit):
        self.habits.append(habit)

    def save_to_excel(self):
        if not self.daily_data:
            return

        df = pd.DataFrame(self.daily_data)
        file_name = "habit_data.xlsx"

        # Convertendo a coluna de data para string formatada
        df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%Y-%m-%d')

        if not os.path.exists(file_name):
            df.to_excel(file_name, index=False)
        else:
            existing_df = pd.read_excel(file_name)
            combined_df = pd.concat([existing_df, df])
            combined_df.to_excel(file_name, index=False)

    def load_from_excel(self):
        file_name = "habit_data.xlsx"
        if os.path.exists(file_name):
            df = pd.read_excel(file_name)
            if 'Data' in df.columns:
                # Filtrar registros para a data atual
                today = datetime.now().date()
                df['Data'] = pd.to_datetime(df['Data']).dt.date  # Ajuste para comparar apenas a data
                self.daily_data = df[df['Data'] == today].to_dict(orient='records')

                # Atualiza o progresso atual dos hábitos
                for habit in self.habits:
                    habit.current_progress = df[habit.name].sum() // habit.base_xp

    def calculate_total_xp(self):
        return sum(habit.current_progress * habit.base_xp for habit in self.habits)

    def calculate_level(self, total_xp):
        if total_xp < 30 * 7:
            return 1, 30 * 7
        elif total_xp < 32 * 7:
            return 2, 32 * 7
        elif total_xp < 34 * 7:
            return 3, 34 * 7
        else:
            return 4, float('inf')  # Nível máximo

    def check_if_today_recorded(self):
        today = datetime.now().date()
        for record in self.daily_data:
            if record['Data'] == today:
                return True
        return False


class HabitTrackerApp(QtWidgets.QWidget):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        self.init_ui()
        self.tracker.load_from_excel()  # Carregando dados do Excel
        self.update_dashboard()  # Atualizando o gráfico com os dados carregados

    def init_ui(self):
        self.setWindowTitle("Rastreador de Hábitos")
        self.setGeometry(100, 100, 600, 500)  # Aumentando a dimensão da janela

        self.layout = QtWidgets.QVBoxLayout()

        self.habit_checkboxes = []
        for habit in self.tracker.habits:
            checkbox = QtWidgets.QCheckBox(habit.name)
            checkbox.setIcon(QtGui.QIcon("check_icon.png"))  # Ícone para cada checkbox
            self.layout.addWidget(checkbox)
            self.habit_checkboxes.append(checkbox)

        self.submit_button = QtWidgets.QPushButton("Registrar Hábitos")
        self.submit_button.setIcon(QtGui.QIcon("submit_icon.png"))  # Ícone para o botão de submit
        self.submit_button.clicked.connect(self.record_habits)
        self.layout.addWidget(self.submit_button)

        # Área para o gráfico
        self.canvas = FigureCanvas(plt.Figure())
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

    def record_habits(self):
        if self.tracker.check_if_today_recorded():
            QtWidgets.QMessageBox.warning(self, "Atenção", "Os dados de hoje já foram preenchidos. Tente novamente amanhã.")
            return

        daily_xp = {}
        for i, habit in enumerate(self.tracker.habits):
            if self.habit_checkboxes[i].isChecked():
                xp = habit.perform_habit()
                daily_xp[habit.name] = xp

        if daily_xp:
            self.tracker.daily_data.append({
                'Data': datetime.now().date(),
                'XP Total': sum(daily_xp.values()),
                **daily_xp
            })

            self.tracker.save_to_excel()
            QtWidgets.QMessageBox.information(self, "Registro", "Hábitos registrados com sucesso!")
            self.update_dashboard()
        else:
            QtWidgets.QMessageBox.warning(self, "Atenção", "Nenhum hábito selecion.")

    def update_dashboard(self):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        total_xp = self.tracker.calculate_total_xp()
        level, next_level_xp = self.tracker.calculate_level(total_xp)

        # Dados para o gráfico
        xp_needed = next_level_xp - total_xp
        ax.barh(['XP Acumulado', 'XP Necessário para Próximo Nível'], [total_xp, xp_needed], color=['blue', 'orange'])
        ax.set_xlabel('XP')
        ax.set_title(f'Nível Atual: {level}')

        # Adicionando rótulos nas barras
        for i in range(len(['XP Acumulado', 'XP Necessário para Próximo Nível'])):
            ax.text(total_xp if i == 0 else xp_needed + 2, i, str(total_xp if i == 0 else xp_needed), va='center')

        self.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    tracker = FitnessTracker()

    # Definindo 8 hábitos
    tracker.add_habit(Habit("Correr 3km"))
    tracker.add_habit(Habit("Escada 30min"))
    tracker.add_habit(Habit("Treino na academia"))
    tracker.add_habit(Habit("Leitura de livro"))
    tracker.add_habit(Habit("Meditação"))
    tracker.add_habit(Habit("Cozinhar uma refeição saudável"))
    tracker.add_habit(Habit("Estudar engenharia de dados"))
    tracker.add_habit(Habit("Caminhada de 1 hora"))

    window = HabitTrackerApp(tracker)
    window.show()

    sys.exit(app.exec_())
