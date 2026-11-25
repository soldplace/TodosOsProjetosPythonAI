"""Lógica central do jogo Empire (mapa, combate, economia, IA e turnos)."""

from __future__ import annotations

import math
import random
from typing import Any

from app.dados import (
    COLUNAS_MAPA,
    CUSTO_RECRUTAR_SOLDAO,
    FACCOES,
    LINHAS_MAPA,
    MANUTENCAO_POR_SOLDADO,
    MELHORIAS_DISPONIVEIS,
    NOMES_TERRITORIOS,
    OBJETIVO_TERRITORIOS_VITORIA,
    RECURSOS_INICIAIS_JOGADOR,
    TECNOLOGIAS_DISPONIVEIS,
    TIPOS_TERRITORIO,
    TOTAL_TERRITORIOS,
)


def criar_novo_jogo(semente: int | None = None) -> dict[str, Any]:
    """Cria e devolve o estado inicial completo de uma nova partida."""
    gerador = random.Random(semente)
    tipos_lista = list(TIPOS_TERRITORIO.keys())
    territorios: list[dict[str, Any]] = []

    for indice in range(TOTAL_TERRITORIOS):
        linha = indice // COLUNAS_MAPA
        coluna = indice % COLUNAS_MAPA
        tipo = gerador.choice(tipos_lista)

        # Posições iniciais fixas para garantir equilíbrio estratégico
        if (linha, coluna) in [(4, 0), (4, 1), (3, 0)]:
            dono = "jogador"
            guarnicao = 18 if (linha, coluna) == (4, 0) else 10
            if (linha, coluna) == (4, 0):
                tipo = "Fortaleza"
        elif (linha, coluna) in [(0, 0), (0, 1), (1, 0)]:
            dono = "inimigo_1"
            guarnicao = 15 if (linha, coluna) == (0, 0) else 9
            if (linha, coluna) == (0, 0):
                tipo = "Fortaleza"
        elif (linha, coluna) in [(0, 4), (1, 4), (4, 4)]:
            dono = "inimigo_2"
            guarnicao = 15 if (linha, coluna) == (4, 4) else 9
            if (linha, coluna) == (4, 4):
                tipo = "Fortaleza"
        else:
            dono = "neutro"
            guarnicao = gerador.randint(5, 11)

        info_tipo = TIPOS_TERRITORIO[tipo]
        territorios.append(
            {
                "id": indice,
                "linha": linha,
                "coluna": coluna,
                "nome": NOMES_TERRITORIOS[indice],
                "tipo": tipo,
                "dono": dono,
                "guarnicao": guarnicao,
                "producao": {
                    "ouro": info_tipo["ouro"],
                    "madeira": info_tipo["madeira"],
                    "ferro": info_tipo["ferro"],
                    "alimentos": info_tipo["alimentos"],
                },
                "defesa_base": info_tipo["defesa"],
            }
        )

    estado = {
        "turno": 1,
        "estado_jogo": "em_curso",  # "em_curso", "vitoria", "derrota"
        "motivo_fim": "",
        "recursos": dict(RECURSOS_INICIAIS_JOGADOR),
        "recursos_inimigos": {
            "inimigo_1": {"ouro": 120, "alimentos": 120},
            "inimigo_2": {"ouro": 120, "alimentos": 120},
        },
        "melhorias": {chave: 0 for chave in MELHORIAS_DISPONIVEIS},
        "tecnologias": [],
        "territorios": territorios,
        "registo": [
            "Turno 1 iniciado. O Império Lusitano prepara-se para expandir as fronteiras."
        ],
    }
    return estado


def obter_territorio(estado: dict[str, Any], territorio_id: int) -> dict[str, Any] | None:
    """Devolve o dicionário de um território pelo seu ID, ou None se inválido."""
    for territorio in estado["territorios"]:
        if territorio["id"] == territorio_id:
            return territorio
    return None


def sao_adjacentes(t1: dict[str, Any], t2: dict[str, Any]) -> bool:
    """Verifica se dois territórios são adjacentes ortogonalmente na grelha."""
    dist_linha = abs(t1["linha"] - t2["linha"])
    dist_coluna = abs(t1["coluna"] - t2["coluna"])
    return (dist_linha + dist_coluna) == 1


def obter_vizinhos_aliados(
    estado: dict[str, Any], territorio_alvo_id: int, dono: str = "jogador"
) -> list[dict[str, Any]]:
    """Lista os territórios pertencentes a `dono` adjacentes ao território alvo."""
    alvo = obter_territorio(estado, territorio_alvo_id)
    if alvo is None:
        return []
    vizinhos = []
    for t in estado["territorios"]:
        if t["dono"] == dono and sao_adjacentes(t, alvo):
            vizinhos.append(t)
    return vizinhos


def contar_territorios_por_dono(estado: dict[str, Any]) -> dict[str, int]:
    """Conta quantos territórios pertencem a cada facção."""
    contagem = {chave: 0 for chave in FACCOES}
    for t in estado["territorios"]:
        dono = t["dono"]
        contagem[dono] = contagem.get(dono, 0) + 1
    return contagem


def calcular_total_tropas(estado: dict[str, Any], dono: str = "jogador") -> int:
    """Calcula o total de soldados estacionados em todos os territórios de uma facção."""
    return sum(t["guarnicao"] for t in estado["territorios"] if t["dono"] == dono)


def calcular_producao_turno(estado: dict[str, Any]) -> dict[str, int]:
    """Calcula a produção total de recursos do jogador por turno com bónus aplicados."""
    totais = {"ouro": 0, "madeira": 0, "ferro": 0, "alimentos": 0}
    for t in estado["territorios"]:
        if t["dono"] == "jogador":
            for recurso in totais:
                totais[recurso] += t["producao"][recurso]

    melhorias = estado["melhorias"]
    tecnologias = estado["tecnologias"]

    fator_ouro = 1.0 + 0.25 * melhorias.get("mercado", 0)
    fator_quinta = 1.0 + 0.25 * melhorias.get("quinta", 0)
    bonus_ferro_forja = 10 * melhorias.get("forja", 0)

    totais["ouro"] = int(round(totais["ouro"] * fator_ouro))
    totais["madeira"] = int(round(totais["madeira"] * fator_quinta))
    totais["alimentos"] = int(round(totais["alimentos"] * fator_quinta))
    totais["ferro"] += bonus_ferro_forja

    if "agricultura" in tecnologias:
        totais["alimentos"] = int(round(totais["alimentos"] * 1.20))
    if "metalurgia" in tecnologias:
        totais["ferro"] = int(round(totais["ferro"] * 1.25))

    return totais


def calcular_manutencao_turno(estado: dict[str, Any]) -> dict[str, int]:
    """Calcula os custos de manutenção do exército do jogador por turno."""
    tropas = calcular_total_tropas(estado, "jogador")
    fator = 0.70 if "logistica" in estado["tecnologias"] else 1.0
    return {
        "ouro": math.ceil(tropas * MANUTENCAO_POR_SOLDADO["ouro"] * fator),
        "alimentos": math.ceil(tropas * MANUTENCAO_POR_SOLDADO["alimentos"] * fator),
    }


def _verificar_recursos_suficientes(
    recursos_atuais: dict[str, int], custos: dict[str, int]
) -> tuple[bool, str]:
    """Verifica se há recursos suficientes para cobrir um dicionário de custos."""
    faltas = []
    for recurso, valor in custos.items():
        if recursos_atuais.get(recurso, 0) < valor:
            faltas.append(f"{recurso} (faltam {valor - recursos_atuais.get(recurso, 0)})")
    if faltas:
        return False, "Recursos insuficientes: " + ", ".join(faltas) + "."
    return True, ""


def _descontar_recursos(recursos_atuais: dict[str, int], custos: dict[str, int]) -> None:
    """Subtrai os custos dos recursos atuais."""
    for recurso, valor in custos.items():
        recursos_atuais[recurso] = max(0, recursos_atuais.get(recurso, 0) - valor)


def recrutar_soldados(
    estado: dict[str, Any], territorio_id: int, quantidade: int
) -> tuple[bool, str]:
    """Recruta `quantidade` de soldados para um território do jogador."""
    if estado["estado_jogo"] != "em_curso":
        return False, "A partida já terminou."
    if not isinstance(quantidade, int) or quantidade <= 0:
        return False, "A quantidade de soldados deve ser um número inteiro positivo."

    territorio = obter_territorio(estado, territorio_id)
    if territorio is None or territorio["dono"] != "jogador":
        return False, "Só podes recrutar soldados em territórios que te pertencem."

    custo_total = {
        rec: val * quantidade for rec, val in CUSTO_RECRUTAR_SOLDAO.items()
    }
    ok, msg = _verificar_recursos_suficientes(estado["recursos"], custo_total)
    if not ok:
        return False, msg

    _descontar_recursos(estado["recursos"], custo_total)
    territorio["guarnicao"] += quantidade
    mensagem = f"Recrutados {quantidade} soldados em {territorio['nome']}."
    estado["registo"].append(mensagem)
    return True, mensagem


def mover_tropas(
    estado: dict[str, Any], origem_id: int, destino_id: int, quantidade: int
) -> tuple[bool, str]:
    """Move tropas entre dois territórios adjacentes pertencentes ao jogador."""
    if estado["estado_jogo"] != "em_curso":
        return False, "A partida já terminou."
    if not isinstance(quantidade, int) or quantidade <= 0:
        return False, "A quantidade a mover deve ser positiva."

    origem = obter_territorio(estado, origem_id)
    destino = obter_territorio(estado, destino_id)
    if origem is None or destino is None:
        return False, "Território inválido."
    if origem["dono"] != "jogador" or destino["dono"] != "jogador":
        return False, "Ambos os territórios têm de pertencer ao teu império."
    if not sao_adjacentes(origem, destino):
        return False, "Os territórios têm de ser adjacentes para mover tropas."
    if origem["guarnicao"] - quantidade < 1:
        return False, "Deves deixar pelo menos 1 soldado na guarnição de origem."

    origem["guarnicao"] -= quantidade
    destino["guarnicao"] += quantidade
    mensagem = f"Movidos {quantidade} soldados de {origem['nome']} para {destino['nome']}."
    estado["registo"].append(mensagem)
    return True, mensagem


def construir_melhoria(estado: dict[str, Any], chave_melhoria: str) -> tuple[bool, str]:
    """Constrói ou evolui uma melhoria económica ou militar."""
    if estado["estado_jogo"] != "em_curso":
        return False, "A partida já terminou."
    if chave_melhoria not in MELHORIAS_DISPONIVEIS:
        return False, "Melhoria desconhecida."

    info = MELHORIAS_DISPONIVEIS[chave_melhoria]
    nivel_atual = estado["melhorias"].get(chave_melhoria, 0)
    if nivel_atual >= info["nivel_max"]:
        return False, f"{info['nome']} já atingiu o nível máximo."

    # Custo escala ligeiramente com o nível atual
    fator_custo = 1.0 + 0.5 * nivel_atual
    custo = {k: int(round(v * fator_custo)) for k, v in info["custo"].items()}
    ok, msg = _verificar_recursos_suficientes(estado["recursos"], custo)
    if not ok:
        return False, msg

    _descontar_recursos(estado["recursos"], custo)
    estado["melhorias"][chave_melhoria] = nivel_atual + 1
    mensagem = f"{info['nome']} evoluído para o nível {nivel_atual + 1}."
    estado["registo"].append(mensagem)
    return True, mensagem


def investigar_tecnologia(estado: dict[str, Any], chave_tech: str) -> tuple[bool, str]:
    """Investiga e desbloqueia uma tecnologia se os requisitos e recursos existirem."""
    if estado["estado_jogo"] != "em_curso":
        return False, "A partida já terminou."
    if chave_tech not in TECNOLOGIAS_DISPONIVEIS:
        return False, "Tecnologia desconhecida."
    if chave_tech in estado["tecnologias"]:
        return False, "Esta tecnologia já foi investigada."

    info = TECNOLOGIAS_DISPONIVEIS[chave_tech]
    req = info["requisito"]
    if req is not None and req not in estado["tecnologias"]:
        nome_req = TECNOLOGIAS_DISPONIVEIS[req]["nome"]
        return False, f"Requer primeiro investigar '{nome_req}'."

    ok, msg = _verificar_recursos_suficientes(estado["recursos"], info["custo"])
    if not ok:
        return False, msg

    _descontar_recursos(estado["recursos"], info["custo"])
    estado["tecnologias"].append(chave_tech)
    mensagem = f"Tecnologia desbloqueada: {info['nome']}!"
    estado["registo"].append(mensagem)
    return True, mensagem


def calcular_fator_ataque_jogador(estado: dict[str, Any]) -> float:
    """Calcula o multiplicador ofensivo do jogador."""
    fator = 1.0 + 0.15 * estado["melhorias"].get("forja", 0)
    if "metalurgia" in estado["tecnologias"]:
        fator += 0.10
    if "taticas_cerco" in estado["tecnologias"]:
        fator += 0.20
    return fator


def calcular_fator_defesa_jogador(estado: dict[str, Any]) -> float:
    """Calcula o multiplicador defensivo adicional do jogador."""
    return 1.0 + 0.15 * estado["melhorias"].get("muralhas", 0)


def atacar_territorio(
    estado: dict[str, Any],
    origem_id: int,
    alvo_id: int,
    tropas_enviadas: int,
    fator_sorte: float | None = None,
) -> tuple[bool, str]:
    """Executa um combate entre um território aliado e um território adjacente inimigo/neutro."""
    if estado["estado_jogo"] != "em_curso":
        return False, "A partida já terminou."
    if not isinstance(tropas_enviadas, int) or tropas_enviadas <= 0:
        return False, "Tens de enviar pelo menos 1 soldado para atacar."

    origem = obter_territorio(estado, origem_id)
    alvo = obter_territorio(estado, alvo_id)
    if origem is None or alvo is None:
        return False, "Território inválido."
    if origem["dono"] != "jogador":
        return False, "O território de origem tem de ser teu."
    if alvo["dono"] == "jogador":
        return False, "Não podes atacar um território que já é teu."
    if not sao_adjacentes(origem, alvo):
        return False, "Só podes atacar territórios adjacentes."
    if origem["guarnicao"] - tropas_enviadas < 1:
        return False, "Tens de deixar pelo menos 1 soldado a defender a origem."

    sorte = fator_sorte if fator_sorte is not None else random.uniform(0.90, 1.15)
    fator_ataque = calcular_fator_ataque_jogador(estado)
    defesa_terreno = alvo["defesa_base"]
    if "taticas_cerco" in estado["tecnologias"]:
        defesa_terreno = max(1.0, defesa_terreno - 0.15)

    forca_ataque = tropas_enviadas * fator_ataque * sorte
    forca_defesa = max(1.0, alvo["guarnicao"] * defesa_terreno)

    origem["guarnicao"] -= tropas_enviadas

    if forca_ataque > forca_defesa:
        # Vitória do atacante: perdas proporcionais à resistência
        racio_perdas = min(0.85, (forca_defesa / forca_ataque) * 0.65)
        sobreviventes = max(1, int(round(tropas_enviadas * (1.0 - racio_perdas))))
        dono_anterior = FACCOES[alvo["dono"]]["nome"]
        alvo["dono"] = "jogador"
        alvo["guarnicao"] = sobreviventes
        # Saque simbólico de vitória
        saque_ouro = 25
        estado["recursos"]["ouro"] += saque_ouro
        mensagem = (
            f"Vitória em {alvo['nome']} (antes de {dono_anterior})! "
            f"Sobreviveram {sobreviventes} soldados (+{saque_ouro} ouro)."
        )
        estado["registo"].append(mensagem)
        verificar_fim_de_jogo(estado)
        return True, mensagem

    # Derrota do atacante: defensor sofre baixas proporcionais
    racio_dano_def = min(0.80, (forca_ataque / forca_defesa) * 0.60)
    baixas_defesa = max(1, int(round(alvo["guarnicao"] * racio_dano_def)))
    alvo["guarnicao"] = max(1, alvo["guarnicao"] - baixas_defesa)
    mensagem = (
        f"Ataque a {alvo['nome']} repelido! Perdeste os {tropas_enviadas} soldados; "
        f"o defensor perdeu {baixas_defesa} tropas."
    )
    estado["registo"].append(mensagem)
    return False, mensagem


def _executar_turno_ia(estado: dict[str, Any], faccao_ia: str) -> list[str]:
    """Inteligência artificial simples para uma facção inimiga."""
    eventos: list[str] = []
    territorios_ia = [t for t in estado["territorios"] if t["dono"] == faccao_ia]
    if not territorios_ia:
        return eventos

    # Recolha simplificada de recursos da IA
    rec_ia = estado["recursos_inimigos"].setdefault(faccao_ia, {"ouro": 80, "alimentos": 80})
    rec_ia["ouro"] += len(territorios_ia) * 14
    rec_ia["alimentos"] += len(territorios_ia) * 12

    # Recrutamento automático em fronteiras
    qtd_recrutar = min(rec_ia["ouro"] // 12, rec_ia["alimentos"] // 6, 8)
    if qtd_recrutar >= 2:
        rec_ia["ouro"] -= qtd_recrutar * 12
        rec_ia["alimentos"] -= qtd_recrutar * 6
        alvo_reforco = min(territorios_ia, key=lambda t: t["guarnicao"])
        alvo_reforco["guarnicao"] += qtd_recrutar

    # Tenta um ataque oportunista se tiver vantagem clara
    melhor_ataque: tuple[dict[str, Any], dict[str, Any], int] | None = None
    for origem in territorios_ia:
        if origem["guarnicao"] < 8:
            continue
        disponiveis = origem["guarnicao"] - 3
        for candidato in estado["territorios"]:
            if candidato["dono"] != faccao_ia and sao_adjacentes(origem, candidato):
                if disponiveis >= candidato["guarnicao"] * 1.25:
                    melhor_ataque = (origem, candidato, disponiveis)
                    break
        if melhor_ataque is not None:
            break

    if melhor_ataque is not None:
        origem, alvo, enviados = melhor_ataque
        origem["guarnicao"] -= enviados
        defesa_efetiva = alvo["guarnicao"] * alvo["defesa_base"]
        if alvo["dono"] == "jogador":
            defesa_efetiva *= calcular_fator_defesa_jogador(estado)
        forca_ia = enviados * random.uniform(0.95, 1.10)

        if forca_ia > defesa_efetiva:
            sobreviventes = max(1, int(round(enviados * 0.60)))
            era_jogador = alvo["dono"] == "jogador"
            alvo["dono"] = faccao_ia
            alvo["guarnicao"] = sobreviventes
            nome_ia = FACCOES[faccao_ia]["nome"]
            if era_jogador:
                eventos.append(f"ALERTA: {nome_ia} conquistou o teu território {alvo['nome']}!")
            else:
                eventos.append(f"{nome_ia} conquistou {alvo['nome']}.")
        else:
            alvo["guarnicao"] = max(1, alvo["guarnicao"] - max(1, enviados // 3))
            if alvo["dono"] == "jogador":
                eventos.append(
                    f"A tua guarnição em {alvo['nome']} repeliu um ataque de {FACCOES[faccao_ia]['nome']}!"
                )

    return eventos


def verificar_fim_de_jogo(estado: dict[str, Any]) -> str:
    """Avalia e atualiza o estado de vitória ou derrota."""
    contagem = contar_territorios_por_dono(estado)
    ter_jogador = contagem.get("jogador", 0)
    inimigos_vivos = contagem.get("inimigo_1", 0) + contagem.get("inimigo_2", 0)

    if ter_jogador == 0:
        estado["estado_jogo"] = "derrota"
        estado["motivo_fim"] = "Perdeste todos os teus territórios. O teu império caiu!"
    elif ter_jogador == TOTAL_TERRITORIOS or (
        inimigos_vivos == 0 and ter_jogador >= OBJETIVO_TERRITORIOS_VITORIA
    ):
        estado["estado_jogo"] = "vitoria"
        estado["motivo_fim"] = (
            f"Conquistaste {ter_jogador} territórios e derrotaste os impérios rivais! Vitória Suprema!"
        )
    else:
        estado["estado_jogo"] = "em_curso"
        estado["motivo_fim"] = ""
    return estado["estado_jogo"]


def terminar_turno(estado: dict[str, Any]) -> dict[str, Any]:
    """Processa o fim de turno: produção, manutenção, IA e verificação de fim de jogo."""
    if estado["estado_jogo"] != "em_curso":
        return {"resumo": ["A partida já foi concluída."]}

    resumo: list[str] = []
    producao = calcular_producao_turno(estado)
    for recurso, valor in producao.items():
        estado["recursos"][recurso] += valor

    manutencao = calcular_manutencao_turno(estado)
    deficit = False
    for recurso in ("ouro", "alimentos"):
        if estado["recursos"][recurso] >= manutencao[recurso]:
            estado["recursos"][recurso] -= manutencao[recurso]
        else:
            estado["recursos"][recurso] = 0
            deficit = True

    if deficit:
        # Deserção por falta de manutenção
        perdas = 0
        for t in estado["territorios"]:
            if t["dono"] == "jogador" and t["guarnicao"] > 1:
                baixa = max(1, t["guarnicao"] // 5)
                t["guarnicao"] = max(1, t["guarnicao"] - baixa)
                perdas += baixa
        resumo.append(
            f"Falta de ouro/alimentos! {perdas} soldados desertaram por falta de pagamento."
        )

    for faccao_ia in ("inimigo_1", "inimigo_2"):
        eventos_ia = _executar_turno_ia(estado, faccao_ia)
        resumo.extend(eventos_ia)

    estado["turno"] += 1
    resumo.insert(
        0,
        (
            f"Turno {estado['turno']}: +{producao['ouro']} ouro, +{producao['madeira']} madeira, "
            f"+{producao['ferro']} ferro, +{producao['alimentos']} alimentos "
            f"(manutenção: -{manutencao['ouro']} ouro, -{manutencao['alimentos']} alimentos)."
        ),
    )

    for linha in resumo:
        estado["registo"].append(linha)
    # Limita o histórico para manter a interface leve
    if len(estado["registo"]) > 80:
        estado["registo"] = estado["registo"][-80:]

    verificar_fim_de_jogo(estado)
    if estado["estado_jogo"] != "em_curso":
        estado["registo"].append(estado["motivo_fim"])
        resumo.append(estado["motivo_fim"])

    return {
        "producao": producao,
        "manutencao": manutencao,
        "resumo": resumo,
    }
