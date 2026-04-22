import csv
import importlib
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


THEME = {
    "bg": "#1a1a2e",
    "card_bg": "#16213e",
    "accent": "#4cc9f0",
    "text": "#ffffff",
    "secondary_text": "#a2a2c2",
}


class StatisticsScreen:
    """Statistics screen for viewing and exporting database records."""

    COLUMNS = (
        "id",
        "player_name",
        "round_number",
        "player_answer",
        "correct_max_flow",
        "result",
        "ford_fulkerson_time",
        "edmonds_karp_time",
        "created_at",
    )

    def __init__(self, root, on_back):
        self.root = root
        self.on_back = on_back
        self.rows = []
        self.filtered_rows = []

        self.frame = tk.Frame(root, bg=THEME["bg"], padx=20, pady=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self.frame, bg=THEME["card_bg"], padx=16, pady=14)
        container.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(container, bg=THEME["card_bg"])
        header.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            header,
            text="Game Statistics",
            font=("Arial", 18, "bold"),
            bg=THEME["card_bg"],
            fg=THEME["text"],
        ).pack(side=tk.LEFT)

        controls = tk.Frame(header, bg=THEME["card_bg"])
        controls.pack(side=tk.RIGHT)

        tk.Button(
            controls,
            text="Export to Excel",
            command=self.export_to_excel,
            font=("Arial", 10, "bold"),
            bg=THEME["accent"],
            fg=THEME["bg"],
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            controls,
            text="Back",
            command=self.on_back,
            font=("Arial", 10),
            bg=THEME["bg"],
            fg=THEME["text"],
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        filter_bar = tk.Frame(container, bg=THEME["card_bg"])
        filter_bar.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            filter_bar,
            text="Search player:",
            font=("Arial", 10),
            bg=THEME["card_bg"],
            fg=THEME["secondary_text"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._apply_filter)

        tk.Entry(
            filter_bar,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=24,
            bg=THEME["bg"],
            fg=THEME["text"],
            insertbackground=THEME["text"],
            relief=tk.FLAT,
        ).pack(side=tk.LEFT)

        self.summary_label = tk.Label(
            filter_bar,
            text="",
            font=("Arial", 10),
            bg=THEME["card_bg"],
            fg=THEME["secondary_text"],
            anchor="e",
        )
        self.summary_label.pack(side=tk.RIGHT)

        table_frame = tk.Frame(container, bg=THEME["card_bg"])
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            table_frame,
            columns=self.COLUMNS,
            show="headings",
            height=12,
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(
            container,
            orient=tk.HORIZONTAL,
            command=self.tree.xview,
        )
        scrollbar_x.pack(fill=tk.X, pady=(4, 0))

        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        heading_map = {
            "id": "ID",
            "player_name": "Player",
            "round_number": "Round",
            "player_answer": "Your Answer",
            "correct_max_flow": "Correct",
            "result": "Result",
            "ford_fulkerson_time": "Ford (s)",
            "edmonds_karp_time": "Edmonds (s)",
            "created_at": "Played At",
        }

        for col in self.COLUMNS:
            heading = heading_map[col]
            self.tree.heading(col, text=heading)
            if col == "player_name":
                width = 110
            elif col == "created_at":
                width = 170
            elif col in {"ford_fulkerson_time", "edmonds_karp_time"}:
                width = 95
            elif col in {"id", "round_number", "result"}:
                width = 70
            else:
                width = 90
            self.tree.column(col, width=width, anchor=tk.CENTER)

        self.status_label = tk.Label(
            container,
            text="No records loaded.",
            font=("Arial", 10),
            bg=THEME["card_bg"],
            fg=THEME["secondary_text"],
            anchor="w",
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def load_rows(self, rows):
        """Load database rows into the statistics table."""
        self.rows = rows or []
        self._apply_filter()

    def _apply_filter(self, *args):
        keyword = self.search_var.get().strip().lower()
        if keyword:
            self.filtered_rows = [
                row for row in self.rows if keyword in str(row[1]).lower()
            ]
        else:
            self.filtered_rows = list(self.rows)

        self.tree.delete(*self.tree.get_children())
        for row in self.filtered_rows:
            self.tree.insert("", tk.END, values=self._format_row_for_display(row))

        total = len(self.rows)
        shown = len(self.filtered_rows)
        self.summary_label.config(text=f"Showing {shown}/{total}")
        self.status_label.config(
            text="Tip: use Search player to quickly find a specific player."
        )

    def _format_row_for_display(self, row):
        return (
            row[0],
            row[1],
            row[2],
            row[4],
            row[5],
            row[6],
            self._format_seconds(row[7]),
            self._format_seconds(row[8]),
            row[9],
        )

    @staticmethod
    def _format_seconds(value):
        if value is None:
            return "N/A"
        return f"{value:.8f}"

    def export_to_excel(self):
        """Export records to an Excel-compatible file."""
        export_rows = self.filtered_rows if self.filtered_rows else self.rows
        if not export_rows:
            messagebox.showinfo("No Data", "There are no records to export.")
            return

        export_path = filedialog.asksaveasfilename(
            title="Export Statistics",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Workbook", "*.xlsx"),
                ("CSV (Excel compatible)", "*.csv"),
            ],
        )
        if not export_path:
            return

        extension = os.path.splitext(export_path)[1].lower()
        try:
            if extension == ".xlsx":
                self._export_xlsx(export_path, export_rows)
                messagebox.showinfo("Export Complete", f"Excel file saved:\n{export_path}")
            else:
                self._export_csv(export_path, export_rows)
                messagebox.showinfo("Export Complete", f"CSV file saved:\n{export_path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", f"Could not export data:\n{exc}")

    def _export_csv(self, export_path, rows):
        headers = [
            "id",
            "player_name",
            "round_number",
            "capacities",
            "player_answer",
            "correct_max_flow",
            "result",
            "ford_fulkerson_time",
            "edmonds_karp_time",
            "created_at",
        ]
        with open(export_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(
                    [
                        row[0],
                        row[1],
                        row[2],
                        self._pretty_capacity_json(row[3]),
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                    ]
                )

    def _export_xlsx(self, export_path, rows):
        try:
            openpyxl = importlib.import_module("openpyxl")
        except ImportError:
            fallback_path = os.path.splitext(export_path)[0] + ".csv"
            self._export_csv(fallback_path, rows)
            messagebox.showwarning(
                "openpyxl Not Installed",
                "Excel export requires 'openpyxl'. Exported CSV instead:\n"
                f"{fallback_path}",
            )
            return

        Workbook = openpyxl.Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Statistics"
        ws.append(
            [
                "id",
                "player_name",
                "round_number",
                "capacities",
                "player_answer",
                "correct_max_flow",
                "result",
                "ford_fulkerson_time",
                "edmonds_karp_time",
                "created_at",
            ]
        )

        for row in rows:
            ws.append(
                [
                    row[0],
                    row[1],
                    row[2],
                    self._pretty_capacity_json(row[3]),
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                ]
            )

        wb.save(export_path)

    @staticmethod
    def _pretty_capacity_json(raw_capacities):
        try:
            parsed = json.loads(raw_capacities)
            return ", ".join(f"{k}:{v}" for k, v in parsed.items())
        except Exception:
            return raw_capacities

    def destroy(self):
        self.frame.destroy()
