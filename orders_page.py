import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector


class OrdersPage:
    def __init__(self, root):
        self.root = root
        self.root.title("All Orders")
        self.root.attributes('-fullscreen', True)

        self.connect_db()

        # ============== Styling ==============
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4a7abc", foreground="white")
        self.style.configure("Treeview", font=("Arial", 11), rowheight=30, background="white", fieldbackground="white")
        self.style.map('Treeview', background=[('selected', '#347083')])

        # ============== Title ==============
        title = tk.Label(root, text="Orders Overview", font=("Arial", 20, "bold"))
        title.pack(pady=15)

        # ============== Filter Section ==============
        filter_frame = tk.LabelFrame(root, text="Filter Orders", padx=10, pady=10, font=("Arial", 13, "bold"))
        filter_frame.pack(pady=10, padx=20, fill='x')

        tk.Label(filter_frame, text="Select Date:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        self.date_picker = DateEntry(filter_frame, date_pattern='yyyy-mm-dd', font=("Arial", 11))
        self.date_picker.grid(row=0, column=1, padx=10)

        tk.Label(filter_frame, text="Select Month:", font=("Arial", 12)).grid(row=0, column=2, padx=10)
        self.month_picker = DateEntry(filter_frame, date_pattern='yyyy-mm-dd', font=("Arial", 11))
        self.month_picker.grid(row=0, column=3, padx=10)

        filter_btn = tk.Button(filter_frame, text="Apply Filter", command=self.apply_filter, bg="green", fg="white", font=("Arial", 11, "bold"))
        filter_btn.grid(row=0, column=4, padx=15)

        reset_btn = tk.Button(filter_frame, text="Reset", command=self.load_orders, bg="orange", fg="white", font=("Arial", 11, "bold"))
        reset_btn.grid(row=0, column=5, padx=5)

        # ============== Orders Table ==============
        table_frame = tk.Frame(root)
        table_frame.pack(pady=20, fill='both', expand=True, padx=20)

        tree_scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_x.pack(side="bottom", fill="x")
        tree_scroll_y.pack(side="right", fill="y")

        columns = ("Order ID", "Items", "Total Amount", "Order Date")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            xscrollcommand=tree_scroll_x.set,
            yscrollcommand=tree_scroll_y.set
        )

        tree_scroll_x.config(command=self.tree.xview)
        tree_scroll_y.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=200)

        self.tree.tag_configure('oddrow', background="#f0f0f0")
        self.tree.tag_configure('evenrow', background="white")

        self.tree.pack(fill='both', expand=True)

        self.load_orders()

        # ============== Back Button ==============
        back_btn = tk.Button(root, text="Back", command=self.go_back, bg="red", fg="white", width=10, font=("Arial", 12, "bold"))
        back_btn.pack(pady=10)

    def connect_db(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="supermarket_db"
        )
        self.cursor = self.conn.cursor()

    def load_orders(self):
        try:
            query = '''
                SELECT 
                    o.order_id,
                    GROUP_CONCAT(i.name SEPARATOR ', ') AS item_names,
                    o.total_amount,
                    o.order_date
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN items i ON oi.item_id = i.item_id
                GROUP BY o.order_id
                ORDER BY o.order_date DESC
            '''
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.populate_table(rows)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading orders\n{str(e)}")

    def apply_filter(self):
        date_value = self.date_picker.get_date().strftime('%Y-%m-%d')
        month_value = self.month_picker.get_date().month

        query = '''
            SELECT 
                o.order_id,
                GROUP_CONCAT(i.name SEPARATOR ', ') AS item_names,
                o.total_amount,
                o.order_date
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN items i ON oi.item_id = i.item_id
            WHERE DATE(o.order_date) = %s OR MONTH(o.order_date) = %s
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
        '''
        try:
            self.cursor.execute(query, (date_value, month_value))
            rows = self.cursor.fetchall()
            self.populate_table(rows)
        except Exception as e:
            messagebox.showerror("Error", f"Error applying filter\n{str(e)}")

    def populate_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=row, tags=(tag,))

    def go_back(self):
        self.root.destroy()
        import main
        main.start_main_ui()
