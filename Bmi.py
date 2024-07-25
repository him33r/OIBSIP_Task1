import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

#Database setup sql
conn = sqlite3.connect('bmi_data.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS bmi (
    id INTEGER PRIMARY KEY,
    date TEXT,
    weight REAL
    height REAL,
    bmi REAL
)
''')
conn.commit()

#BMI categories for restrictions 
def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Under weight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

#BMI Calculator
class BMICalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("BMI Calculator made by Himanshu")
        self.geometry("400x450")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Weight (kg):").pack(pady=10)
        self.weight_entry = ttk.Entry(self)
        self.weight_entry.pack(pady=5)

        ttk.Label(self, text="Height (cm):").pack(pady=10)
        self.height_entry = ttk.Entry(self)
        self.height_entry.pack(pady=5)

        #Calculate Button
        ttk.Button(self, text="Calculate BMI", command=self.calculate_bmi).pack(pady=20)

        self.result_label = ttk.Label(self, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=10)

        #Category Label
        self.category_label = ttk.Label(self, text="", font=("Helvetica", 12))
        self.category_label.pack(pady=5)

        #History Button
        ttk.Button(self, text="View History", command=self.view_history).pack(pady=10)

        #Trend Button
        ttk.Button(self, text="Show Trends", command=self.show_trend).pack(pady=10)

    def calculate_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get()) / 100  # Convert to meters

            if not (0 < weight < 500) or not (0 < height < 3):  # Validate input ranges
                raise ValueError("Invalid weight or height range.")

            bmi = weight / (height ** 2)
            bmi = round(bmi, 2)

            category = categorize_bmi(bmi)

            self.result_label.config(text=f"BMI: {bmi}")
            self.category_label.config(text=f"Category: {category}")

            #Save to database
            cursor.execute("INSERT INTO bmi (date, weight, height, bmi) VALUES (?, ?, ?, ?)",
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), weight, height, bmi))
            conn.commit()

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for weight (0-500 kg) and height (0-300 cm).")


    def view_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("BMI History")
        history_window.geometry("400x300")

        cursor.execute("SELECT date, weight, height, bmi FROM bmi")
        rows = cursor.fetchall()

        history_text = "\n".join([f"Date: {row[0]}, Weight: {row[1]} kg, Height: {row[2]*100} cm, BMI: {row[3]}" for row in rows])

        scrolled_text = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, width=50, height=15)
        scrolled_text.insert(tk.END, history_text)
        scrolled_text.config(state=tk.DISABLED)
        scrolled_text.pack(pady=10)

    def show_trend(self):
        cursor.execute("SELECT date, bmi FROM bmi")
        rows = cursor.fetchall()

        dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in rows]
        bmis = [row[1] for row in rows]

        if dates and bmis:
            plt.figure()
            plt.plot(dates, bmis, marker='o')
            plt.title("BMI Trend Over Time")
            plt.xlabel("Date")
            plt.ylabel("BMI")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showinfo("No Data", "No data available to show the trend.")

if __name__ == "__main__":
    app = BMICalculator()
    app.mainloop()

#Close the database connection
conn.close()
