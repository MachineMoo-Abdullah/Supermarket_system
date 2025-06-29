import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime


class DashboardPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Dashboard - Supermarket Management System")
        self.master.geometry("900x700")
        self.master.config(bg='white')

        self.connect_db()
        self.fetch_stats()
        self.build_ui()

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="supermarket_db"
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error connecting to database:\n{str(e)}")

    def fetch_stats(self):
        try:
            self.cursor.execute("SELECT IFNULL(SUM(total_amount), 0) FROM orders")
            self.total_sales = f"Rs {self.cursor.fetchone()[0]:,.0f}"

            self.cursor.execute("SELECT IFNULL(SUM(quantity_in_stock), 0) FROM items")
            self.items_in_stock = f"{self.cursor.fetchone()[0]}"

            self.cursor.execute("SELECT COUNT(*) FROM orders")
            self.total_orders = f"{self.cursor.fetchone()[0]}"

            self.cursor.execute("SELECT COUNT(*) FROM customers")
            self.total_customers = f"{self.cursor.fetchone()[0]}"

        except Exception as e:
            messagebox.showerror("Data Fetch Error", f"Error fetching stats:\n{str(e)}")

    def build_ui(self):
        # Top bar
        top_frame = tk.Frame(self.master, bg='#4ade80', height=60)
        top_frame.pack(fill='x')
        title = tk.Label(top_frame, text="Welcome to Dashboard", bg='#4ade80',
                         font=("Arial", 18, "bold"), fg='white')
        title.pack(pady=10)

        # Stats section
        stats_frame = tk.Frame(self.master, bg='white')
        stats_frame.pack(pady=30)

        # Add this line along with other stat cards
        self.create_stat_card(stats_frame, "Total Profit", f"Rs {self.get_total_profit():.2f}", "#1e3a8a")  # Dark blue
        self.create_stat_card(stats_frame, "Total Sales", self.total_sales, "#2563eb")  # Blue
        self.create_stat_card(stats_frame, "Items in Stock", self.items_in_stock, "#7c3aed")  # Violet
        self.create_stat_card(stats_frame, "Total Orders", self.total_orders, "#b91c1c")  # Red
        self.create_stat_card(stats_frame, "Customers", self.total_customers, "#065f46")  # Dark Green

        # Sales Chart Section
        chart_frame = tk.Frame(self.master, bg='white')
        chart_frame.pack(pady=30)

        chart_label = tk.Label(chart_frame, text="Monthly Sales Overview", font=("Arial", 16,"bold"), bg='white')
        chart_label.pack()

        self.plot_sales_chart(chart_frame)

        # Navigation button
        nav_button = tk.Button(self.master, text="Back to Home", command=self.go_back,
                               font=("Arial", 12), bg='red', fg='white', relief='ridge')
        nav_button.pack(pady=20)

    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, width=180, height=80, relief='raised', bd=2)
        card.pack_propagate(False)
        card.pack(side='left', padx=15)

        title_label = tk.Label(card, text=title, bg=color, font=("Arial", 10, "bold"), fg='white')
        title_label.pack()
        value_label = tk.Label(card, text=value, bg=color, font=("Arial", 16), fg='white')
        value_label.pack()

    def get_total_profit(self):
        try:
            query = '''
                SELECT SUM((oi.unit_price - i.cost_price) * oi.quantity) AS total_profit
                FROM order_items oi
                JOIN items i ON oi.item_id = i.item_id
            '''
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result[0] else 0
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching profit: {str(e)}")
            return 0

    def plot_sales_chart(self, parent):
        try:
            self.cursor.execute("""
                SELECT 
                    DATE_FORMAT(order_date, '%Y-%m') AS month,
                    SUM(total_amount) AS total
                FROM orders
                GROUP BY month
                ORDER BY month
            """)
            data = self.cursor.fetchall()
            months = [datetime.strptime(row[0], '%Y-%m').strftime('%b %Y') for row in data]
            totals = [row[1] for row in data]

            fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
            ax.plot(months, totals, marker='o', color='#4ade80')
            ax.set_title("Monthly Sales")
            ax.set_xlabel("Month")
            ax.set_ylabel("Total Sales (Rs)")
            ax.grid(True)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack()

        except Exception as e:
            messagebox.showerror("Chart Error", f"Failed to draw sales chart:\n{str(e)}")

    def go_back(self):
        self.master.destroy()
        import main
        main.start_main_ui()
