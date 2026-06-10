import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd


n_df = "Name"
pr_df = "PreseasonRank"
y_df = "YearRank"
s_df = "Status"
p_df = "Program"


class SpartanLeaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spartan Leader Group Builder")
        self.root.geometry("800x700")

        self.df = None

        # IMPORTANT: use row index as source of truth
        self.check_vars = {}
        self.students = []
        self.selected_state = {}
        self.groups = []

        self.upload_screen()

    # ---------------- UI RESET ----------------
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------------- START SCREEN ----------------
    def upload_screen(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text="Spartan Leader Group Builder",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        tk.Button(
            self.root,
            text="Select Excel File",
            command=self.load_file,
            width=25,
            height=2
        ).pack(pady=20)

    # ---------------- LOAD FILE ----------------
    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )

        if not filepath:
            return

        try:
            self.df = pd.read_excel(filepath)
            self.prepare_data()
            self.reset_leaders()
            self.leader_selection_screen()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- DATA PREP ----------------
    def prepare_data(self):

        def col(letter):
            return self.df.columns[ord(letter.upper()) - ord('A')]

        preseason_col = col("P")
        yog_col = col("I")
        name_col = col("E")
        status_col = col("J")
        program_col = col("H")

        current_senior_yog = self.df[yog_col].min()

        self.df[pr_df] = self.df[preseason_col].apply(
            lambda x: 0 if str(x).strip().lower() == "no" else 1
        )

        self.df[y_df] = self.df[yog_col].apply(
            lambda x: 0 if x == current_senior_yog else 1
        )

        self.df[n_df] = self.df[name_col].fillna("").astype(str).str.strip()
        self.df[s_df] = self.df[status_col].fillna("").astype(str).str.strip()
        self.df[p_df] = self.df[program_col].fillna("").astype(str).str.strip()

        # Clean out cabinet members
        self.df = self.df[
            self.df[p_df].str.lower() != "cabinet"
        ]

        self.df = self.df.sort_values(by=[pr_df, y_df, s_df, n_df])

    # ---------------- LEADER SCREEN ----------------
    def leader_selection_screen(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text="Select Group Leaders",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.counter_label = tk.Label(
            self.root,
            text="Selected Leaders: 0",
            font=("Arial", 12, "bold")
        )
        self.counter_label.pack(pady=5)

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        scroll_frame = tk.Frame(canvas)

        window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll_frame.bind("<Configure>", on_configure)

        def resize(event):
            canvas.itemconfig(window, width=event.width)

        canvas.bind("<Configure>", resize)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # SIMPLE WORKING SCROLL (NO BROKEN BIND_ALL)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.check_vars = {}
        self.students = []

        # ---------------- BUILD LIST ----------------
        for i, row in self.df.iterrows():

            name = row[n_df]
            status = row[s_df]
            program = row[p_df]
            preseason = self.show_preseason(
                row[pr_df]
            )
            yog = self.show_yog(
                row[y_df]
            )

            var = tk.BooleanVar()
            var.set(self.selected_state.get(i, False))

            def make_callback(idx=i, v=var):
                def callback():
                    self.selected_state[idx] = v.get()
                    self.update_counter()
                return callback


            cb = tk.Checkbutton(
                scroll_frame,
                text=f"{name} | {yog} | {program} | {preseason} Preseason | {status}",
                variable=var,
                anchor="w",
                command=make_callback()
            )

            cb.pack(fill="x", padx=10)

            self.check_vars[i] = var
            self.students.append(name)

        self.update_counter()

        bottom = tk.Frame(self.root)
        bottom.pack(pady=10)

        tk.Button(
            bottom,
            text="Reset",
            command=self.reset_leaders
        ).pack(side="left", padx=5)

        tk.Button(
            bottom,
            text="Back",
            command=self.upload_screen
        ).pack(side="left", padx=5)

        tk.Button(
            bottom,
            text="Next",
            command=self.generate_groups
        ).pack(side="left", padx=5)

    # ---------------- COUNTER ----------------
    def update_counter(self):
        count = sum(self.selected_state.get(i, False) for i in self.check_vars)
        self.counter_label.config(text=f"Selected Leaders: {count}")

    def get_selected_count(self):
        return sum(self.selected_state.get(i, False) for i in self.check_vars)

    # ---------------- RESET ----------------
    def reset_leaders(self):
        self.selected_state = {}
        self.leader_selection_screen()

    # ---------------- GROUP GENERATION ----------------
    def generate_groups(self):
        selected = []

        for row_id, var in self.check_vars.items():

            if var.get():

                row = self.df.loc[row_id]

                selected.append({
                    "row_id": row_id,
                    "name": row[n_df],
                    "status": row[s_df],
                    "preseason": self.show_preseason(row[pr_df]),
                    "yog": self.show_yog(row[y_df]),
                    "program": row[p_df]
                })

        if len(selected) == 0:
            messagebox.showerror(
                "Error",
                "No leaders selected."
            )
            return

        self.show_groups(selected)

    # ---------------- GROUP SCREEN ----------------
    def show_groups(self, leaders):
        self.clear_screen()

        tk.Label(
            self.root,
            text="Leader Assignments",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        frame = tk.Frame(canvas)

        window = canvas.create_window((0, 0), window=frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_configure)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for idx, leader in enumerate(leaders, start=1):

            box = tk.LabelFrame(
                frame,
                text=f"Group {idx}",
                padx=10,
                pady=10
            )

            box.pack(fill="x", padx=20, pady=5)

            tk.Label(
                box,
                text=(
                    f"⭐ {leader['name']} | "
                    f"{leader['yog']} | "
                    f"{leader["program"]} | "
                    f"{leader['preseason']} Preseason | "
                    f"{leader['status']}"
                ),
                font=("Arial", 12)
            ).pack(anchor="w")

        tk.Button(
            self.root,
            text="Back",
            command=self.leader_selection_screen
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Start Over",
            command=self.upload_screen
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Generate Groups",
            command=self.generate_full_groups
        ).pack(pady=10)

    def show_preseason(self, val):
        return "Yes" if int(val) == 1 else "No"

    def show_yog(self, val):
        return "Senior" if int(val) == 0 else "Junior"

    def generate_full_groups(self):
        self.groups = []

        leader_row_ids = []

        for row_id, var in self.check_vars.items():
            if var.get():
                leader_row_ids.append(row_id)

                self.groups.append({
                    "leader_row": row_id,
                    "rows": [row_id]
                })

        remaining = [
            row_id
            for row_id in self.df.index
            if row_id not in leader_row_ids
        ]

        remaining.sort(
            key=lambda r: (
                self.df.loc[r, pr_df],
                self.df.loc[r, y_df]
            ),
            reverse=True
        )

        for row_id in remaining:

            smallest_size = min(
                len(group["rows"])
                for group in self.groups
            )

            eligible_groups = [
                i
                for i, group in enumerate(self.groups)
                if len(group["rows"]) == smallest_size
            ]

            best_group = eligible_groups[0]
            best_score = float("inf")

            for group_idx in eligible_groups:

                group = self.groups[group_idx]

                candidate = self.df.loc[row_id]

                candidate_program = str(candidate[p_df]).strip().lower()
                candidate_status = str(candidate[s_df]).strip().lower()

                program_count = 0
                status_count = 0

                for r in group["rows"]:

                    row = self.df.loc[r]

                    if str(row[p_df]).strip().lower() == candidate_program:
                        program_count += 1

                    if str(row[s_df]).strip().lower() == candidate_status:
                        status_count += 1

                preseason_count = sum(
                    self.df.loc[r, pr_df]
                    for r in group["rows"]
                )

                yog_count = sum(
                    self.df.loc[r, y_df]
                    for r in group["rows"]
                )

                group_size = len(group["rows"])

                preseason_ratio = preseason_count / group_size
                yog_ratio = yog_count / group_size

                score = 0

                # Keep groups same size
                score += group_size * 5

                # Balance preseason
                score += abs(preseason_ratio - 0.5) * 10

                # Balance senior/junior
                score += abs(yog_ratio - 0.5) * 10

                # Penalize duplicate programs
                score += program_count * 8

                # Penalize duplicate statuses
                score += status_count * 8

                if score < best_score:
                    best_score = score
                    best_group = group_idx

            self.groups[best_group]["rows"].append(row_id)

        self.display_final_groups()
    
    def find_best_group(self, row_id):
        candidate = self.df.loc[row_id]

        best_group = 0
        best_score = float("inf")

        ideal_size = len(self.df) / len(self.groups)

        for i, group in enumerate(self.groups):

            score = 0

            # ------------------
            # GROUP SIZE WEIGHT
            # ------------------
            size = len(group["members"])

            score += size * 50

            # ------------------
            # PRESEASON BALANCE
            # ------------------
            preseason_count = sum(
                self.df.loc[r, pr_df]
                for r in group["rows"]
                if r is not None
            )

            preseason_ratio = preseason_count / max(1, len(group["rows"]))

            score += abs(preseason_ratio - 0.5) * 20

            # ------------------
            # SENIOR/JUNIOR BALANCE
            # ------------------
            yog_count = sum(
                self.df.loc[r, y_df]
                for r in group["rows"]
                if r is not None
            )

            yog_ratio = yog_count / max(1, len(group["rows"]))

            score += abs(yog_ratio - 0.5) * 20

            # ------------------
            # CANDIDATE FIT
            # ------------------
            if candidate[pr_df] == 1:
                score -= 3

            if candidate[y_df] == 1:
                score -= 3

            if score < best_score:
                best_score = score
                best_group = i

        return best_group
    
    def display_final_groups(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text="Generated Groups",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        frame = tk.Frame(canvas)

        canvas_window = canvas.create_window(
            (0, 0),
            window=frame,
            anchor="nw"
        )

        def configure_scroll(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        frame.bind("<Configure>", configure_scroll)

        def resize(event):
            canvas.itemconfig(
                canvas_window,
                width=event.width
            )

        canvas.bind("<Configure>", resize)

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        def wheel(event):
            canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        canvas.bind_all("<MouseWheel>", wheel)

        # ------------------
        # GROUPS
        # ------------------

        for idx, group in enumerate(self.groups, start=1):

            box = tk.LabelFrame(
                frame,
                text=f"Group {idx}",
                padx=10,
                pady=10
            )

            box.pack(
                fill="x",
                padx=20,
                pady=5
            )

            for pos, row_id in enumerate(group["rows"]):
                row = self.df.loc[row_id]

                name = row[n_df]
                status = row[s_df]

                preseason = self.show_preseason(
                    row[pr_df]
                )

                yog = self.show_yog(
                    row[y_df]
                )

                program = row[p_df]

                text = (
                    f"{name} | "
                    f"{yog} | "
                    f"{program} | "
                    f"{preseason} Preseason | "
                    f"{status}"
                )

                if pos == 0:
                    text = "⭐ " + text

                row_frame = tk.Frame(box)
                row_frame.pack(fill="x", pady=1)

                tk.Label(
                    row_frame,
                    text=text,
                    anchor="w",
                    width=60
                ).pack(side="left")

                # Leaders can't move
                if pos != 0:

                    group_var = tk.StringVar()
                    group_var.set(f"Group {idx}")

                    group_choices = [
                        f"Group {g}"
                        for g in range(1, len(self.groups) + 1)
                    ]

                    dropdown = tk.OptionMenu(
                        row_frame,
                        group_var,
                        *group_choices,
                        command=lambda selected,
                                    row_id=row_id,
                                    current_group=idx-1:
                            self.move_student(
                                row_id,
                                current_group,
                                int(selected.split()[1]) - 1
                            )
                    )

                    dropdown.pack(side="right")

        button_row = tk.Frame(self.root)
        button_row.pack(pady=10)

        tk.Button(
            button_row,
            text="Back",
            command=self.leader_selection_screen
        ).pack(side="left", padx=5)

        tk.Button(
            button_row,
            text="Start Over",
            command=self.upload_screen
        ).pack(side="left", padx=5)

        tk.Button(
            button_row,
            text="Export Excel",
            command=self.export_groups_to_excel
        ).pack(side="left", padx=5)

    def move_student(self, row_id, old_group_idx, new_group_idx):
        if old_group_idx == new_group_idx:
            return

        if row_id == self.groups[old_group_idx]["leader_row"]:
            messagebox.showwarning(
                "Leader Move Blocked",
                "Leaders cannot be moved."
            )
            return

        self.groups[old_group_idx]["rows"].remove(row_id)
        self.groups[new_group_idx]["rows"].append(row_id)

        self.display_final_groups()

    # ---------------- EXPORT SECTION ----------------
    def export_groups_to_excel(self):
        if not self.groups:
            messagebox.showerror(
                "Error",
                "No groups generated yet."
            )
            return

        rows = []

        for group_num, group in enumerate(self.groups, start=1):

            for pos, row_id in enumerate(group["rows"]):

                row = self.df.loc[row_id]

                rows.append({
                    "Group": group_num,
                    "Leader": "Yes" if pos == 0 else "No",
                    "Name": row[n_df],
                    "Program": row[p_df],
                    "Senior/Junior": self.show_yog(row[y_df]),
                    "Preseason": self.show_preseason(row[pr_df]),
                    "Status": row[s_df]
                })

        export_df = pd.DataFrame(rows)

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile="Spartan_Groups.xlsx"
        )

        if not filename:
            return

        try:
            with pd.ExcelWriter(
                filename,
                engine="openpyxl"
            ) as writer:

                export_df.to_excel(
                    writer,
                    sheet_name="Groups",
                    index=False
                )

            messagebox.showinfo(
                "Success",
                f"Groups exported to:\n{filename}"
            )

        except Exception as e:
            messagebox.showerror(
                "Export Error",
                str(e)
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = SpartanLeaderApp(root)
    root.mainloop()