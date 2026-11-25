"""Interface gráfica Tkinter para o Simulador de Parque de Estacionamento."""

from __future__ import annotations

from datetime import datetime
import math
import tkinter as tk
from tkinter import messagebox, ttk

from app.armazenamento import carregar_parque, guardar_parque
from app.dados import CAPACIDADE_MAXIMA, CAPACIDADE_MINIMA
from app.logica import (
    avancar_relogio,
    configurar_tarifa,
    criar_novo_parque,
    obter_estatisticas,
    obter_hora_atual,
    reconfigurar_capacidade,
    registar_entrada,
    registar_saida,
    simular_saida,
)

COR_FUNDO = "#1A2228"
COR_PAINEL = "#232E36"
COR_CARD = "#2C3942"
COR_DESTAQUE = "#F4D03F"
COR_VERDE = "#27AE60"
COR_TEXTO = "#ECF0F1"
COR_SEC = "#AEB6BF"


class AplicacaoParqueEstacionamento:
    """Controlador da interface do Parking Manager."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Parking Manager — Gestão de Parque de Estacionamento")
        self.raiz.geometry("1180x760")
        self.raiz.minsize(1040, 670)
        self.raiz.configure(bg=COR_FUNDO)

        self.estado = criar_novo_parque()

        self._configurar_estilos()
        self._construir_interface()
        self.atualizar_interface()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=COR_FUNDO)
        estilo.configure("Painel.TFrame", background=COR_PAINEL)
        estilo.configure("Card.TFrame", background=COR_CARD)
        estilo.configure(
            "Titulo.TLabel",
            background=COR_PAINEL,
            foreground=COR_DESTAQUE,
            font=("Segoe UI", 14, "bold"),
        )
        estilo.configure(
            "Sub.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
        )
        estilo.configure(
            "Txt.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Sec.TLabel",
            background=COR_PAINEL,
            foreground=COR_SEC,
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Amarelo.TButton",
            background=COR_DESTAQUE,
            foreground="#1A1A1A",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        estilo.map("Amarelo.TButton", background=[("active", "#F7DC6F")])
        estilo.configure(
            "Acao.TButton",
            background="#3B4B57",
            foreground=COR_TEXTO,
            font=("Segoe UI", 9, "bold"),
            padding=5,
        )
        estilo.map("Acao.TButton", background=[("active", "#4E6270")])
        estilo.configure(
            "Ocupacao.Horizontal.TProgressbar",
            troughcolor="#12181C",
            background=COR_DESTAQUE,
            thickness=14,
        )
        estilo.configure(
            "Treeview",
            background="#171E24",
            foreground=COR_TEXTO,
            fieldbackground="#171E24",
            rowheight=24,
        )
        estilo.configure(
            "Treeview.Heading",
            background=COR_CARD,
            foreground=COR_DESTAQUE,
            font=("Segoe UI", 9, "bold"),
        )

    def _construir_interface(self) -> None:
        # Barra superior: Relógio de simulação + controlos temporais + persistência
        topo = ttk.Frame(self.raiz, style="Painel.TFrame", padding=(14, 10))
        topo.pack(fill=tk.X, padx=10, pady=(10, 6))

        self.lbl_relogio = ttk.Label(topo, text="", style="Titulo.TLabel")
        self.lbl_relogio.pack(side=tk.LEFT)

        frame_tempo = ttk.Frame(topo, style="Painel.TFrame")
        frame_tempo.pack(side=tk.LEFT, padx=18)
        for texto, mins in [("+15 min", 15), ("+30 min", 30), ("+1 hora", 60), ("+3 horas", 180)]:
            ttk.Button(
                frame_tempo,
                text=texto,
                style="Acao.TButton",
                command=lambda m=mins: self._acao_avancar_tempo(m),
            ).pack(side=tk.LEFT, padx=3)

        btns_topo = ttk.Frame(topo, style="Painel.TFrame")
        btns_topo.pack(side=tk.RIGHT)
        ttk.Button(btns_topo, text="Novo Parque", style="Acao.TButton", command=self._acao_novo).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns_topo, text="Guardar", style="Acao.TButton", command=self._acao_guardar).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btns_topo, text="Carregar", style="Acao.TButton", command=self._acao_carregar).pack(
            side=tk.LEFT, padx=4
        )

        corpo = ttk.Frame(self.raiz)
        corpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Coluna esquerda: Planta visual do parque + Estatísticas
        col_esq = ttk.Frame(corpo, style="Painel.TFrame", padding=12)
        col_esq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        ttk.Label(
            col_esq, text="Planta Superior do Parque de Estacionamento", style="Sub.TLabel"
        ).pack(anchor=tk.W, pady=(0, 6))

        self.canvas_parque = tk.Canvas(
            col_esq,
            height=410,
            bg="#2B3035",
            highlightthickness=1,
            highlightbackground=COR_DESTAQUE,
        )
        self.canvas_parque.pack(fill=tk.BOTH, expand=True)
        self.canvas_parque.bind("<Configure>", lambda _e: self._desenhar_parque())
        self.canvas_parque.bind("<Button-1>", self._ao_clicar_lugar)

        # Barra de ocupação e métricas
        frame_stats = ttk.Frame(col_esq, style="Card.TFrame", padding=10)
        frame_stats.pack(fill=tk.X, pady=(8, 0))

        linha_oc = ttk.Frame(frame_stats, style="Card.TFrame")
        linha_oc.pack(fill=tk.X)
        self.lbl_ocupacao = ttk.Label(
            linha_oc,
            text="",
            background=COR_CARD,
            foreground=COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
        )
        self.lbl_ocupacao.pack(side=tk.LEFT)
        self.barra_ocupacao = ttk.Progressbar(
            linha_oc, style="Ocupacao.Horizontal.TProgressbar", maximum=100
        )
        self.barra_ocupacao.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(12, 0))

        self.lbl_metricas = ttk.Label(
            frame_stats,
            text="",
            background=COR_CARD,
            foreground=COR_DESTAQUE,
            font=("Segoe UI", 10),
        )
        self.lbl_metricas.pack(anchor=tk.W, pady=(6, 0))

        # Coluna direita: Operações, Lista de veículos, Configuração e Histórico
        col_dir = ttk.Frame(corpo, style="Painel.TFrame", padding=12, width=480)
        col_dir.pack(side=tk.RIGHT, fill=tk.BOTH)
        col_dir.pack_propagate(False)

        # Cartão Entrada
        card_ent = ttk.Frame(col_dir, style="Card.TFrame", padding=10)
        card_ent.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            card_ent,
            text="Entrada de Veículo (ex.: AA-00-AA, 12-BC-34)",
            background=COR_CARD,
            foreground=COR_DESTAQUE,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W)

        linha_ent = ttk.Frame(card_ent, style="Card.TFrame")
        linha_ent.pack(fill=tk.X, pady=(6, 0))
        self.var_matricula_entrada = tk.StringVar()
        ttk.Entry(linha_ent, textvariable=self.var_matricula_entrada, width=18, font=("Consolas", 11)).pack(
            side=tk.LEFT
        )
        ttk.Button(
            linha_ent, text="Registar Entrada", style="Amarelo.TButton", command=self._acao_entrada
        ).pack(side=tk.LEFT, padx=8)

        # Cartão Saída
        card_sai = ttk.Frame(col_dir, style="Card.TFrame", padding=10)
        card_sai.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            card_sai,
            text="Saída de Veículo (Matrícula ou Bilhete)",
            background=COR_CARD,
            foreground=COR_DESTAQUE,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W)

        linha_sai = ttk.Frame(card_sai, style="Card.TFrame")
        linha_sai.pack(fill=tk.X, pady=(6, 0))
        self.var_termo_saida = tk.StringVar()
        ttk.Entry(linha_sai, textvariable=self.var_termo_saida, width=18, font=("Consolas", 11)).pack(
            side=tk.LEFT
        )
        ttk.Button(
            linha_sai, text="Processar Saída (€)", style="Amarelo.TButton", command=self._acao_saida
        ).pack(side=tk.LEFT, padx=8)

        # Cartão Configurações do Parque
        card_cfg = ttk.Frame(col_dir, style="Card.TFrame", padding=10)
        card_cfg.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            card_cfg,
            text="Tarifário (arredondado à hora iniciada) e Capacidade",
            background=COR_CARD,
            foreground=COR_TEXTO,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W)

        linha_cfg = ttk.Frame(card_cfg, style="Card.TFrame")
        linha_cfg.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(linha_cfg, text="€/h:", background=COR_CARD, foreground=COR_TEXTO).pack(side=tk.LEFT)
        self.var_tarifa = tk.StringVar(value=f"{self.estado['tarifa_hora']:.2f}")
        ttk.Entry(linha_cfg, textvariable=self.var_tarifa, width=7).pack(side=tk.LEFT, padx=4)
        ttk.Button(linha_cfg, text="Aplicar", style="Acao.TButton", command=self._acao_tarifa).pack(
            side=tk.LEFT, padx=(0, 12)
        )

        ttk.Label(linha_cfg, text="Lugares:", background=COR_CARD, foreground=COR_TEXTO).pack(
            side=tk.LEFT
        )
        self.var_capacidade = tk.IntVar(value=self.estado["capacidade"])
        ttk.Spinbox(
            linha_cfg,
            from_=CAPACIDADE_MINIMA,
            to=CAPACIDADE_MAXIMA,
            textvariable=self.var_capacidade,
            width=5,
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(linha_cfg, text="Ajustar", style="Acao.TButton", command=self._acao_capacidade).pack(
            side=tk.LEFT
        )

        # Abas: Estacionados | Histórico
        self.abas = ttk.Notebook(col_dir)
        self.abas.pack(fill=tk.BOTH, expand=True)

        tab_est = ttk.Frame(self.abas, style="Painel.TFrame", padding=6)
        tab_hist = ttk.Frame(self.abas, style="Painel.TFrame", padding=6)
        self.abas.add(tab_est, text="Veículos Estacionados")
        self.abas.add(tab_hist, text="Histórico de Operações")

        colunas = ("lugar", "matricula", "bilhete", "entrada")
        self.tabela_veiculos = ttk.Treeview(tab_est, columns=colunas, show="headings", height=9)
        self.tabela_veiculos.heading("lugar", text="Lugar")
        self.tabela_veiculos.heading("matricula", text="Matrícula")
        self.tabela_veiculos.heading("bilhete", text="Bilhete")
        self.tabela_veiculos.heading("entrada", text="Hora Entrada")
        self.tabela_veiculos.column("lugar", width=60, anchor=tk.CENTER)
        self.tabela_veiculos.column("matricula", width=110, anchor=tk.CENTER)
        self.tabela_veiculos.column("bilhete", width=95, anchor=tk.CENTER)
        self.tabela_veiculos.column("entrada", width=140, anchor=tk.CENTER)
        self.tabela_veiculos.pack(fill=tk.BOTH, expand=True)
        self.tabela_veiculos.bind("<<TreeviewSelect>>", self._ao_selecionar_tabela)

        self.txt_historico = tk.Text(
            tab_hist,
            bg="#151C21",
            fg=COR_TEXTO,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=6,
            pady=6,
        )
        self.txt_historico.pack(fill=tk.BOTH, expand=True)

    def _desenhar_parque(self) -> None:
        self.canvas_parque.delete("all")
        larg = max(400, self.canvas_parque.winfo_width())
        alt = max(280, self.canvas_parque.winfo_height())

        total = len(self.estado["lugares"])
        colunas = 4 if total <= 16 else (5 if total <= 25 else 8)
        linhas = math.ceil(total / colunas)

        margem = 18
        espaco_x = 12
        espaco_y = 20
        lc = (larg - 2 * margem - (colunas - 1) * espaco_x) / colunas
        ac = (alt - 2 * margem - (linhas - 1) * espaco_y) / linhas

        # Faixas de circulação subtis
        for l_idx in range(linhas - 1):
            y_faixa = margem + (l_idx + 1) * ac + l_idx * espaco_y + espaco_y / 2
            self.canvas_parque.create_line(
                margem, y_faixa, larg - margem, y_faixa, fill="#4E565E", dash=(8, 6), width=2
            )

        for idx, lugar in enumerate(self.estado["lugares"]):
            col = idx % colunas
            lin = idx // colunas
            x0 = margem + col * (lc + espaco_x)
            y0 = margem + lin * (ac + espaco_y)
            x1 = x0 + lc
            y1 = y0 + ac

            cor_borda = "#E74C3C" if lugar["ocupado"] else COR_VERDE
            cor_fundo_vaga = "#21262B" if lugar["ocupado"] else "#1E3328"

            self.canvas_parque.create_rectangle(
                x0, y0, x1, y1, fill=cor_fundo_vaga, outline=cor_borda, width=2
            )
            self.canvas_parque.create_text(
                x0 + 8, y0 + 11, text=lugar["codigo"], anchor=tk.W,
                fill=COR_DESTAQUE, font=("Segoe UI", 8, "bold")
            )

            if lugar["ocupado"] and lugar["veiculo"] is not None:
                v = lugar["veiculo"]
                # Desenha silhueta superior de carro
                pad_x = max(10, lc * 0.16)
                pad_y = max(20, ac * 0.25)
                cx0, cy0 = x0 + pad_x, y0 + pad_y
                cx1, cy1 = x1 - pad_x, y1 - max(16, ac * 0.14)
                if cx1 > cx0 + 10 and cy1 > cy0 + 10:
                    self.canvas_parque.create_rectangle(
                        cx0, cy0, cx1, cy1, fill=v["cor"], outline="#111111", width=2
                    )
                    # Vidro dianteiro do carro
                    self.canvas_parque.create_rectangle(
                        cx0 + 4, cy0 + 4, cx1 - 4, cy0 + max(6, (cy1 - cy0) * 0.28),
                        fill="#1B2631", outline=""
                    )
                self.canvas_parque.create_text(
                    (x0 + x1) / 2, y1 - 8,
                    text=v["matricula"],
                    fill="#FFFFFF",
                    font=("Consolas", 8, "bold"),
                )
            else:
                self.canvas_parque.create_text(
                    (x0 + x1) / 2, (y0 + y1) / 2 + 4,
                    text="LIVRE",
                    fill="#82E0AA",
                    font=("Segoe UI", 9, "bold"),
                )

    def _ao_clicar_lugar(self, evento: tk.Event) -> None:
        larg = max(400, self.canvas_parque.winfo_width())
        alt = max(280, self.canvas_parque.winfo_height())
        total = len(self.estado["lugares"])
        colunas = 4 if total <= 16 else (5 if total <= 25 else 8)
        linhas = math.ceil(total / colunas)
        margem = 18
        espaco_x = 12
        espaco_y = 20
        lc = (larg - 2 * margem - (colunas - 1) * espaco_x) / colunas
        ac = (alt - 2 * margem - (linhas - 1) * espaco_y) / linhas

        col = int((evento.x - margem) // (lc + espaco_x))
        lin = int((evento.y - margem) // (ac + espaco_y))
        idx = lin * colunas + col
        if 0 <= col < colunas and 0 <= idx < total:
            lugar = self.estado["lugares"][idx]
            if lugar["ocupado"] and lugar["veiculo"] is not None:
                self.var_termo_saida.set(lugar["veiculo"]["matricula"])

    def _ao_selecionar_tabela(self, _evento: tk.Event) -> None:
        sel = self.tabela_veiculos.selection()
        if not sel:
            return
        valores = self.tabela_veiculos.item(sel[0], "values")
        if valores:
            self.var_termo_saida.set(valores[1])

    def atualizar_interface(self) -> None:
        """Atualiza relógio, planta, tabela, estatísticas e histórico."""
        agora = obter_hora_atual(self.estado)
        self.lbl_relogio.config(
            text=f"🕒 {agora.strftime('%d/%m/%Y %H:%M')}  |  Tarifa: {self.estado['tarifa_hora']:.2f} €/h"
        )

        stats = obter_estatisticas(self.estado)
        self.lbl_ocupacao.config(
            text=f"Ocupação: {stats['ocupados']}/{stats['capacidade']} ({stats['taxa_ocupacao']}%) | Livres: {stats['livres']}"
        )
        self.barra_ocupacao["value"] = stats["taxa_ocupacao"]
        self.lbl_metricas.config(
            text=(
                f"Receita Total: {stats['receita_total']:.2f} €  |  "
                f"Entradas: {stats['total_entradas']}  |  Saídas: {stats['total_saidas']}  |  "
                f"Tempo Médio: {stats['tempo_medio_min']} min"
            )
        )

        self.tabela_veiculos.delete(*self.tabela_veiculos.get_children())
        for lugar in self.estado["lugares"]:
            if lugar["ocupado"] and lugar["veiculo"] is not None:
                v = lugar["veiculo"]
                ent_fmt = datetime.fromisoformat(v["entrada"]).strftime("%d/%m %H:%M")
                self.tabela_veiculos.insert(
                    "", tk.END, values=(lugar["codigo"], v["matricula"], v["bilhete"], ent_fmt)
                )

        self.txt_historico.config(state=tk.NORMAL)
        self.txt_historico.delete("1.0", tk.END)
        for linha in reversed(self.estado["historico"][-40:]):
            self.txt_historico.insert(tk.END, f"• {linha}\n")
        self.txt_historico.config(state=tk.DISABLED)

        self._desenhar_parque()

    def _acao_entrada(self) -> None:
        mat = self.var_matricula_entrada.get()
        ok, msg, _ = registar_entrada(self.estado, mat)
        if not ok:
            messagebox.showwarning("Entrada Inválida", msg)
            return
        self.var_matricula_entrada.set("")
        self.atualizar_interface()
        messagebox.showinfo("Bilhete Emitido", msg)

    def _acao_saida(self) -> None:
        termo = self.var_termo_saida.get()
        ok, msg_erro, resumo = simular_saida(self.estado, termo)
        if not ok or resumo is None:
            messagebox.showwarning("Saída", msg_erro)
            return

        confirmar = messagebox.askyesno(
            "Confirmar Saída e Pagamento",
            (
                f"Veículo: {resumo['matricula']} (Bilhete {resumo['bilhete']})\n"
                f"Lugar: {resumo['lugar']}\n"
                f"Permanência: {resumo['minutos']} minutos ({resumo['horas_cobradas']}h cobradas)\n"
                f"Total a pagar: {resumo['valor']:.2f} €\n\n"
                "Confirmar pagamento e libertar lugar?"
            ),
        )
        if confirmar:
            ok_s, msg_s, _ = registar_saida(self.estado, termo)
            if ok_s:
                self.var_termo_saida.set("")
                self.atualizar_interface()
                messagebox.showinfo("Saída Concluída", msg_s)

    def _acao_avancar_tempo(self, minutos: int) -> None:
        avancar_relogio(self.estado, minutos)
        self.atualizar_interface()

    def _acao_tarifa(self) -> None:
        try:
            valor = float(self.var_tarifa.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Tarifa Inválida", "Introduz um valor numérico válido em euros.")
            return
        ok, msg = configurar_tarifa(self.estado, valor)
        if not ok:
            messagebox.showwarning("Tarifa", msg)
        else:
            self.atualizar_interface()
            messagebox.showinfo("Tarifa", msg)

    def _acao_capacidade(self) -> None:
        try:
            cap = int(self.var_capacidade.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Capacidade Inválida", "Introduz um número inteiro.")
            return
        ok, msg = reconfigurar_capacidade(self.estado, cap)
        if not ok:
            messagebox.showwarning("Capacidade", msg)
        else:
            self.atualizar_interface()
            messagebox.showinfo("Capacidade", msg)

    def _acao_novo(self) -> None:
        if messagebox.askyesno("Novo Parque", "Queres reiniciar o parque e limpar os registos?"):
            self.estado = criar_novo_parque()
            self.var_tarifa.set(f"{self.estado['tarifa_hora']:.2f}")
            self.var_capacidade.set(self.estado["capacidade"])
            self.atualizar_interface()

    def _acao_guardar(self) -> None:
        ok, msg = guardar_parque(self.estado)
        if ok:
            messagebox.showinfo("Guardar", msg)
        else:
            messagebox.showerror("Guardar", msg)

    def _acao_carregar(self) -> None:
        dados, msg = carregar_parque()
        if dados is None:
            messagebox.showwarning("Carregar", msg)
            return
        self.estado = dados
        self.var_tarifa.set(f"{self.estado['tarifa_hora']:.2f}")
        self.var_capacidade.set(self.estado["capacidade"])
        self.atualizar_interface()
        messagebox.showinfo("Carregar", msg)


def iniciar_interface() -> None:
    """Inicia a janela principal do Parking Manager."""
    raiz = tk.Tk()
    AplicacaoParqueEstacionamento(raiz)
    raiz.mainloop()
