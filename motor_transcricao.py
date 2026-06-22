"""
motor_transcricao.py
Logica de download + transcricao (TikTok, Instagram, YouTube), compartilhada
entre a versao desktop (tkinter) e a versao web (Streamlit) do
Wil É Foda - Transcritor.

Suporta dois "motores" de transcricao:
  - "groq"    -> usa a API da Groq (rapida, na nuvem, precisa de internet e chave)
  - "whisper" -> usa o Whisper local (mais lento, roda offline, sem custo por uso)
"""

import os
import sys
import time
import subprocess

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))


def pasta_resultados(plataforma):
    return os.path.join(PASTA_BASE, f"resultados_{plataforma}")


def pasta_audios_temp(plataforma):
    return os.path.join(PASTA_BASE, f"audios_temp_{plataforma}")


def arquivo_final(plataforma):
    return os.path.join(PASTA_BASE, f"todas_transcricoes_{plataforma}.txt")


class MotorTranscricao:

    LIMIAR_VIDEO_LONGO = 5 * 60
    MODELO_CURTO = "small"
    MODELO_LONGO = "medium"
    MODELO_GROQ = "whisper-large-v3-turbo"
    LIMITE_TAMANHO_GROQ_MB = 25

    def __init__(self, log_callback, progresso_callback, motor_ia="groq", chave_groq=None):
        self.log = log_callback
        self.progresso = progresso_callback
        self.motor_ia = motor_ia
        self.chave_groq = chave_groq
        self.modelos_carregados = {}
        self._cliente_groq = None
        self.cancelar = False

    def carregar_modelo(self, nome_modelo):
        if nome_modelo not in self.modelos_carregados:
            self.log(f"Carregando modelo Whisper local '{nome_modelo}'...")
            import whisper
            self.modelos_carregados[nome_modelo] = whisper.load_model(nome_modelo)
            self.log(f"Modelo '{nome_modelo}' carregado.")
        return self.modelos_carregados[nome_modelo]

    def _obter_cliente_groq(self):
        if self._cliente_groq is None:
            if not self.chave_groq:
                raise ValueError("Chave de API da Groq nao informada.")
            from groq import Groq
            self._cliente_groq = Groq(api_key=self.chave_groq)
        return self._cliente_groq

    def transcrever_via_groq(self, caminho_audio):
        cliente = self._obter_cliente_groq()
        with open(caminho_audio, "rb") as arquivo_audio:
            resultado = cliente.audio.transcriptions.create(
                file=(os.path.basename(caminho_audio), arquivo_audio.read()),
                model=self.MODELO_GROQ,
                language="pt",
                response_format="text",
            )
        if isinstance(resultado, str):
            return resultado.strip()
        return getattr(resultado, "text", str(resultado)).strip()

    def obter_duracao(self, link):
        comando = [
            sys.executable, "-m", "yt_dlp",
            "--print", "%(duration)s",
            "--skip-download",
            link
        ]
        resultado = subprocess.run(
            comando, capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        if resultado.returncode != 0:
            return None
        saida = resultado.stdout.strip().splitlines()
        if not saida:
            return None
        try:
            return float(saida[-1])
        except ValueError:
            return None

    def escolher_modelo_por_duracao(self, duracao_segundos):
        if duracao_segundos is not None and duracao_segundos > self.LIMIAR_VIDEO_LONGO:
            return self.MODELO_LONGO
        return self.MODELO_CURTO

    def baixar_audio(self, link, identificador, plataforma):
        pasta_audio = pasta_audios_temp(plataforma)
        os.makedirs(pasta_audio, exist_ok=True)
        nome_saida = os.path.join(pasta_audio, f"video_{identificador}.mp3")

        comando = [
            sys.executable, "-m", "yt_dlp",
            "-x", "--audio-format", "mp3",
            "-o", nome_saida,
            link
        ]
        resultado = subprocess.run(
            comando, capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        if resultado.returncode != 0:
            erro_resumido = resultado.stderr.strip().splitlines()[-1] if resultado.stderr.strip() else "erro desconhecido"
            return None, erro_resumido
        return nome_saida, None

    def transcrever_audio(self, caminho_audio, identificador, link, plataforma, modelo_whisper=None):
        usar_groq = self.motor_ia == "groq"

        if usar_groq:
            tamanho_mb = os.path.getsize(caminho_audio) / (1024 * 1024)
            if tamanho_mb > self.LIMITE_TAMANHO_GROQ_MB:
                self.log(f"Arquivo tem {tamanho_mb:.1f}MB (acima do limite da Groq) -> usando Whisper local.")
                usar_groq = False

        if usar_groq:
            texto = self.transcrever_via_groq(caminho_audio)
        else:
            nome_modelo = modelo_whisper or self.MODELO_CURTO
            modelo = self.carregar_modelo(nome_modelo)
            resultado = modelo.transcribe(caminho_audio, language="pt")
            texto = resultado["text"].strip()

        pasta_res = pasta_resultados(plataforma)
        os.makedirs(pasta_res, exist_ok=True)
        caminho_saida = os.path.join(pasta_res, f"video_{identificador}.txt")
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(f"Link original: {link}\n\n")
            f.write(texto)
        return caminho_saida

    def processar_links(self, links, plataforma):
        total = len(links)
        self.log(f"Total de links: {total}")
        self.log(f"Motor: {'Groq (API, rapido)' if self.motor_ia == 'groq' else 'Whisper local'}\n")

        pasta_res = pasta_resultados(plataforma)
        pasta_audio = pasta_audios_temp(plataforma)
        os.makedirs(pasta_res, exist_ok=True)
        os.makedirs(pasta_audio, exist_ok=True)

        prefixo_rodada = time.strftime("%Y%m%d_%H%M%S")

        usar_whisper_local = self.motor_ia != "groq"
        sempre_curto = plataforma in ("tiktok", "instagram")
        if usar_whisper_local and sempre_curto:
            self.carregar_modelo(self.MODELO_CURTO)

        sucesso = 0
        falhas = 0
        log_erros = []
        caminhos_desta_rodada = []

        for indice, link in enumerate(links, start=1):
            if self.cancelar:
                self.log("\nCancelado pelo usuario.")
                break

            id_arquivo = f"{prefixo_rodada}_{indice}"
            nome_modelo_whisper = None

            if usar_whisper_local and not sempre_curto:
                self.log(f"[{indice}/{total}] Verificando duracao...")
                duracao = self.obter_duracao(link)
                nome_modelo_whisper = self.escolher_modelo_por_duracao(duracao)

            self.log(f"[{indice}/{total}] Baixando: {link}")
            caminho_audio, erro = self.baixar_audio(link, id_arquivo, plataforma)

            if caminho_audio is None:
                self.log(f"[{indice}/{total}] ERRO ao baixar -> {erro}")
                log_erros.append(f"video_{id_arquivo} | {link} | ERRO DOWNLOAD: {erro}")
                falhas += 1
                self.progresso(indice, total)
                continue

            try:
                self.log(f"[{indice}/{total}] Transcrevendo...")
                caminho_saida = self.transcrever_audio(
                    caminho_audio, id_arquivo, link, plataforma,
                    modelo_whisper=nome_modelo_whisper,
                )
                self.log(f"[{indice}/{total}] OK -> {os.path.basename(caminho_saida)}")
                caminhos_desta_rodada.append(caminho_saida)
                sucesso += 1
            except Exception as e:
                self.log(f"[{indice}/{total}] ERRO ao transcrever -> {e}")
                log_erros.append(f"video_{id_arquivo} | {link} | ERRO TRANSCRICAO: {e}")
                falhas += 1

            self.progresso(indice, total)

        if log_erros:
            caminho_erros = os.path.join(PASTA_BASE, f"erros_{plataforma}.txt")
            with open(caminho_erros, "w", encoding="utf-8") as f:
                f.write("\n".join(log_erros))
            self.log(f"\nLog de erros: {os.path.basename(caminho_erros)}")

        self.log(f"\nFinalizado! Sucesso: {sucesso} | Falhas: {falhas}")
        return sucesso, falhas, caminhos_desta_rodada

    def juntar_arquivos_especificos(self, caminhos, nome_saida_base="transcricoes_rodada"):
        if not caminhos:
            return None
        prefixo_rodada = time.strftime("%Y%m%d_%H%M%S")
        caminho_final = os.path.join(PASTA_BASE, f"{nome_saida_base}_{prefixo_rodada}.txt")
        with open(caminho_final, "w", encoding="utf-8") as saida:
            for caminho in caminhos:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                saida.write(f"===== {os.path.basename(caminho)} =====\n")
                saida.write(conteudo)
                saida.write("\n\n")
        return caminho_final

    def juntar_resultados(self, plataforma):
        pasta_res = pasta_resultados(plataforma)
        if not os.path.isdir(pasta_res):
            return 0, None

        arquivos = sorted(f for f in os.listdir(pasta_res) if f.endswith(".txt"))
        caminho_final = arquivo_final(plataforma)
        with open(caminho_final, "w", encoding="utf-8") as saida:
            for nome_arquivo in arquivos:
                caminho = os.path.join(pasta_res, nome_arquivo)
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                saida.write(f"===== {nome_arquivo} =====\n")
                saida.write(conteudo)
                saida.write("\n\n")

        return len(arquivos), caminho_final
