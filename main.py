import csv
import json
import os
import sys
import threading
import tkinter as tk
from dataclasses import asdict, dataclass
from tkinter import filedialog, messagebox, ttk
from typing import Literal

IS_PYINSTALLER = getattr(sys, "frozen", False)
if IS_PYINSTALLER:
    images_dir = os.path.join(sys._MEIPASS, "images")  # type: ignore
else:
    images_dir = os.path.join(os.path.dirname(__file__), "images")


@dataclass
class File:
    name: str
    path: str
    full_path: str
    size: int


@dataclass
class Results:
    terms: dict[str, list[File]]

    @property
    def total_files(self) -> int:
        """
        Get total number of files found across all search terms.
        """
        return sum(len(files) for files in self.terms.values())

    def as_dict(self) -> dict:
        """
        Convert results to a serializable dictionary.
        """
        return asdict(self)

    @property
    def csv_fieldnames(self) -> list[str]:
        """
        Get CSV field names for writing.
        """
        return ["Search Term", "Full Path", "Size"]

    def as_csv_rows(self) -> list[dict[str, str]]:
        """
        Convert results to a list of dictionaries for CSV writing.
        Each dictionary represents a row.
        """
        rows = []
        for term, files in self.terms.items():
            for f in files:
                rows.append(
                    {
                        "Search Term": term,
                        "Full Path": f.full_path,
                        "Size": str(f.size),
                    }
                )
        return rows


class FileFinderWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("File Finder 9000")
        self.root.iconbitmap(os.path.join(images_dir, "icon.ico"))
        self.root.geometry("500x450")
        root.resizable(True, False)

        # Variables
        self.everything_file_path = tk.StringVar()
        self.search_terms_path = tk.StringVar()
        self.ignore_extensions_str = tk.StringVar()
        self.exclude_shortcuts = tk.BooleanVar(value=True)
        self.dedupe_results = tk.BooleanVar(value=False)
        self.status_msg = tk.StringVar(value="Ready")

        self._results: Results | None = None  # To store search results in memory

        # --- Styles ---
        style = ttk.Style()
        style.configure("Gray_Foreground.TLabel", foreground="gray")
        style.configure("Blue_Foreground.TLabel", foreground="blue")

        # --- File Selection Section ---
        frame_files = ttk.Labelframe(self.root, text="Input Files", padding=10)
        frame_files.pack(fill=tk.X, padx=10, pady=5)
        frame_files.columnconfigure(1, weight=1)

        # Everything CSV Input
        ttk.Label(frame_files, text="Everything CSV File:").grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Entry(frame_files, textvariable=self.everything_file_path, width=40).grid(
            row=0, column=1, padx=5, sticky=tk.EW
        )
        ttk.Button(
            frame_files, text="Browse", command=self.browse_everything_file
        ).grid(row=0, column=2, sticky=tk.E)

        # Search Terms Input
        ttk.Label(frame_files, text="Search Terms List (txt):").grid(
            row=1, column=0, sticky=tk.W
        )
        ttk.Entry(frame_files, textvariable=self.search_terms_path, width=40).grid(
            row=1, column=1, padx=5, sticky=tk.EW
        )
        ttk.Button(frame_files, text="Browse", command=self.browse_terms_file).grid(
            row=1, column=2, sticky=tk.E
        )

        # --- Options Section ---
        frame_opts = ttk.Labelframe(self.root, text="Filters & Options", padding=10)
        frame_opts.pack(fill=tk.X, padx=10, pady=5)

        # Shortcuts
        ttk.Checkbutton(
            frame_opts, text="Exclude Shortcuts (.lnk)", variable=self.exclude_shortcuts
        ).grid(row=0, column=0, sticky=tk.W)

        # Dedupe
        ttk.Checkbutton(
            frame_opts,
            text="Deduplicate (by Name & Size)",
            variable=self.dedupe_results,
        ).grid(row=1, column=0, sticky=tk.W)

        # Extensions
        ttk.Label(frame_opts, text="Ignore Extensions (comma separated):").grid(
            row=2, column=0, sticky=tk.W, pady=(10, 0)
        )
        ttk.Entry(frame_opts, textvariable=self.ignore_extensions_str, width=50).grid(
            row=3, column=0, columnspan=2, sticky=tk.W
        )
        ttk.Label(
            frame_opts, text="Example: .xls, .pdf", style="Gray_Foreground.TLabel"
        ).grid(row=4, column=0, sticky=tk.W)

        # --- Action Section ---
        frame_action = ttk.Frame(self.root, padding=10)
        frame_action.pack(fill=tk.X, padx=10)

        self.btn_search = ttk.Button(
            frame_action, text="Run Search", command=self.start_search_thread
        )
        self.btn_search.pack(fill=tk.X, ipady=2)

        # Progress Bar
        self.progress = ttk.Progressbar(
            frame_action, orient=tk.HORIZONTAL, length=100, mode="determinate"
        )
        self.progress.pack(fill=tk.X, pady=10)

        # Status Label
        ttk.Label(
            frame_action, textvariable=self.status_msg, style="Blue_Foreground.TLabel"
        ).pack()

        # --- Export Section ---
        frame_export = ttk.Labelframe(self.root, text="Export Results", padding=10)
        frame_export.pack(fill=tk.X, padx=10, pady=5)

        self.btn_save_csv = ttk.Button(
            frame_export,
            text="Save as CSV",
            command=lambda: self.save_results("csv"),
            state=tk.DISABLED,
        )
        self.btn_save_csv.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.btn_save_json = ttk.Button(
            frame_export,
            text="Save as JSON",
            command=lambda: self.save_results("json"),
            state=tk.DISABLED,
        )
        self.btn_save_json.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)

    # --- File Dialog Helpers ---
    def browse_everything_file(self) -> None:
        """
        Open file dialog to select Everything CSV file.
        """
        filename = filedialog.askopenfilename(
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Everything Files", "*.efu"),
                ("All Files", "*.*"),
            ]
        )
        if filename:
            self.everything_file_path.set(filename)

    def browse_terms_file(self) -> None:
        """
        Open file dialog to select search terms text file.
        """
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            self.search_terms_path.set(filename)

    # --- Main Logic ---
    def start_search_thread(self) -> None:
        """
        Start the search in a separate thread to keep UI responsive.
        """

        # Validation
        if not os.path.exists(self.everything_file_path.get()):
            messagebox.showerror("Error", "Everything CSV file not found.")
            return

        if not os.path.exists(self.search_terms_path.get()):
            messagebox.showerror("Error", "Search terms file not found.")
            return

        # Disable buttons during search
        self.toggle_inputs(False)
        self._results = None

        # Start thread
        t = threading.Thread(target=self.run_search)
        t.daemon = True
        t.start()

    def run_search(self) -> None:
        """
        Execute the search logic.
        """
        try:
            everything_path = self.everything_file_path.get()
            terms_path = self.search_terms_path.get()

            # Load Everything CSV
            self.update_progress(0, 100)  # placeholder to reset progress bar

            # Count total lines for progress bar (First Pass)
            self.update_status("Counting rows in CSV...")
            with open(everything_path, "r", encoding="utf-8") as f:
                total_rows = sum(1 for row in f) - 1  # Subtract header

            # Load Search Terms
            self.update_status("Loading search terms...")
            with open(terms_path, "r", encoding="utf-8") as f:
                search_terms = [line.strip() for line in f if line.strip()]

            # deduplicate search terms and keep order
            search_terms = list(dict.fromkeys(search_terms))

            # Prepare filters
            ignore_exts = [
                x.strip().lower()
                for x in self.ignore_extensions_str.get().split(",")
                if x.strip()
            ]
            if self.exclude_shortcuts.get():
                ignore_exts.append(".lnk")

            do_dedupe = self.dedupe_results.get()

            # Search Logic
            self._results = Results(terms={term: [] for term in search_terms})
            self.update_status("Searching...")

            # Iterate through files looking for matches
            with open(everything_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    row: dict[str, str]
                    count += 1

                    if count % 1000 == 0:  # Update progress every 1000 rows
                        self.update_progress(count, total_rows)

                    # for csv files
                    name = row.get("Name")
                    path = row.get("Path")

                    # for .efu files
                    if name is None or path is None:
                        filename = row["Filename"]
                        name = os.path.basename(filename)
                        path = os.path.dirname(filename)

                    size = row.get("Size")

                    # Skip if size is missing (folders or other blank entries)
                    if not size or size == "0":
                        continue

                    name_lower = name.lower()

                    # 1. Check Extensions
                    is_ignored = False
                    for ext in ignore_exts:
                        if name_lower.endswith(ext):
                            is_ignored = True
                            break

                    if is_ignored:
                        continue

                    # 2. Check Match
                    for term in search_terms:
                        if term.lower() in name_lower:
                            self._results.terms[term].append(
                                File(
                                    name=name,
                                    path=path,
                                    full_path=os.path.join(path, name),
                                    size=int(size),
                                )
                            )

            # 3. Dedupe Results if needed
            if do_dedupe:
                self.update_status("Deduplicating results...")
                for term, files in self._results.terms.items():
                    seen = set()
                    deduped_files = []
                    for f in files:
                        identifier = (f.name, f.size)
                        if identifier not in seen:
                            seen.add(identifier)
                            deduped_files.append(f)
                    self._results.terms[term] = deduped_files

            self.search_complete(True, f"Found {self._results.total_files} files.")

        except Exception as e:
            self.search_complete(False, str(e))

    # --- UI Updaters (Thread Safe wrappers) ---
    def update_status(self, message: str) -> None:
        """
        Update status message in a thread-safe manner.
        """
        self.root.after(0, lambda: self.status_msg.set(message))

    def update_progress(self, current: int, total: int) -> None:
        """
        Update progress bar in a thread-safe manner.
        """
        if total > 0:
            perc = (current / total) * 100
            self.root.after(0, lambda: self.progress.configure(value=perc))

    def toggle_inputs(self, enable: bool) -> None:
        """
        Enable or disable input buttons.
        """
        state = tk.NORMAL if enable else tk.DISABLED
        self.btn_search.config(state=state)

        self.btn_save_csv.config(state=tk.DISABLED)  # Always disable save until done
        self.btn_save_json.config(state=tk.DISABLED)

    def search_complete(self, success: bool, message: str) -> None:
        """
        Handle search completion in a thread-safe manner.
        """

        def _finish():
            self.progress.configure(value=100)
            self.status_msg.set(message)
            self.toggle_inputs(True)

            if success:
                # Enable save buttons if we have results
                if self._results and self._results.total_files > 0:
                    self.btn_save_csv.config(state=tk.NORMAL)
                    self.btn_save_json.config(state=tk.NORMAL)
                else:
                    messagebox.showinfo("Result", "No matches found.")
            else:
                messagebox.showerror("Error", message)

        self.root.after(0, _finish)

    # --- Export ---
    def save_results(self, file_type: Literal["csv", "json"]) -> None:
        """
        Save results to CSV or JSON file.
        """
        if not self._results:
            return

        if file_type == "csv":
            f_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
            )
            if f_path:
                try:
                    with open(f_path, "w", encoding="utf-8") as f:
                        writer = csv.DictWriter(
                            f,
                            lineterminator="\n",
                            fieldnames=self._results.csv_fieldnames,
                        )
                        writer.writeheader()
                        writer.writerows(self._results.as_csv_rows())

                    messagebox.showinfo("Success", "Saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save: {e}")

        elif file_type == "json":
            f_path = filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("JSON Files", "*.json")]
            )
            if f_path:
                try:
                    with open(f_path, "w", encoding="utf-8") as f:
                        json.dump(self._results.as_dict(), f, indent=4)

                    messagebox.showinfo("Success", "Saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    app = FileFinderWindow(root)

    root.deiconify()
    root.mainloop()
