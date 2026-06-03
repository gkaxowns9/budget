import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os

class BudgetApp:
    def __init__(self, root:tk.Tk):
        self.root = root
        self.root.title("파이썬 가계부 (Budget Manager)")
        self.root.geometry("620x520")
        
        self.data_file = "data.json"
        self.records = self.load_data()
        
        self.setup_ui()
        self.update_treeview()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        # 입력 프레임
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(fill="x")
        
        tk.Label(input_frame, text="날짜 선택:").grid(row=0, column=0)
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue',foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', enable_wheel_on_calendar=True)
        self.date_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(input_frame, text="항목:").grid(row=0, column=2)
        self.item_entry = tk.Entry(input_frame)
        self.item_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(input_frame, text="금액:").grid(row=1, column=0, pady=5)
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(input_frame, text="분류:").grid(row=1, column=2)
        self.category_var = tk.StringVar(value="지출")
        tk.OptionMenu(input_frame, self.category_var, "수입", "지출").grid(row=1, column=3, padx=5)
        
        tk.Button(input_frame, text="추가", command=self.add_record, width=10).grid(row=0, column=4, rowspan=2, padx=10)

        filter_frame=tk.Frame(self.root, padx=10, pady=5)
        filter_frame.pack(fill="x")

        tk.Label(filter_frame, text="필터").pack(side="left", padx=5)

        self.filter_var = tk.StringVar(value="전체")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=["전체", "수입", "지출"], width=12, state="readonly")
        self.filter_combo.pack(side="left", padx=5)

        # 리스트 프레임 (Treeview)
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("date", "category", "item", "amount")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("date", text="날짜")
        self.tree.heading("category", text="분류")
        self.tree.heading("item", text="항목")
        self.tree.heading("amount", text="금액")
        self.tree.column("amount", anchor="e")
        self.tree.pack(fill="both", expand=True)
        
        # 삭제 버튼 및 잔액 표시
        bottom_frame = tk.Frame(self.root, pady=10)
        bottom_frame.pack(fill="x", padx=10)
        
        tk.Button(bottom_frame, text="선택 삭제", command=self.delete_record).pack(side="left")
        
        self.balance_label = tk.Label(bottom_frame, text="현재 잔액: 0원", font=("Arial", 12, "bold"))
        self.balance_label.pack(side="right")

    def add_record(self):
        date = self.date_entry.get()
        item = self.item_entry.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        
        if not item or not amount:
            messagebox.showwarning("경고", "항목과 금액을 입력해주세요.")
            return
            
        try:
            amount = int(amount)
        except ValueError:
            messagebox.showwarning("경고", "금액은 숫자만 입력 가능합니다.")
            return
            
        self.records.append({
            "date": date,
            "category": category,
            "item": item,
            "amount": amount
        })
        self.save_data()
        self.update_treeview()
        
        # 입력창 초기화 (날짜 제외)
        self.item_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def delete_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("경고", "삭제할 항목을 선택해주세요.")
            return
            
        for item in selected_item:
            # Treeview의 인덱스를 사용하여 records에서 삭제
            idx = self.tree.index(item)
            del self.records[idx]
            
        self.save_data()
        self.update_treeview()

    def update_treeview(self):
        # 기존 내용 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_balance = 0
        for r in self.records:
            self.tree.insert("", "end", values=(r["date"], r["category"], r["item"], f"{r['amount']:,}"))
            if r["category"] == "수입":
                total_balance += r["amount"]
            else:
                total_balance -= r["amount"]
                
        self.balance_label.config(text= f"현재 잔액: {total_balance:,}원")

    def on_closing(self):
        if messagebox.askokcancel("종료","가계부를 종료하시겠습니까?"):
            self.root.destroy()

root = tk.Tk()
app = BudgetApp(root)
root.mainloop()
