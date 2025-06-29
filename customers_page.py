import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class CustomerPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Overview")
        self.root.attributes('-fullscreen', True)
        self.connect_db()

        # Style customization
        self.style = ttk.Style()
        self.style.theme_use("default")

        # Configure heading style
        self.style.configure("Treeview.Heading",
                             font=("Arial", 12, "bold"),
                             foreground="white",
                             background="#4a7abc")  # Blue header

        # Configure row font and background
        self.style.configure("Treeview",
                             font=("Arial", 11),
                             rowheight=30,
                             background="white",
                             fieldbackground="white")

        self.style.map('Treeview',
                       background=[('selected', '#347083')])

        header_frame = tk.Frame(self.root, bg="#22c55e", height=60)
        header_frame.pack(fill='x')

        title = tk.Label(header_frame, text="Customer Purchase Ranking", font=("Arial", 18, "bold"),
                         bg="#22c55e", fg="white")
        title.pack(pady=15)

        # Treeview table with adjusted column widths
        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Email", "Phone", "Total Purchased"),
                                 show='headings', height=15)

        # Set column headings and widths
        self.tree.heading("ID", text="Customer ID")
        self.tree.column("ID", width=100, anchor="center")

        self.tree.heading("Name", text="Name")
        self.tree.column("Name", width=180, anchor="w")

        self.tree.heading("Email", text="Email")
        self.tree.column("Email", width=220, anchor="w")

        self.tree.heading("Phone", text="Phone")
        self.tree.column("Phone", width=150, anchor="center")

        self.tree.heading("Total Purchased", text="Total Purchased (Rs)")
        self.tree.column("Total Purchased", width=200, anchor="e")

        self.tree.tag_configure('oddrow', background="#f0f0f0")
        self.tree.tag_configure('evenrow', background="white")

        self.tree.pack(fill='both', expand=True, padx=20, pady=20)

        self.load_customers()

        # Back Button
        back_btn = tk.Button(root, text="Back", command=self.go_back, bg="red", fg="white", width=10)
        back_btn.pack(pady=10)

    def connect_db(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="supermarket_db"
        )
        self.cursor = self.conn.cursor()

    def load_customers(self):
        try:
            query = '''
                SELECT 
                    c.customer_id, 
                    c.name, 
                    c.email, 
                    c.phone,
                    COALESCE(SUM(o.total_amount), 0) AS total_purchased
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id
                ORDER BY total_purchased DESC
            '''
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Clear old rows
            for item in self.tree.get_children():
                self.tree.delete(item)

            for index, row in enumerate(rows):
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.tree.insert("", tk.END, values=row, tags=(tag,))

        except Exception as e:
            messagebox.showerror("Error", f"Error loading customers\n{str(e)}")

    def go_back(self):
        self.root.destroy()
        import main
        main.start_main_ui()
