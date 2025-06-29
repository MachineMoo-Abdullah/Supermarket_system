import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class ItemsPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Items")
        self.root.attributes('-fullscreen', True)
        self.create_db_table()

        # ============== Treeview Styling ==============
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4a7abc", foreground="white")
        self.style.configure("Treeview", font=("Arial", 11), rowheight=30, background="white", fieldbackground="white")
        self.style.map('Treeview', background=[('selected', '#347083')])

        # ============== Back Button ==============
        back_btn = tk.Button(root, text="Back", command=self.go_back, bg="red", fg="white", font=("Arial", 12, "bold"))
        back_btn.pack(pady=10)

        # ============== Top Frames ==============
        frame = tk.Frame(root)
        frame.pack(pady=10, fill='x')

        # ===== Add Item =====
        add_frame = tk.LabelFrame(frame, text="Add Item", padx=10, pady=10, font=("Arial", 14, "bold"))
        add_frame.pack(side="left", padx=(20, 10), anchor="w", expand=True)

        self.add_fields = {}
        labels = ["Name", "Category", "Price", "Quantity in Stock", "Cost Price"]
        add_entries = []

        for i, label in enumerate(labels):
            tk.Label(add_frame, text=label, font=("Arial", 12)).grid(row=i, column=0, sticky="w")
            entry = tk.Entry(add_frame, font=("Arial", 12), width=20)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.add_fields[label.lower().replace(" ", "_")] = entry
            add_entries.append(entry)

        for i in range(len(add_entries) - 1):
            add_entries[i].bind("<Return>", lambda e, next_entry=add_entries[i + 1]: next_entry.focus())
        add_entries[-1].bind("<Return>", lambda e: self.add_item())

        tk.Button(add_frame, text="Add", command=self.add_item, bg="green", fg="white", font=("Arial", 12, "bold")) \
            .grid(row=6, columnspan=2, pady=10)

        # ===== Update Item =====
        update_frame = tk.LabelFrame(frame, text="Update Item", padx=10, pady=10, font=("Arial", 14, "bold"))
        update_frame.pack(side="left", padx=(10, 10), anchor="center", expand=True)

        self.update_fields = {}

        tk.Label(update_frame, text="Item ID", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.update_id_entry = tk.Entry(update_frame, font=("Arial", 12), width=20)
        self.update_id_entry.grid(row=0, column=1)
        tk.Button(update_frame, text="Fetch", command=self.fetch_item_by_id, font=("Arial", 10)).grid(row=0, column=2,
                                                                                                      padx=5)
        self.update_id_entry.bind("<Return>", lambda event: self.fetch_item_by_id())

        for i, label in enumerate(labels):
            tk.Label(update_frame, text=label, font=("Arial", 12)).grid(row=i + 1, column=0, sticky="w")
            entry = tk.Entry(update_frame, font=("Arial", 12), width=20)
            entry.grid(row=i + 1, column=1, padx=5, pady=2)
            self.update_fields[label.lower().replace(" ", "_")] = entry

        tk.Button(update_frame, text="Update", command=self.update_item, bg="blue", fg="white",
                  font=("Arial", 12, "bold")) \
            .grid(row=7, columnspan=2, pady=10)

        # ===== Delete Item =====
        delete_frame = tk.LabelFrame(frame, text="Delete Item", padx=10, pady=10, font=("Arial", 14, "bold"))
        delete_frame.pack(side="right", padx=(10, 20), anchor="e", expand=True)

        tk.Label(delete_frame, text="Item ID", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.delete_id_entry = tk.Entry(delete_frame, font=("Arial", 12), width=20)
        self.delete_id_entry.grid(row=0, column=1)
        tk.Button(delete_frame, text="Delete", command=self.delete_item, bg="darkred", fg="white",
                  font=("Arial", 12, "bold")) \
            .grid(row=1, columnspan=2, pady=10)

        # ============== TreeView ==============
        table_frame = tk.Frame(root)
        table_frame.pack(pady=20, fill='both', expand=True)

        tree_scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_x.pack(side="bottom", fill="x")
        tree_scroll_y.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Category", "Price", "Quantity", "Utility", "Cost Price"),
            show='headings',
            xscrollcommand=tree_scroll_x.set,
            yscrollcommand=tree_scroll_y.set
        )
        tree_scroll_x.config(command=self.tree.xview)
        tree_scroll_y.config(command=self.tree.yview)

        self.tree.column("ID", width=50, anchor="center", stretch=True)
        self.tree.column("Name", width=150, anchor="w", stretch=True)
        self.tree.column("Category", width=120, anchor="w", stretch=True)
        self.tree.column("Price", width=100, anchor="center", stretch=True)
        self.tree.column("Quantity", width=120, anchor="center", stretch=True)
        self.tree.column("Utility", width=100, anchor="center", stretch=True)
        self.tree.column("Cost Price", width=120, anchor="center", stretch=True)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        self.tree.tag_configure('oddrow', background="#f0f0f0")
        self.tree.tag_configure('evenrow', background="white")

        self.tree.pack(fill='both', expand=True)
        self.load_items()

    def create_db_table(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="supermarket_db"
        )
        self.cursor = self.conn.cursor()

    def add_item(self):
        try:
            data = {k: v.get() for k, v in self.add_fields.items()}
            if not data["name"]:
                raise ValueError("Name cannot be empty")

            self.cursor.execute("SELECT * FROM items WHERE name=%s", (data["name"],))
            if self.cursor.fetchone():
                messagebox.showwarning("Exists", "Item already exists. Consider using update.")
                return

            self.cursor.execute('''
                INSERT INTO items (name, category, price, quantity_in_stock, cost_price, utility_score)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (data["name"], data["category"], float(data["price"]), int(data["quantity_in_stock"]), float(data["cost_price"]), 0.0))
            self.conn.commit()
            messagebox.showinfo("Success", "Item added successfully!")
            self.clear_fields(self.add_fields)
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def fetch_item_by_id(self):
        try:
            item_id = self.update_id_entry.get()
            self.cursor.execute("SELECT name, category, price, quantity_in_stock, cost_price FROM items WHERE item_id = %s", (item_id,))
            row = self.cursor.fetchone()
            if row:
                for key, value in zip(self.update_fields, row):
                    self.update_fields[key].delete(0, tk.END)
                    self.update_fields[key].insert(0, value)
            else:
                messagebox.showwarning("Not Found", "Item ID not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_item(self):
        try:
            item_id = self.update_id_entry.get()
            data = {k: v.get() for k, v in self.update_fields.items()}
            self.cursor.execute('''
                UPDATE items
                SET name=%s, category=%s, price=%s, quantity_in_stock=%s, cost_price=%s
                WHERE item_id=%s
            ''', (data["name"], data["category"], float(data["price"]), int(data["quantity_in_stock"]), float(data["cost_price"]), item_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Item updated successfully!")
            self.clear_fields(self.update_fields)
            self.update_id_entry.delete(0, tk.END)
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_item(self):
        try:
            item_id = self.delete_id_entry.get()
            if not item_id:
                raise ValueError("Please enter an item ID.")
            self.cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Item deleted successfully!")
            self.delete_id_entry.delete(0, tk.END)
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_items(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cursor.execute("SELECT * FROM items")
        rows = self.cursor.fetchall()
        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=row, tags=(tag,))

    def clear_fields(self, fields_dict):
        for entry in fields_dict.values():
            entry.delete(0, tk.END)

    def go_back(self):
        self.root.destroy()
        import main
        main.start_main_ui()
