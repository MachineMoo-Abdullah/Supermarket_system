import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


class FrequentPatternsPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Frequent Item Combinations")
        self.root.attributes('-fullscreen', True)

        self.connect_db()
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        analyze_btn = tk.Button(button_frame, text="Analyze Frequent Patterns", command=self.analyze_patterns,
                                font=("Arial", 12, "bold"), bg="#4ade80", fg="black", padx=10, pady=5)
        analyze_btn.pack(side="left", padx=20)

        back_btn = tk.Button(button_frame, text="Back", command=self.go_back,
                             bg="red", fg="white", width=10, font=("Arial", 12, "bold"))
        back_btn.pack(side="left", padx=10)
        # ============ Styling ============
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4a7abc", foreground="white")
        style.configure("Treeview", font=("Arial", 11), rowheight=30, background="white", fieldbackground="white")
        style.map('Treeview', background=[('selected', '#347083')])

        # ============ Title ============
        title = tk.Label(root, text="Frequent Itemset Analysis", font=("Arial", 20, "bold"))
        title.pack(pady=15)

        # ============ Frequent Patterns Table ============
        table_frame = tk.Frame(root)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ("Items", "Support")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        self.tree.heading("Items", text="Items")
        self.tree.column("Items", anchor='w', width=500, stretch=True)
        self.tree.heading("Support", text="Support (%)")
        self.tree.column("Support", anchor='center', width=150)

        self.tree.tag_configure('oddrow', background="#f0f0f0")
        self.tree.tag_configure('evenrow', background="white")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side='left', fill='both', expand=True)

        # ============ Association Rules Table ============
        rules_label = tk.Label(root, text="Association Rules", font=("Arial", 16, "bold"))
        rules_label.pack(pady=(10, 5))

        rules_frame = tk.Frame(root)
        rules_frame.pack(fill='both', expand=True, padx=20, pady=10)

        rules_columns = ("If Items", "Then Items", "Confidence (%)", "Lift")
        self.rules_tree = ttk.Treeview(rules_frame, columns=rules_columns, show='headings', height=8)

        for col in rules_columns:
            self.rules_tree.heading(col, text=col)
            self.rules_tree.column(col, anchor='center', width=200)

        rules_vsb = ttk.Scrollbar(rules_frame, orient="vertical", command=self.rules_tree.yview)
        rules_hsb = ttk.Scrollbar(rules_frame, orient="horizontal", command=self.rules_tree.xview)
        self.rules_tree.configure(yscrollcommand=rules_vsb.set, xscrollcommand=rules_hsb.set)

        rules_vsb.pack(side='right', fill='y')
        rules_hsb.pack(side='bottom', fill='x')
        self.rules_tree.pack(side='left', fill='both', expand=True)

        # ============ Buttons ============


    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="supermarket_db"
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database:\n{str(e)}")
            self.root.destroy()

    def fetch_transactions(self):
        try:
            query = '''
                SELECT o.order_id, i.name
                FROM order_items oi
                JOIN items i ON oi.item_id = i.item_id
                JOIN orders o ON oi.order_id = o.order_id
            '''
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            transactions = {}
            for order_id, item_name in rows:
                transactions.setdefault(order_id, []).append(item_name)

            return list(transactions.values())
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching transactions\n{str(e)}")
            return []

    def analyze_patterns(self):
        transactions = self.fetch_transactions()
        if not transactions:
            return

        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        frequent_itemsets = apriori(df, min_support=0.2, use_colnames=True)

        if frequent_itemsets.empty:
            messagebox.showinfo("No Patterns", "No frequent itemsets found with the current support threshold.")
            return

        frequent_itemsets = frequent_itemsets.sort_values(by='support', ascending=False)

        self.tree.delete(*self.tree.get_children())
        self.rules_tree.delete(*self.rules_tree.get_children())

        for idx, (_, row) in enumerate(frequent_itemsets.iterrows()):
            items = ', '.join(sorted(list(row['itemsets'])))
            support = round(row['support'] * 100, 2)
            tag = 'oddrow' if idx % 2 != 0 else 'evenrow'
            self.tree.insert("", tk.END, values=(items, f"{support}%"), tags=(tag,))

        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)

        for _, rule in rules.iterrows():
            lhs = ', '.join(sorted(list(rule['antecedents'])))
            rhs = ', '.join(sorted(list(rule['consequents'])))
            confidence = round(rule['confidence'] * 100, 2)
            lift = round(rule['lift'], 2)
            self.rules_tree.insert("", tk.END, values=(lhs, rhs, f"{confidence}%", lift))

    def go_back(self):
        self.root.destroy()
        try:
            import main
            main.start_main_ui()
        except Exception as e:
            messagebox.showerror("Navigation Error", f"Unable to return to main UI.\n{str(e)}")
