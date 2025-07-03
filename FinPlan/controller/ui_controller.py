from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QBrush, QColor

class UIController:
    """
    Controller for UI: toggles buttons, manages input modes,
    displays dialogs, and refreshes tables/charts.
    """
    def __init__(self, view):
        """
        Store references to main window panels.
        """
        self.view = view
        self.input_panel = view.input_panel
        self.output_panel = view.output_panel

    def enable_main_buttons(self):
        """
        Enable primary action buttons after period is set.
        """
        ip = self.input_panel
        ip.submitExpensesBtn.setEnabled(True)
        ip.submitIncomeBtn.setEnabled(True)
        ip.nextPeriodBtn.setEnabled(True)
        ip.refreshOutputBtn.setEnabled(True)
        ip.changeScenarioBtn.setEnabled(True)
        ip.saveExitBtn.setEnabled(True)
        ip.clearDataBtn.setEnabled(True)

    def init_after_period(self, labels, month):
        """
        Set month buttons and disable date selection.
        """
        ip = self.input_panel
        ip.set_month_buttons_labels(labels)
        ip.enable_date_selection(False)
        ip.enable_month_buttons(True)
        ip.clear_month_buttons_selection()
        ip.month_buttons[0].setChecked(True)

    def enter_pre_shift_mode(self, month):
        """
        Prepare UI for entering actuals before shifting period.
        """
        ip = self.input_panel
        ip.enable_date_selection(False)
        ip.enable_month_buttons(False)
        ip.confirmMonthBtn.setEnabled(False)
        ip.nextPeriodBtn.setEnabled(False)
        ip.recalcPeriodBtn.setEnabled(True)
        ip.submitExpensesBtn.setEnabled(True)
        ip.submitIncomeBtn.setEnabled(True)
        ip.refreshOutputBtn.setEnabled(False)
        ip.changeScenarioBtn.setEnabled(False)
        ip.saveExitBtn.setEnabled(False)
        ip.clearDataBtn.setEnabled(False)
        ip.clear_month_buttons_selection()
        ip.month_buttons[0].setChecked(True)

    def refresh_ui_after_shift(self, labels, months, first_month_label):
        """
        Restore full UI after a period shift.
        """
        ip = self.input_panel
        ip.set_month_buttons_labels(labels)
        ip.clear_month_buttons_selection()
        ip.month_buttons[0].setChecked(True)
        ip.start_label.setText(first_month_label)
        ip.enable_month_buttons(True)
        ip.nextPeriodBtn.setEnabled(True)
        ip.recalcPeriodBtn.setEnabled(False)
        ip.submitExpensesBtn.setEnabled(True)
        ip.submitIncomeBtn.setEnabled(True)
        ip.refreshOutputBtn.setEnabled(True)
        ip.changeScenarioBtn.setEnabled(True)
        ip.saveExitBtn.setEnabled(True)
        ip.clearDataBtn.setEnabled(True)
        ip.enable_date_selection(False)

    def reset_ui_after_clear(self):
        """
        Reset inputs and re-enable only date confirmation.
        """
        ip = self.input_panel
        ip.clear_expense_inputs()
        ip.clear_income_inputs()
        ip.enable_date_selection(True)
        ip.confirmMonthBtn.setEnabled(True)
        ip.enable_month_buttons(False)
        ip.clear_month_buttons_selection()
        ip.start_label.setText("Choose month")
        ip.nextPeriodBtn.setEnabled(False)
        ip.recalcPeriodBtn.setEnabled(False)
        ip.submitExpensesBtn.setEnabled(False)
        ip.submitIncomeBtn.setEnabled(False)
        ip.refreshOutputBtn.setEnabled(False)
        ip.changeScenarioBtn.setEnabled(False)
        ip.saveExitBtn.setEnabled(False)
        ip.clearDataBtn.setEnabled(False)

    def show_warning(self, title, message):
        """
        Display a warning dialog.
        """
        QMessageBox.warning(self.view, title, message)

    def show_info(self, title, message):
        """
        Display an informational dialog.
        """
        QMessageBox.information(self.view, title, message)

    def confirm_dialog(self, title, message, default_button=QMessageBox.No):
        """
        Ask a Yes/No confirmation; return True on Yes.
        """
        ans = QMessageBox.question(
            self.view, title, message,
            QMessageBox.Yes | QMessageBox.No,
            default_button
        )
        return ans == QMessageBox.Yes

    def refresh_entries_table(self, headers, rows):
        """
        Populate the forecast entries table with grouped headers.
        """
        table = self.output_panel.entries_table
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            if len(row) == 1:
                item = QTableWidgetItem(row[0])
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(QBrush(QColor(220, 220, 220)))
                table.setSpan(i, 0, 1, len(headers))
                table.setItem(i, 0, item)
            else:
                for j, val in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(val))
        table.resizeColumnsToContents()

    def refresh_forecast_table(self, headers, rows):
        """
        Update forecast metrics table via output panel.
        """
        self.output_panel.set_forecast_data(headers, rows)

    def refresh_charts(self, net_flows, runways):
        """
        Redraw Net Cash Flow and Runway charts.
        """
        self.plot_chart(self.output_panel.figure1, self.output_panel.canvas1,
                        "Net Cash Flow", net_flows)
        self.plot_chart(self.output_panel.figure2, self.output_panel.canvas2,
                        "Runway", runways)

    def plot_chart(self, figure, canvas, title, data):
        """
        Render a line chart on provided figure and canvas.
        """
        figure.clear()
        ax = figure.add_subplot(111)
        self.plot_series(ax, title, data)
        figure.tight_layout()
        canvas.draw()

    def plot_series(self, ax, title, data):
        """
        Plot actual vs forecast and connect with a dotted line.
        """
        x_all = list(range(len(data)))
        actual = [(i, val) for i, (typ, _, val) in enumerate(data) if typ == "actual"]
        forecast = [(i, val) for i, (typ, _, val) in enumerate(data) if typ == "forecast"]
        ax.clear()
        ax.set_title(title)
        ax.grid(True)
        ax.set_xticks(x_all)
        ax.set_xlabel("Month")
        if actual:
            ax.plot(*zip(*actual), linestyle="-", marker="o")
        if forecast:
            ax.plot(*zip(*forecast), linestyle="--", marker="x")
        if actual and forecast:
            ax.plot([actual[-1][0], forecast[0][0]],
                    [actual[-1][1], forecast[0][1]],
                    linestyle=":", linewidth=2)