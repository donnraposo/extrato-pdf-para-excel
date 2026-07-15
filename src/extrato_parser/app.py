from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .service import convert_statement


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Extrato Parser")
        self.geometry("650x300")
        self.minsize(560, 280)
        self.pdf_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="Selecione um extrato bancário em PDF.")
        self.messages: queue.Queue[tuple[str, object]] = queue.Queue()
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Extrato bancário em PDF", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.pdf_path).grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Button(frame, text="Selecionar PDF", command=self._choose_pdf).grid(row=1, column=2, padx=(8, 0))

        ttk.Label(frame, text="Arquivo Excel de saída", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, columnspan=3, sticky="w", pady=(18, 8))
        ttk.Entry(frame, textvariable=self.output_path).grid(row=3, column=0, columnspan=2, sticky="ew")
        ttk.Button(frame, text="Escolher destino", command=self._choose_output).grid(row=3, column=2, padx=(8, 0))

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(20, 8))
        ttk.Label(frame, textvariable=self.status, wraplength=600).grid(row=5, column=0, columnspan=3, sticky="w")
        self.convert_button = ttk.Button(frame, text="Gerar Excel", command=self._start)
        self.convert_button.grid(row=6, column=2, sticky="e", pady=(18, 0))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def _choose_pdf(self) -> None:
        chosen = filedialog.askopenfilename(title="Selecione o extrato", filetypes=[("PDF", "*.pdf")])
        if chosen:
            self.pdf_path.set(chosen)
            self.output_path.set(str(Path(chosen).with_suffix(".xlsx")))

    def _choose_output(self) -> None:
        chosen = filedialog.asksaveasfilename(title="Salvar Excel", defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if chosen:
            self.output_path.set(chosen)

    def _start(self) -> None:
        if not self.pdf_path.get() or not self.output_path.get():
            messagebox.showwarning("Campos obrigatórios", "Selecione o PDF e o destino do Excel.")
            return
        self.convert_button.configure(state="disabled")
        self.progress.start(10)
        self.status.set("Processando o extrato...")
        threading.Thread(target=self._run, daemon=True).start()
        self.after(100, self._poll)

    def _run(self) -> None:
        try:
            result = convert_statement(Path(self.pdf_path.get()), Path(self.output_path.get()))
            self.messages.put(("ok", result))
        except Exception as exc:
            self.messages.put(("error", str(exc)))

    def _poll(self) -> None:
        try:
            kind, payload = self.messages.get_nowait()
        except queue.Empty:
            self.after(100, self._poll)
            return
        self.progress.stop()
        self.convert_button.configure(state="normal")
        if kind == "error":
            self.status.set("Não foi possível concluir o processamento.")
            messagebox.showerror("Erro", str(payload))
            return
        result = payload
        reviews = result.metadata.get("Itens para conferência", 0)
        text = f"Excel criado com {len(result.entries)} lançamentos. Itens para conferência: {reviews}."
        self.status.set(text)
        messagebox.showinfo("Concluído", text)


def main() -> None:
    Application().mainloop()


if __name__ == "__main__":
    main()
