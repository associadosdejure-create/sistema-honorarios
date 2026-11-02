import streamlit as str_app
import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time
import os
import bcrypt
import json
import base64
import html
import re
from decimal import Decimal, InvalidOperation

st.set_page_config(page_title="Controle DEJURE ADVOCACIA", layout="wide", page_icon="⚖️")

# --- LAYOUT DEJURE | GRAFITE E DOURADO ORIGINAL (SOMENTE VISUAL) ---
st.markdown("""
<style>
:root { color-scheme: dark; --dejure-ouro: #D4AF37; --dejure-fundo: #101216; --dejure-painel: #1A1E24; }
.stApp, [data-testid="stAppViewContainer"] { background: var(--dejure-fundo) !important; color: #E9E9EA !important; }
[data-testid="stHeader"] { background: rgba(16,18,22,.96) !important; }
[data-testid="stSidebar"] { background: #171A1F !important; border-right: 1px solid #36332A !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .55rem; }
.block-container { max-width: 1500px; padding-top: 1.5rem; padding-bottom: 3rem; }
h1, h2, h3, h4, h5, h6 { font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important; letter-spacing: -.018em; font-weight: 650 !important; color: var(--dejure-ouro) !important; }
h1 { font-size: clamp(1.65rem, 2.6vw, 2.25rem) !important; }
.stMarkdown p, .stMarkdown li { color: #E2E3E5; }
label, [data-testid="stWidgetLabel"] p { color: #D4AF37 !important; font-weight: 550 !important; }
[data-testid="stCaptionContainer"], .stCaption { color: #ADB0B5 !important; }
[data-testid="stMetric"] { background: var(--dejure-painel); border: 1px solid #393A3B; border-radius: 11px; padding: 1rem 1.1rem; min-height: 108px; }
[data-testid="stMetricLabel"] p { color: #D4AF37 !important; font-weight: 550 !important; }
/* PADRONIZAÇÃO DE LEGIBILIDADE: títulos inteiros, sem reticências */
[data-testid="stMetric"] { min-width: 0 !important; height: auto !important; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] > div { min-width: 0 !important; max-width: 100% !important; }
[data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"] p {
    font-size: clamp(.79rem, .9vw, .91rem) !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere !important;
    display: block !important;
    -webkit-line-clamp: unset !important;
}
[data-testid="stMetricValue"] { font-size: clamp(1.4rem, 1.8vw, 1.9rem) !important; }
.stButton > button, .stDownloadButton > button, [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
    height: auto !important;
    min-height: 2.65rem !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    line-height: 1.35 !important;
    font-size: .88rem !important;
    padding: .55rem .85rem !important;
}
.stButton > button p, .stDownloadButton > button p, button[data-testid^="stBaseButton"] p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere !important;
    line-height: 1.35 !important;
    font-size: inherit !important;
}
[data-testid="stSidebar"] .stButton > button { min-height: 2.5rem !important; font-size: .87rem !important; }
[data-baseweb="tab-list"] button[data-baseweb="tab"] { height: auto !important; min-height: 2.5rem !important; white-space: normal !important; font-size: .87rem !important; }
[data-baseweb="tab-list"] button[data-baseweb="tab"] p { white-space: normal !important; overflow-wrap: anywhere !important; }
[data-testid="stWidgetLabel"] p { white-space: normal !important; overflow-wrap: anywhere !important; line-height: 1.4 !important; }

[data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: 700; letter-spacing: -.025em; }
[data-testid="stForm"], [data-testid="stExpander"] { background: #1A1E24 !important; border: 1px solid #383B3E !important; border-radius: 11px !important; }
.stButton > button, .stDownloadButton > button, [data-testid="stBaseButton-secondary"] { background: #242930 !important; color: #D4AF37 !important; border: 1px solid #424039 !important; border-radius: 8px !important; font-weight: 600; min-height: 2.6rem; transition: background .15s ease, border-color .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { background: #30343A !important; border-color: #D4AF37 !important; color: #F0D678 !important; }
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] { background: #D4AF37 !important; color: #141619 !important; border: 1px solid #D4AF37 !important; font-weight: 700 !important; }
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { background: #E5C75D !important; color: #141619 !important; }
[data-testid="stSidebar"] .stButton > button { justify-content: flex-start; text-align: left; width: 100%; }
[data-baseweb="input"], [data-baseweb="select"], [data-baseweb="textarea"], [data-testid="stDateInput"] input, textarea { background: #22272D !important; color: #F0F0F0 !important; border-color: #45494D !important; border-radius: 8px !important; }
input, textarea { color: #F0F0F0 !important; }
[data-baseweb="tab-list"] { gap: .45rem; border-bottom: 1px solid #393A3C; }
button[data-baseweb="tab"] { color: #BFC2C7 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #D4AF37 !important; border-bottom-color: #D4AF37 !important; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid #393C40; border-radius: 9px; overflow: hidden; }
[data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td, [data-testid="stTable"] th, [data-testid="stTable"] td { white-space: normal !important; word-break: break-word !important; overflow-wrap: break-word !important; }
hr { border-color: #393A3C !important; }
[data-testid="stAlert"] { border-radius: 9px !important; }
@media (max-width: 768px) { .block-container { padding: 1rem .8rem 2rem; } [data-testid="stMetric"] { padding: .8rem; min-height: 92px; } }
</style>
""", unsafe_allow_html=True)

try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    st.error("⚠️ ERRO CRÍTICO: Chaves do Supabase ausentes nos Secrets.")
    st.stop()

# Cliente privilegiado restrito ao servidor Streamlit: somente operações de
# Storage e medição da cota. Nunca expor a chave em páginas, logs ou GitHub.
# A chave publica continua sendo usada nas demais operações do sistema.
def cliente_storage_servidor():
    chave = str(st.secrets.get('SUPABASE_SERVICE_ROLE_KEY', '')).strip()
    if not chave or chave.startswith('sb_publishable_'):
        raise RuntimeError(
            'Configure SUPABASE_SERVICE_ROLE_KEY nos Secrets do Streamlit '
            '(chave secreta do Supabase; não use a publishable).'
        )
    return create_client(st.secrets['SUPABASE_URL'], chave)

# --- CONFIRMAÇÃO VISUAL DE OPERAÇÕES ---
def confirmar_operacao(mensagem):
    """Mostra confirmação imediata e mantém aviso após st.rerun()."""
    st.session_state['_dejure_ultima_confirmacao'] = str(mensagem)
    st.success(mensagem, icon="✅")
    st.toast(str(mensagem), icon="✅")

# Exibe a confirmação após um rerun (por exemplo, depois de cadastrar ou excluir).
if st.session_state.get('_dejure_ultima_confirmacao'):
    st.success(st.session_state.pop('_dejure_ultima_confirmacao'), icon="✅")

# --- APRESENTAÇÃO DE TABELAS: CAMPOS SEM DADOS FICAM EM BRANCO ---
def preparar_tabela_visualizacao(dados):
    """Limpa apenas a visualização, sem alterar os registros do Supabase."""
    tabela = dados.copy()
    # Evita exibir os textos None, nan, NaN e <NA> vindos de colunas textuais.
    for coluna in tabela.columns:
        serie = tabela[coluna]
        if pd.api.types.is_object_dtype(serie) or pd.api.types.is_string_dtype(serie):
            tabela[coluna] = serie.map(
                lambda valor: "" if valor is None or (
                    isinstance(valor, str) and valor.strip().lower() in
                    ("none", "nan", "nat", "<na>", "null")
                ) else valor
            )
    # A conversão para string ocorre SOMENTE na cópia exibida.
    # Isso evita que a grade do Streamlit apresente None/NaN e mantém
    # números e datas intactos no banco e nas rotinas de cálculo.
    tabela = tabela.astype(object).where(pd.notna(tabela), "")
    return tabela


def largura_automatica_colunas(tabela):
    """Dimensiona as colunas conforme cabeçalho e conteúdo exibido.

    O Streamlit usa uma grade com rolagem horizontal quando a soma das
    larguras excede a tela; assim não é necessário comprimir o texto.
    """
    configuracao = {}
    for coluna in tabela.columns:
        # Trabalha somente com a cópia de exibição; não altera os dados.
        serie = tabela[coluna]
        textos = [str(coluna)]
        textos.extend(str(valor) for valor in serie if valor is not None and str(valor) != "")
        # Aproxima a largura do texto na fonte padrão da grade, com folga.
        # Para campos muito longos, permite até 2400 px por coluna.
        maior = max((len(linha) for texto in textos for linha in texto.splitlines()), default=0)
        largura = min(2400, max(110, int(maior * 8.5 + 40)))
        configuracao[str(coluna)] = st.column_config.Column(width=largura)
    return configuracao


def exibir_tabela(dados, **kwargs):
    """Exibe valores ausentes em branco e ajusta a largura das colunas."""
    if isinstance(dados, pd.io.formats.style.Styler):
        # Preserva os estilos e trabalha com uma cópia dos dados.
        tabela = preparar_tabela_visualizacao(dados.data)
        dados = dados._copy(deepcopy=True)
        dados.data = tabela
    elif isinstance(dados, pd.DataFrame):
        tabela = preparar_tabela_visualizacao(dados)
        dados = tabela
    else:
        return st.dataframe(dados, **kwargs)

    # Não sobrescreve eventuais configurações específicas já fornecidas.
    configuracao = largura_automatica_colunas(tabela)
    configuracao.update(kwargs.pop("column_config", {}) or {})
    return st.dataframe(dados, column_config=configuracao, **kwargs)

# --- ENTRADAS MONETÁRIAS EM PADRÃO BRASILEIRO ---
def interpretar_moeda_br(texto):
    """Aceita R$ 10.000,00; 10000,00; 10000; 10000.00; retorna float."""
    valor = str(texto or "").strip().replace("R$", "").replace(" ", "")
    if not valor:
        return 0.0
    if not re.fullmatch(r"[0-9.,]+", valor):
        raise ValueError("Informe apenas números, pontos de milhar e vírgula decimal.")
    if "," in valor:
        if valor.count(",") != 1 or len(valor.split(",")[1]) > 2:
            raise ValueError("Use até duas casas decimais, por exemplo R$ 10.000,00.")
        inteiro, centavos = valor.split(",")
        if "." in inteiro and not re.fullmatch(r"[0-9]{1,3}(\.[0-9]{3})+", inteiro):
            raise ValueError("Separe os milhares com pontos, por exemplo 10.000,00.")
        normalizado = inteiro.replace(".", "") + "." + (centavos or "0")
    elif "." in valor:
        if re.fullmatch(r"[0-9]{1,3}(\.[0-9]{3})+", valor):
            normalizado = valor.replace(".", "")
        elif valor.count(".") == 1 and len(valor.split(".")[1]) <= 2:
            normalizado = valor  # aceita também 10000.50
        else:
            raise ValueError("Formato inválido. Exemplo: R$ 10.000,00.")
    else:
        normalizado = valor
    try:
        numero = Decimal(normalizado)
        if numero < 0 or not numero.is_finite():
            raise ValueError("O valor não pode ser negativo.")
        return float(numero.quantize(Decimal("0.01")))
    except (InvalidOperation, OverflowError):
        raise ValueError("Valor monetário inválido.")


def campo_valor_invalido(texto):
    try:
        interpretar_moeda_br(texto)
        return False
    except ValueError:
        return True


def normalizar_campo_moeda(chave):
    """Formata ao confirmar o campo (Enter/Tab/clique fora)."""
    try:
        numero = interpretar_moeda_br(st.session_state[chave])
        st.session_state[chave] = formatar_moeda_br(numero)
    except ValueError:
        pass  # Mantém o texto para o usuário corrigir.


def campo_moeda_br(rotulo, chave, inicial=0.0, em_formulario=False):
    """Campo textual com valor numérico retornado para cálculos/Supabase."""
    if chave not in st.session_state:
        st.session_state[chave] = formatar_moeda_br(inicial)
    kwargs = {"key": chave, "help": "Exemplo: R$ 10.000,00. Ao sair do campo, o valor será formatado."}
    if not em_formulario:
        kwargs["on_change"] = normalizar_campo_moeda
        kwargs["args"] = (chave,)
    texto = st.text_input(rotulo, **kwargs)
    try:
        return interpretar_moeda_br(texto)
    except ValueError as erro:
        st.error(f"{rotulo}: {erro}")
        return None



# Consulta pública de CEP: somente o CEP é enviado ao ViaCEP.
def consultar_cep(cep):
    import urllib.request
    import json as _json
    numeros = re.sub(r"\D", "", str(cep or ""))
    if len(numeros) != 8:
        raise ValueError("Informe um CEP com 8 dígitos.")
    requisicao = urllib.request.Request(
        f"https://viacep.com.br/ws/{numeros}/json/",
        headers={"User-Agent": "DEJURE-Advocacia/1.0"}
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=6) as resposta:
            dados = _json.load(resposta)
    except Exception as erro:
        raise RuntimeError("Serviço de CEP indisponível. Preencha o endereço manualmente.") from erro
    if dados.get("erro"):
        raise ValueError("CEP não encontrado. Confira os números digitados.")
    return dados


def aplicar_cep_campos(prefixo):
    try:
        dados = consultar_cep(st.session_state.get(prefixo + "cep", ""))
        for campo, origem in (("logradouro", "logradouro"), ("bairro", "bairro"),
                              ("cid", "localidade"), ("uf", "uf")):
            if dados.get(origem):
                st.session_state[prefixo + campo] = dados[origem]
        st.session_state[prefixo + "cep_mensagem"] = "Endereço localizado. Confira os dados e informe o número."
    except (ValueError, RuntimeError) as erro:
        st.session_state[prefixo + "cep_mensagem"] = str(erro)


def endereco_legado(logradouro, numero, bairro):
    return ", ".join(parte for parte in [
        str(logradouro or "").strip(),
        str(numero or "").strip(),
        str(bairro or "").strip()
    ] if parte)

def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def converter_imagem_base64(file) -> str:
    encoded = base64.b64encode(file.read()).decode()
    mime_type = file.type
    return f"data:{mime_type};base64,{encoded}"

def registrar_auditoria(usuario, acao, modulo, detalhes=""):
    try:
        supabase.table("logs_auditoria").insert({
            "usuario": usuario,
            "acao": acao,
            "modulo": modulo,
            "detalhes": detalhes
        }).execute()
    except Exception:
        pass



def dejure_logs_repasses_ativos(cliente):
    """Reconstroi o ultimo estado de cada parcela a partir de eventos imutaveis de auditoria."""
    registros = []
    inicio = 0
    while True:
        lote = (cliente.table('logs_auditoria').select('*').eq('modulo', 'Repasses')
                .order('id').range(inicio, inicio + 999).execute().data or [])
        registros.extend(lote)
        if len(lote) < 1000:
            break
        inicio += 1000
    estado = {}
    sem_id = []
    for log in registros:
        try:
            dados = json.loads(log.get('detalhes') or '{}')
            pid = dados.get('parcela_id')
            if pid is None:
                if log.get('acao') == 'Baixa e Rateio':
                    sem_id.append(log)
                continue
            chave = str(pid)
            if log.get('acao') == 'Cancelamento de Baixa':
                estado.pop(chave, None)
            elif log.get('acao') in ('Baixa e Rateio', 'Correção de Baixa'):
                estado[chave] = log
        except (ValueError, TypeError, AttributeError):
            continue
    return sem_id + list(estado.values())


def dejure_registrar_evento_repasse(cliente, usuario, acao, dados):
    """Nao engole erros: eventos financeiros precisam de confirmacao do banco."""
    retorno = cliente.table('logs_auditoria').insert({
        'usuario': usuario, 'acao': acao, 'modulo': 'Repasses',
        'detalhes': json.dumps(dados, ensure_ascii=False)
    }).execute()
    if not retorno.data:
        raise RuntimeError('O banco nao confirmou o registro financeiro.')
    return retorno

def dejure_historicos_balanco(cliente):
    """Ultima escolha por parcela, inclusive desmarcacoes, sem gerar eventos de repasse."""
    eventos = {}
    inicio = 0
    while True:
        lote = (cliente.table('logs_auditoria').select('*').eq('modulo', 'Balanço Histórico')
                .order('id').range(inicio, inicio + 999).execute().data or [])
        for log in lote:
            try:
                d = json.loads(log.get('detalhes') or '{}')
                if d.get('parcela_id') is not None:
                    eventos[str(d['parcela_id'])] = d
            except (ValueError, TypeError, AttributeError):
                continue
        if len(lote) < 1000:
            break
        inicio += 1000
    return eventos


def dejure_salvar_historico_balanco(cliente, usuario, parcela_id, incluir, valor, data_recebimento, motivo, competencia_balanco=None):
    dados = {'parcela_id': parcela_id, 'incluir_balanco': bool(incluir),
             'valor': round(float(valor), 2), 'data_recebimento': str(data_recebimento),
             'competencia_balanco': str(competencia_balanco or str(data_recebimento)[:7]),
             'motivo': motivo}
    res = cliente.table('logs_auditoria').insert({
        'usuario': usuario, 'acao': 'Atualizar inclusão de parcela histórica no balanço',
        'modulo': 'Balanço Histórico', 'detalhes': json.dumps(dados, ensure_ascii=False)
    }).execute()
    if not res.data:
        raise RuntimeError('Não foi possível confirmar o lançamento contábil.')
    return res


def limpar_flags_cadastro():
    for k in ['cad_cli_sucesso', 'cad_hon_sucesso', 'cad_per_sucesso', 'cad_exp_sucesso', 'cad_trf_sucesso', 'cad_pen_sucesso', 'cad_pros_pend_sucesso', 'cad_user_sucesso', 'ultimo_cliente_cadastrado_id', 'ultimo_cliente_cadastrado_nome', 'ultimo_cliente_cadastrado_doc', 'ultimo_cliente_cadastrado_tel', 'ultimo_cliente_cadastrado_obs']:
        if k in st.session_state:
            st.session_state[k] = False if isinstance(st.session_state[k], bool) else None

def formatar_telefone(v):
    if not v: return None
    nums = re.sub(r'\D', '', str(v))
    if len(nums) == 10:
        return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
    elif len(nums) == 11:
        return f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
    return v if v.strip() else None

def validar_telefone_fixo(v):
    if not v or not str(v).strip(): return True
    nums = re.sub(r'\D', '', str(v))
    return len(nums) == 10

def validar_celular(v):
    if not v or not str(v).strip(): return True
    nums = re.sub(r'\D', '', str(v))
    return len(nums) == 11 and nums[2] == '9'

def validar_email(email):
    if not email or not email.strip():
        return True
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(padrao, email.strip()))

def formatar_data_br(val):
    if not val: return ""
    str_val = str(val).strip()
    try:
        if len(str_val) >= 10:
            dt = datetime.strptime(str_val[:10], "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
    except:
        pass
    return str_val

def formatar_hora_br(val):
    if not val: return ""
    str_val = str(val).strip()
    try:
        if len(str_val) == 5:
            return f"{str_val}:00"
        elif len(str_val) >= 8:
            return str_val[:8]
    except:
        pass
    return str_val if len(str_val) == 8 else f"{str_val}:00" if len(str_val) == 5 else str_val

def formatar_moeda_br(val):
    try:
        num = float(val)
        s = f"{num:,.2f}"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {s}"
    except:
        return "R$ 0,00"

# --- STATUS VISUAL UNIFICADO: A RECEBER / A PAGAR ---
def dejure_status_parcela_visual(status, vencimento, mes_referencia, natureza='receber'):
    """Somente apresentação: nunca altera o status financeiro no banco."""
    quitado = str(status or '').strip().casefold() in ('pago', 'paga', 'quitado', 'quitada', 'recebido', 'recebida')
    if quitado:
        return '🟢 Recebida' if natureza == 'receber' else '🟢 Paga'
    try:
        data_v = date.fromisoformat(str(vencimento)[:10])
        mesmo_mes = data_v.year == mes_referencia.year and data_v.month == mes_referencia.month
    except (ValueError, TypeError):
        mesmo_mes = False
    if mesmo_mes:
        return '🔴 A receber no mês' if natureza == 'receber' else '🔴 A pagar no mês'
    return '🟡 A receber' if natureza == 'receber' else '🟡 A pagar'


def dejure_cor_status_visual(valor):
    txt = str(valor)
    if txt.startswith('🟢'):
        return 'background-color: #123d2b; color: #9ff3c1; font-weight: bold;'
    if txt.startswith('🔴'):
        return 'background-color: #552025; color: #ffb1b1; font-weight: bold;'
    if txt.startswith('🟡'):
        return 'background-color: #493d16; color: #ffe18a; font-weight: bold;'
    return ''


def carregar_usuarios_db():
    # O hash inicial fica exclusivamente no Streamlit Secrets, nunca no GitHub.
    # Após trocar a senha na tela, o hash persistido no Supabase tem prioridade.
    hash_inicial = str(st.secrets.get("MASTER_PASSWORD_HASH", "")).strip()
    if not hash_inicial.startswith(("$2a$", "$2b$", "$2y$")):
        st.error("Configuração de segurança incompleta: MASTER_PASSWORD_HASH ausente ou inválido nos Secrets.")
        st.stop()

    cred_dict = {
        "usernames": {
            "master": {
                "name": "Administrador Master", "password": hash_inicial,
                "role": "admin", "trocar_senha": False,
                "foto_url": None, "telefone": "", "oab": "",
                "data_nascimento": None, "destaque_mes": False
            }
        }
    }

    try:
        res = supabase.table("usuarios_sistema").select("*").execute()
        for u in (res.data or []):
            uname = str(u.get("username", "")).strip().lower()
            if not uname:
                continue
            if uname == "master":
                senha_master_db = str(u.get("senha_hash") or u.get("password") or "").strip()
                # Compatibilidade com a implementação anterior de troca de senha.
                senha_foi_alterada = str(u.get("nome_completo") or "").endswith(" [SENHA_ALTERADA]")
                if senha_foi_alterada:
                    if not senha_master_db.startswith(("$2a$", "$2b$", "$2y$")):
                        raise ValueError("Hash do master no banco está inválido")
                    cred_dict["usernames"]["master"]["password"] = senha_master_db
                continue

            senha_db = str(u.get("senha_hash") or u.get("password") or "").strip()
            if senha_db and not senha_db.startswith("$2"):
                senha_db = gerar_hash(senha_db)
            cred_dict["usernames"][uname] = {
                "name": str(u.get("nome_completo", u.get("name", "Usuário"))),
                "password": senha_db,
                "role": str(u.get("role", "estagiario")),
                "trocar_senha": u.get("trocar_senha", True),
                "foto_url": u.get("foto_url"), "telefone": u.get("telefone", ""),
                "oab": u.get("oab", ""), "data_nascimento": u.get("data_nascimento"),
                "observacoes_pessoais": u.get("observacoes_pessoais", ""),
                "destaque_mes": u.get("destaque_mes", False)
            }
    except Exception:
        # Falha fechada: jamais retornar ao hash inicial por erro de consulta.
        st.error("Falha ao verificar as credenciais no Supabase. Login temporariamente indisponível.")
        st.stop()
    return cred_dict


credentials = carregar_usuarios_db()
cookie_secret = str(st.secrets.get("AUTH_COOKIE_KEY", "")).strip()
if len(cookie_secret) < 32:
    st.error("Configuração de segurança incompleta: AUTH_COOKIE_KEY deve ter pelo menos 32 caracteres.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials,
    cookie_name="sistema_dejure_cookie_seguro_v1",
    cookie_key=cookie_secret,
    cookie_expiry_days=1
)

authentication_status = st.session_state.get('authentication_status')

if authentication_status != True:
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚖️ DEJURE ADVOCACIA</h1>", unsafe_allow_html=True)

try:
    authenticator.login(location='main')
except Exception:
    authenticator.login('main')

name = st.session_state.get('name')
username = st.session_state.get('username')

if authentication_status == True and not st.session_state.get('login_registrado', False):
    registrar_auditoria(username, "Login", "Acesso", f"Usuário {name} ({username}) efetuou login no sistema.")
    st.session_state['login_registrado'] = True

if authentication_status == False:
    st.error('❌ Usuário ou senha incorretos.')
elif authentication_status == None:
    if st.session_state.get('sessao_expirada'):
        st.warning('⏱️ Sua sessão expirou (15 minutos de inatividade). Faça login novamente.')
    else:
        pass  
elif authentication_status == True:
    
    agora = time.time()
    TEMPO_MAXIMO = 900  # 15 minutos sem interação
    if 'ultima_atividade' in st.session_state and agora - st.session_state['ultima_atividade'] > TEMPO_MAXIMO:
        registrar_auditoria(username, "Logout (Inatividade)", "Acesso", f"Sessão de {username} expirou por inatividade.")
        st.session_state.update({'authentication_status': None, 'sessao_expirada': True, 'login_registrado': False})
        del st.session_state['ultima_atividade']
        st.rerun()
        
    st.session_state['sessao_expirada'] = False
    st.session_state['ultima_atividade'] = agora

    user_info = credentials["usernames"].get(username, {})
    user_role = user_info.get("role", "estagiario")
    
    precisa_trocar_senha = user_info.get("trocar_senha", False) if username != "master" else False

    if precisa_trocar_senha:
        st.markdown("<h2 style='text-align: center; color: #D4AF37;'>🔒 PRIMEIRO ACESSO DETECTADO</h2>", unsafe_allow_html=True)
        st.warning(f"Olá, **{name}**! Por razões de segurança do escritório, você deve cadastrar uma nova senha pessoal antes de acessar o sistema.")
        
        col_pa1, col_pa2, col_pa3 = st.columns([1, 2, 1])
        with col_pa2:
            with st.form("form_primeiro_acesso"):
                nova_s = st.text_input("Nova Senha Pessoal", type="password")
                conf_s = st.text_input("Confirme a Nova Senha", type="password")
                
                if st.form_submit_button("Atualizar Senha e Entrar", type="primary"):
                    if not nova_s or nova_s != conf_s:
                        st.error("As senhas não coincidem ou estão em branco.")
                    elif nova_s == "mudar123":
                        st.error("A nova senha não pode ser igual à senha padrão ('mudar123'). Escolha uma senha segura.")
                    else:
                        hash_novo = gerar_hash(nova_s)
                        try:
                            try:
                                supabase.table("usuarios_sistema").update({
                                    "senha_hash": hash_novo,
                                    "password": hash_novo,
                                    "trocar_senha": False
                                }).eq("username", username).execute()
                            except Exception:
                                supabase.table("usuarios_sistema").update({
                                    "senha_hash": hash_novo,
                                    "password": hash_novo
                                }).eq("username", username).execute()
                            
                            registrar_auditoria(username, "Troca de Senha Obrigatória", "Segurança", "Senha alterada com sucesso no primeiro acesso.")
                            st.cache_data.clear()
                            confirmar_operacao("🎉 Senha alterada com sucesso! Liberando acesso ao sistema...")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar senha no banco: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⬅️ Sair / Voltar para a Tela de Login", use_container_width=True):
                registrar_auditoria(username, "Logout (Primeiro Acesso)", "Acesso", f"Usuário {username} optou por sair na tela de primeiro acesso.")
                st.session_state.update({
                    'authentication_status': None,
                    'login_registrado': False,
                    'name': None,
                    'username': None
                })
                if 'ultima_atividade' in st.session_state:
                    del st.session_state['ultima_atividade']
                st.rerun()
        
        st.stop()

    if 'pagina_atual' not in st.session_state: st.session_state['pagina_atual'] = "🏠 Página Inicial"
    if 'submenu_atual' not in st.session_state: st.session_state['submenu_atual'] = ""
    
    if 'ocultar_vencidos' not in st.session_state: st.session_state['ocultar_vencidos'] = set()
    if 'ocultar_urgentes' not in st.session_state: st.session_state['ocultar_urgentes'] = set()
    if 'ocultar_lembretes' not in st.session_state: st.session_state['ocultar_lembretes'] = set()

    def validar_cpf(cpf):
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) != 11 or cpf == cpf[0] * 11: return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        d1 = (soma * 10) % 11; d1 = 0 if d1 == 10 else d1
        if d1 != int(cpf[9]): return False
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        d2 = (soma * 10) % 11; d2 = 0 if d2 == 10 else d2
        return d2 == int(cpf[10])

    @st.cache_data(ttl=300)
    def carregar_dados(tabela):
        res = supabase.table(tabela).select("*").execute()
        return res.data if res.data else []

    def importar_excel_para_supabase(tabela, arquivo):
        try:
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)
            
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
            df = df.dropna(how='all', axis=1)
            df.columns = df.columns.str.strip().str.lower()
            
            df = df.where(pd.notnull(df), "")
            df = df.fillna("")
            
            for col in df.columns:
                if 'data' in col.lower() or 'vencimento' in col.lower():
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                    df[col] = df[col].replace(['NaT', 'nan', 'NAT', 'NaN', 'None', ''], None)
                elif 'hora' in col.lower():
                    df[col] = df[col].apply(lambda x: x.strftime('%H:%M:%S') if hasattr(x, 'strftime') else (str(x) if x != "" else None))

            dados = df.to_dict(orient="records")
            dadosLimpos = [{k: (v if pd.notnull(v) and v != "" else None) for k, v in registro.items()} for registro in dados]

            supabase.table(tabela).insert(dadosLimpos).execute()
            registrar_auditoria(username, "Importação Excel", tabela, f"{len(dadosLimpos)} registros importados.")
            st.cache_data.clear()
            confirmar_operacao(f"🎉 {len(dadosLimpos)} registros importados com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ Erro ao importar planilha: {e}")

    def colorir_status(val):
        if str(val).lower() == 'pendente' or str(val).lower() == 'aguardando documentação':
            return 'color: #FF4B4B; font-weight: bold;'
        elif str(val).lower() in ['manifestado', 'concluído', 'pago', 'entregue', 'distribuído', 'protocolado']:
            return 'color: #00CC96; font-weight: bold;'
        elif str(val).lower() in ['em andamento', 'produzindo peça', 'aguardando revisão', 'acompanhando movimentações']:
            return 'color: #FFA15A; font-weight: bold;'
        return ''

    with st.sidebar:
        user_foto = user_info.get("foto_url", None)
        col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
        with col_f2:
            if user_foto:
                st.image(user_foto, use_container_width=True)
            else:
                st.markdown("<h1 style='text-align: center; margin: 0;'>👤</h1>", unsafe_allow_html=True)

        st.write(f"Logado como: **{name}**")
        p_txt = {"admin": "Sócio", "advogado": "Advogado(a)", "bacharel": "Bacharel(a)"}.get(user_role, "Estagiário")
        st.caption(f"Perfil: {p_txt}")
        
        if st.button("Sair", use_container_width=True):
            registrar_auditoria(username, "Logout", "Acesso", f"Usuário {name} ({username}) efetuou logout do sistema.")
            st.session_state.update({'authentication_status': None, 'login_registrado': False})
            st.rerun()

        # Atualização automática do cronômetro sem reiniciar a página inteira.
        # A execução periódica NÃO renova a última atividade do usuário.
        @st.fragment(run_every="1s")
        def mostrar_tempo_sessao():
            restante = max(0, int(TEMPO_MAXIMO - (time.time() - st.session_state.get('ultima_atividade', time.time())) + 0.999))
            minutos, segundos = divmod(restante, 60)
            st.markdown(f"**Sessão expira em:**  `{minutos:02d}:{segundos:02d}`")
            if restante <= 0:
                registrar_auditoria(username, "Logout (Inatividade)", "Acesso", f"Sessão de {username} expirou por inatividade.")
                st.session_state.update({'authentication_status': None, 'sessao_expirada': True, 'login_registrado': False})
                st.session_state.pop('ultima_atividade', None)
                st.rerun(scope="app")

        mostrar_tempo_sessao()
        st.markdown("---")
        
        st.subheader("Módulos do Sistema")
        # Os rótulos exibidos são sóbrios; os identificadores internos não mudam.
        modulos = {
            "Página Inicial": "🏠 Página Inicial",
            "Clientes": "Clientes",
            "Prospectados Pendentes": "Prospectados Pendentes",
            "Meus Processos": "Meus Processos",
            "Pagamentos": "Pagamentos",
            "Perícias": "Perícias",
            "Expedientes": "Expedientes",
            "Expedientes TRF": "Expedientes TRF",
            "Pendências": "Pendências",
            "Equipe Dejure": "Equipe Dejure",
            "Segurança": "Segurança"
        }

        if user_role == 'admin':
            modulos["Distribuição de Processos"] = "Distribuição de Processos"
            modulos["Auditoria"] = "Auditoria"
            modulos["Balanço Financeiro"] = "Balanço Financeiro"
            modulos["Gerenciar Baixas"] = "Gerenciar Baixas"
            if username == "master":
                modulos["Gerenciar Protocolos"] = "Gerenciar Protocolos"

        for label, pag in modulos.items():
            if st.button(label, use_container_width=True):
                st.session_state['pagina_atual'] = pag
                st.session_state['submenu_atual'] = "" if pag == "🏠 Página Inicial" else {
                    "Clientes": "Consultar Clientes", 
                    "Prospectados Pendentes": "Consultar Prospectados Pendentes",
                    "Meus Processos": "Consultar Meus Processos",
                    "Pagamentos": "Ver Parcelas", 
                    "Perícias": "Ver Perícias", 
                    "Expedientes": "Consultar Expedientes", 
                    "Expedientes TRF": "Consultar Expedientes TRF",
                    "Pendências": "Consultar Pendências",
                    "Equipe Dejure": "Nossa Equipe",
                    "Segurança": "Meu Perfil",
                    "Distribuição de Processos": "Fila de Distribuição",
                    "Auditoria": "Ver Logs",
                    "Balanço Financeiro": "Painel Financeiro",
                    "Gerenciar Baixas": "Gerenciar Baixas"
                }.get(pag, "")
                limpar_flags_cadastro()
                st.rerun()
        
        # --- RADIO DEJURE: catálogo brasileiro dinâmico, sem alterações no banco ---
        st.markdown("---")
        st.markdown("<div style='color:#D4AF37;font-weight:700;font-size:1rem;margin-bottom:6px'>📻 Rádio DEJURE</div>", unsafe_allow_html=True)
        import streamlit.components.v1 as dejure_components
        dejure_components.html(r"""
        <!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
        <style>
          *{box-sizing:border-box}body{margin:0;background:#1a1e24;color:#eee;font:12px Arial,sans-serif}
          .radio{padding:11px;border:1px solid #51452b;border-radius:12px;background:#1a1e24}
          label{display:block;color:#d4af37;font-weight:600;margin:0 0 5px}
          select,input[type=search]{width:100%;background:#252a31;color:#f0f0f0;border:1px solid #555044;border-radius:7px;padding:8px;font-size:12px;min-width:0}
          input[type=search]{margin-bottom:8px}select{margin-bottom:6px}
          .controls{display:flex;align-items:center;gap:7px;margin-top:7px}
          button{background:#d4af37;color:#17191d;border:0;border-radius:7px;padding:9px 11px;font-weight:700;cursor:pointer;white-space:nowrap}
          button:hover{background:#e5c75d}input[type=range]{min-width:0;flex:1;accent-color:#d4af37}
          .status{color:#b9bdc3;font-size:11px;margin-top:8px;min-height:28px;overflow-wrap:anywhere;line-height:1.4}
          .small{color:#a9adb5;font-size:10px;margin:3px 0 0}
        </style></head><body>
        <div class="radio">
          <label for="busca">Buscar estação</label><input type="search" id="busca" placeholder="Nome ou estilo musical..." autocomplete="off">
          <label for="estacao">Escolha uma rádio</label><select id="estacao" aria-label="Estação de rádio"></select>
          <div class="controls"><button id="toggle" type="button">▶ Ouvir</button>
            <span title="Volume">🔊</span><input id="volume" type="range" min="0" max="100" value="65" aria-label="Volume"></div>
          <div id="status" class="status" role="status">Carregando catálogo de rádios brasileiras...</div>
          <div class="small">30+ brasileiras (catálogo online) e 5 internacionais.</div>
          <audio id="audio" preload="none"></audio>
        </div>
        <script>
        (()=>{
          const audio=document.getElementById('audio'), sel=document.getElementById('estacao');
          const btn=document.getElementById('toggle'), msg=document.getElementById('status');
          const busca=document.getElementById('busca'); audio.volume=.65;
          const fixas=[
            ['🇧🇷 Brasileiras · Música','Antena 1','https://antenaone.crossradio.com.br/stream/1;'],
            ['🇧🇷 Brasileiras · Música','Bossa Jazz Brasil','https://centova5.transmissaodigital.com:20104/live'],
            ['🇧🇷 Brasileiras · Música','Jovem Pan FM Florianópolis','https://live.paineldj.com.br/proxy/jfloripa?mp=/stream'],
            ['🇧🇷 Brasileiras · Música','Jovem Pan BH','https://8062.brasilstream.com.br/mp3'],
            ['🇧🇷 Brasileiras · Música','Rádio Roberto Carlos','https://stream.zeno.fm/erbpkq1cz55vv'],
            ['🇧🇷 Brasileiras · Música','Rádio Reggae Brasil','https://casthttps.suaradionanet.net/13805/stream'],
            ['🇧🇷 Brasileiras · Notícias e Cultura','Rádio Câmara','https://stream3.camara.leg.br/radiocamara1t64'],
            ['🇧🇷 Brasileiras · Notícias e Cultura','Rádio Senado','https://radioaovivo.senado.leg.br:443/fm.mp3'],
            ['🌎 Internacionais','Groove Salad · Ambient','https://ice1.somafm.com/groovesalad-128-mp3'],
            ['🌎 Internacionais','Secret Agent · Lounge','https://ice1.somafm.com/secretagent-128-mp3'],
            ['🌎 Internacionais','Drone Zone · Relax','https://ice1.somafm.com/dronezone-128-mp3'],
            ['🌎 Internacionais','Indie Pop Rocks · Indie','https://ice1.somafm.com/indiepop-128-mp3'],
            ['🌎 Internacionais','DEF CON Radio · Eletrônica','https://ice1.somafm.com/defcon-128-mp3']
          ];
          let catalogo=fixas.slice(); let urlAtual='';
          const texto=(s)=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
          function categoria(r){
            const t=texto((r.name||'')+' '+(r.tags||''));
            if(/noticia|news|jornal|talk|informativ|esporte|politic/.test(t))return '🇧🇷 Notícias e Esportes';
            if(/sertanej|country|modao|forro|piseiro/.test(t))return '🇧🇷 Sertanejo e Regional';
            if(/gospel|crista|religios|evangelic/.test(t))return '🇧🇷 Gospel e Religiosas';
            if(/mpb|bossa|samba|pagode|brasilidades|jazz/.test(t))return '🇧🇷 MPB, Samba e Jazz';
            if(/rock|metal|alternativ/.test(t))return '🇧🇷 Rock';
            if(/pop|hits|dance|eletron|jovem/.test(t))return '🇧🇷 Pop e Eletrônica';
            return '🇧🇷 Variedades e Música';
          }
          function desenhar(){
            const anterior=sel.value; const filtro=texto(busca.value.trim()); sel.replaceChildren();
            const grupos=new Map();
            for(const item of catalogo){
              if(filtro&&!texto(item[1]+' '+item[0]).includes(filtro))continue;
              if(!grupos.has(item[0]))grupos.set(item[0],[]); grupos.get(item[0]).push(item);
            }
            for(const [titulo,itens] of grupos){
              const grupo=document.createElement('optgroup');grupo.label=titulo;
              for(const [,nome,url] of itens){const op=document.createElement('option');op.value=url;op.textContent=nome;grupo.appendChild(op);}
              sel.appendChild(grupo);
            }
            if(anterior&&Array.from(sel.options).some(x=>x.value===anterior))sel.value=anterior;
            if(!sel.options.length){const op=document.createElement('option');op.textContent='Nenhuma estação encontrada';op.value='';sel.appendChild(op);}
          }
          function atualizar(){btn.textContent=audio.paused?'▶ Ouvir':'❚❚ Pausar';}
          async function tocar(){
            if(!sel.value)return;
            if(urlAtual!==sel.value){audio.src=sel.value;urlAtual=sel.value;audio.load();}
            msg.textContent='Conectando à estação...';
            try{await audio.play();msg.textContent='Ao vivo · '+sel.options[sel.selectedIndex].textContent;}
            catch(e){msg.textContent='Não foi possível reproduzir esta estação. Tente outra.';}
            atualizar();
          }
          btn.addEventListener('click',()=>{if(audio.paused)tocar();else{audio.pause();msg.textContent='Reprodução pausada.';atualizar();}});
          sel.addEventListener('change',()=>{const tocando=!audio.paused;audio.pause();audio.removeAttribute('src');urlAtual='';audio.load();atualizar();msg.textContent='Estação selecionada.';if(tocando)tocar();});
          busca.addEventListener('input',desenhar);
          document.getElementById('volume').addEventListener('input',e=>{audio.volume=Number(e.target.value)/100;});
          audio.addEventListener('error',()=>{msg.textContent='Transmissão indisponível ou bloqueada pelo navegador. Selecione outra.';atualizar();});
          audio.addEventListener('pause',atualizar);audio.addEventListener('play',atualizar);
          desenhar();
          async function carregarBrasileiras(){
            // Catálogo público com verificações periódicas de funcionamento.
            // Não depende de chave, Supabase nem alterações no requirements.txt.
            const servidores=['https://de1.api.radio-browser.info','https://nl1.api.radio-browser.info','https://at1.api.radio-browser.info'];
            for(const servidor of servidores){
              const ctrl=new AbortController();const timer=setTimeout(()=>ctrl.abort(),6500);
              try{
                const url=servidor+'/json/stations/search?countrycode=BR&hidebroken=true&order=votes&reverse=true&limit=350';
                const res=await fetch(url,{signal:ctrl.signal,headers:{'Accept':'application/json'}});
                if(!res.ok)throw Error('Serviço temporariamente indisponível');
                const lista=await res.json();if(!Array.isArray(lista))throw Error('Resposta inválida');
                const existentes=new Set(catalogo.map(x=>texto(x[1])));
                const urls=new Set(catalogo.map(x=>x[2].toLowerCase()));
                const novas=[];
                for(const r of lista){
                  const nome=String(r.name||'').trim().replace(/\s+/g,' ');
                  const link=String(r.url_resolved||r.url||'').trim();
                  if(!nome||nome.length>75||!link.startsWith('https://'))continue;
                  if(!['MP3','AAC','AAC+'].includes(String(r.codec||'').toUpperCase()))continue;
                  if(r.hls||r.lastcheckok===0||/\.(m3u8?|pls)(\?|$)/i.test(link))continue;
                  if(existentes.has(texto(nome))||urls.has(link.toLowerCase()))continue;
                  existentes.add(texto(nome));urls.add(link.toLowerCase());
                  novas.push([categoria(r),nome,link]);
                  if(novas.length>=35)break;
                }
                if(novas.length<20)throw Error('Catálogo insuficiente');
                catalogo=fixas.concat(novas);desenhar();
                msg.textContent='Catálogo carregado: '+(novas.length+8)+' rádios brasileiras e 5 internacionais. Escolha uma estação e clique em Ouvir.';
                return;
              }catch(e){}finally{clearTimeout(timer);}
            }
            msg.textContent='Catálogo online indisponível. As 8 brasileiras e 5 internacionais fixas continuam disponíveis.';
          }
          carregarBrasileiras();
        })();
        </script></body></html>
        """, height=256, scrolling=False)
        st.caption("Busca e categorias; catálogo brasileiro atualizado online. O áudio pode parar ao navegar entre módulos.")

        st.markdown("---")
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.write("**DEJURE ADVOCACIA**")


    # --- PLACAR DE PROTOCOLOS: inclui toda a equipe, mesmo com zero pontos ---
    def montar_ranking_protocolos(eventos, credenciais):
        # O protocolo armazena o nome do usuário autenticado.
        nomes = {}
        for login, info in credenciais['usernames'].items():
            if login != 'master' and info.get('role') not in ('inativo', 'bloqueado'):
                nome = str(info.get('name') or login).strip()
                if nome:
                    nomes[nome.casefold()] = nome
        contagem = {chave: 0 for chave in nomes}
        for evento in eventos:
            nome = str(evento.get('protocolado_por') or '').strip()
            if nome:
                chave = nome.casefold()
                # Preserva pontuação de usuários removidos, sem perder histórico.
                if chave not in nomes:
                    nomes[chave] = nome
                    contagem[chave] = 0
                contagem[chave] += 1
        return sorted(((nomes[chave], total) for chave, total in contagem.items()),
                      key=lambda item: (-item[1], item[0].casefold()))

    def exibir_placar_protocolos(eventos, mes_escolhido, credenciais):
        """Placar premium: somente apresentação; mantém as regras e os dados originais."""
        ranking = montar_ranking_protocolos(eventos, credenciais)
        total = sum(pontos for _, pontos in ranking)
        com_protocolos = sum(pontos > 0 for _, pontos in ranking)
        maior = ranking[0][1] if ranking else 0
        lideres = [nome for nome, pontos in ranking if pontos == maior] if maior else []

        st.markdown("""
        <style>
        .dj-placar {font-family:Inter,'Segoe UI',Arial,sans-serif;color:#E7E9EC;}
        .dj-placar .dj-kpis {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:12px 0 16px;}
        .dj-placar .dj-kpi {background:#1C2229;border:1px solid #343A40;border-radius:12px;padding:15px 17px;}
        .dj-placar .dj-kpi-label {font-size:12px;color:#B4BAC2;margin-bottom:8px;}
        .dj-placar .dj-kpi-number {font-size:29px;line-height:1.1;color:#D4AF37;font-weight:750;}
        .dj-placar .dj-destaque {background:#262219;border:1px solid #75602C;border-radius:12px;padding:16px 18px;margin-bottom:19px;}
        .dj-placar .dj-destaque-label {font-size:12px;letter-spacing:.07em;font-weight:750;color:#D4AF37;margin-bottom:7px;}
        .dj-placar .dj-destaque-nome {color:#F3E5BD;font-size:17px;font-weight:700;overflow-wrap:anywhere;}
        .dj-placar .dj-destaque-sub {font-size:12px;color:#C7BA96;margin-top:5px;}
        .dj-placar .dj-rank-title {font-size:15px;font-weight:700;color:#D4AF37;margin-bottom:12px;}
        .dj-placar .dj-rank-item {display:flex;gap:13px;align-items:center;background:#1A1E24;border:1px solid #30353B;border-radius:10px;padding:11px 13px;margin-bottom:8px;}
        .dj-placar .dj-rank-item.dj-first {border-color:#75602C;background:#211F1B;}
        .dj-placar .dj-rank-pos {flex:0 0 38px;height:35px;border-radius:9px;background:#2C323A;color:#D6D9DF;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:750;}
        .dj-placar .dj-first .dj-rank-pos {background:#6B5522;color:#FFE19A;}
        .dj-placar .dj-rank-main {flex:1;min-width:0;}
        .dj-placar .dj-rank-head {display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:8px;}
        .dj-placar .dj-rank-name {font-size:13px;color:#E7E9EC;font-weight:550;overflow-wrap:anywhere;}
        .dj-placar .dj-first .dj-rank-name {color:#F4D27B;font-weight:700;}
        .dj-placar .dj-rank-score {font-size:15px;color:#D4AF37;font-weight:750;white-space:nowrap;}
        .dj-placar .dj-rank-track {height:6px;border-radius:99px;background:#30353D;overflow:hidden;}
        .dj-placar .dj-rank-fill {height:100%;border-radius:99px;background:#967F42;}
        .dj-placar .dj-first .dj-rank-fill {background:#D4AF37;}
        @media(max-width:650px) {.dj-placar .dj-kpis {gap:6px;} .dj-placar .dj-kpi {padding:10px 8px;} .dj-placar .dj-kpi-number {font-size:23px;} .dj-placar .dj-kpi-label {font-size:10px;} .dj-placar .dj-rank-item {padding:10px 8px;gap:8px;}}
        </style>
        """, unsafe_allow_html=True)

        kpis = (
            ('Protocolos no mês', total),
            ('Usuários no placar', len(ranking)),
            ('Com protocolos', com_protocolos),
        )
        kpi_html = ''.join(
            f'<div class="dj-kpi"><div class="dj-kpi-label">{html.escape(rotulo)}</div>'
            f'<div class="dj-kpi-number">{valor}</div></div>'
            for rotulo, valor in kpis
        )
        if len(lideres) == 1:
            destaque_nome = html.escape(lideres[0])
            destaque_sub = f'{maior} processo(s) protocolado(s) em {html.escape(mes_escolhido)}'
            destaque_rotulo = '★ DESTAQUE DO MÊS'
        elif lideres:
            destaque_nome = ' · '.join(html.escape(nome) for nome in lideres)
            destaque_sub = f'Empate: {maior} protocolo(s) por colaborador em {html.escape(mes_escolhido)}'
            destaque_rotulo = '★ DESTAQUES DO MÊS — EMPATE'
        else:
            destaque_nome = 'Aguardando primeiros protocolos'
            destaque_sub = f'Nenhum protocolo registrado em {html.escape(mes_escolhido)}'
            destaque_rotulo = '★ DESTAQUE DO MÊS'

        linhas = []
        # Classificação de competição: pontuações iguais têm a mesma posição.
        # Exemplo: 8, 8, 5, 3 -> 1º, 1º, 3º, 4º.
        posicao_anterior = None
        pontos_anteriores = None
        for indice, (nome, pontos) in enumerate(ranking, 1):
            if pontos != pontos_anteriores:
                posicao_anterior = indice
                pontos_anteriores = pontos
            posicao = posicao_anterior
            porcentagem = (100 * pontos / maior) if maior else 0
            classe = ' dj-first' if pontos > 0 and pontos == maior else ''
            linhas.append(
                f'<div class="dj-rank-item{classe}">'
                f'<div class="dj-rank-pos">{posicao}º</div>'
                f'<div class="dj-rank-main"><div class="dj-rank-head">'
                f'<span class="dj-rank-name">{html.escape(nome)}</span>'
                f'<span class="dj-rank-score">{pontos}</span></div>'
                f'<div class="dj-rank-track"><div class="dj-rank-fill" style="width:{porcentagem:.2f}%"></div></div>'
                f'</div></div>'
            )
        lista_html = ''.join(linhas) if linhas else '<p>Nenhum colaborador cadastrado.</p>'
        st.markdown(
            '<div class="dj-placar">'
            '<div class="dj-kpis">' + kpi_html + '</div>'
            '<div class="dj-destaque">'
            f'<div class="dj-destaque-label">{destaque_rotulo}</div>'
            f'<div class="dj-destaque-nome">{destaque_nome}</div>'
            f'<div class="dj-destaque-sub">{destaque_sub}</div></div>'
            '<div class="dj-rank-title">Ranking da equipe</div>'
            + lista_html + '</div>',
            unsafe_allow_html=True,
        )
        st.caption('Pontuação atribuída a quem registrou o protocolo. Cada processo conta uma vez; registros antigos sem protocolante não entram no placar.')
        return lideres

    menu_escolha = st.session_state['pagina_atual']

    if menu_escolha == "🏠 Página Inicial":
        if os.path.exists("logo.png"):
            # Logo centralizada: 60% menor que a versão anterior (24% da largura útil).
            # Redução adicional de 40%, preservando a proporção original.
            # Não modifica as logos do login ou da barra lateral.
            _logo_esquerda, _logo_centro, _logo_direita = st.columns([38, 24, 38], gap="small")
            with _logo_centro:
                st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #D4AF37;'>⚖️ DEJURE ADVOCACIA</h2>", unsafe_allow_html=True)

        st.markdown(f"### Seja bem-vindo, {name}! ⚖️")
        st.markdown("### 📊 Visão Geral do Escritório")
        
        try:
            cli, pros_pend, hon, per, exp, exp_trf, pen = carregar_dados("clientes_cadastrados"), carregar_dados("prospectados_pendentes"), carregar_dados("honorarios"), carregar_dados("pericias"), carregar_dados("expedientes"), carregar_dados("expedientes_trf"), carregar_dados("pendencias")
            parcelas_db = carregar_dados("parcelas")
            
            # Filtra apenas os prospectados que ainda NÃO foram atendidos para o contador da Visão Geral
            pros_pendentes_reais = [p for p in pros_pend if not p.get('atendido', False)]

            per_pendentes_com_data = 0
            for p in per:
                if p.get('status') == 'Pendente' and (p.get('data_pm') or p.get('data_ps')):
                    per_pendentes_com_data += 1

            # Duas linhas evitam truncamento em telas comuns e notebooks.
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Clientes", len(cli))
            c2.metric("Prospectados Pendentes", len(pros_pendentes_reais))
            c3.metric("Contratos", len(hon))
            c4.metric("Perícias Pendentes", per_pendentes_com_data)
            c5, c6, c7 = st.columns(3)
            c5.metric("Expedientes Pendentes", len([e for e in exp if e.get('status') == 'Pendente' and e.get('data_manifestacao')]))
            c6.metric("Expedientes TRF Pendentes", len([et for et in exp_trf if et.get('status') == 'Pendente' and et.get('data_manifestacao')]))
            c7.metric("Parcelas Pendentes", len([pc for pc in parcelas_db if pc.get('status') == 'Pendente' and pc.get('vencimento')]))
        except Exception: pass

        st.markdown("---")
        # Placar calculado a partir dos eventos de protocolo, sem alterar
        # os registros existentes nem depender da data de atualização.
        st.subheader("Placar mensal de processos protocolados")
        hoje_placar = date.today()
        meses_placar = [(hoje_placar.replace(day=1) - relativedelta(months=i)) for i in range(12)]
        opcoes_meses = {m.strftime("%m/%Y"): m for m in meses_placar}
        mes_escolhido = st.selectbox("Mês de referência", list(opcoes_meses), key="mes_placar_inicio")
        inicio_mes = opcoes_meses[mes_escolhido]
        fim_mes = inicio_mes + relativedelta(months=1)
        ranking_placar = []
        destaque_automatico = None
        try:
            # Consulta privilegiada somente no servidor, após login.
            consulta = (cliente_storage_servidor().table('dejure_protocolos')
                .select('processo_id,protocolado_por,protocolado_em')
                .gte('protocolado_em', inicio_mes.isoformat())
                .lt('protocolado_em', fim_mes.isoformat())
                .limit(10000).execute())
            eventos = consulta.data or []
            if len(eventos) == 10000:
                st.warning('O limite de 10.000 eventos foi atingido. O placar pode estar incompleto.')
            lideres = exibir_placar_protocolos(eventos, mes_escolhido, credentials)
        except Exception:
            st.error('Placar indisponível. Execute o SQL de protocolos no Supabase e confira os Secrets do Streamlit.')


        # RPV: painel permanente, pois estes recebíveis NÃO possuem vencimento.
        st.markdown("---")
        st.subheader("🏛️ RPVs / Retroativos — aguardando liberação")
        try:
            rpv_inicio = 0
            rpvs_abertas = []
            while True:
                lote_rpv = (cliente_storage_servidor().table('dejure_rpv_recebiveis')
                            .select('id,cliente,servico,valor,percentual_rpv,valor_rpv_bruto,status,observacoes')
                            .eq('status', 'Aguardando liberação')
                            .range(rpv_inicio, rpv_inicio + 999).execute().data or [])
                rpvs_abertas.extend(lote_rpv)
                if len(lote_rpv) < 1000:
                    break
                rpv_inicio += 1000
            st.caption("Recebíveis sem data de vencimento. Permanecem visíveis até a liberação da RPV.")
            st.metric("RPVs aguardando liberação", len(rpvs_abertas))
            with st.expander(f"Ver RPVs em acompanhamento ({len(rpvs_abertas)})", expanded=bool(rpvs_abertas)):
                if rpvs_abertas:
                    for r in sorted(rpvs_abertas, key=lambda x: str(x.get('cliente') or '')):
                        st.info(f"**Cliente:** {r.get('cliente') or 'Não informado'} | **Serviço:** {r.get('servico') or 'RPV'} | **Honorários sobre RPV:** {r.get('percentual_rpv') or 0}% | **Valor da RPV:** a definir | **Situação:** aguardando liberação")
                else:
                    st.success("Nenhuma RPV aguardando liberação.")
        except Exception:
            st.caption("Painel RPV indisponível. Execute primeiro o SQL de instalação da tabela dejure_rpv_recebiveis.")

        st.markdown("---")
        try:
            hoje = date.today()
            alertas_pericias = []
            alertas_expedientes = []
            alertas_expedientes_trf = []
            alertas_pagamentos = []

            # Relaciona cada parcela ao cliente do contrato de honorários.
            # Mantém os dados carregados na Visão Geral, sem novas consultas.
            clientes_por_honorario = {
                str(h.get('id')): str(h.get('cliente') or 'Não informado').strip()
                for h in hon if h.get('id') is not None
            }

            for p in per:
                if p.get('status') == 'Pendente':
                    if p.get('data_pm'):
                        dt = datetime.strptime(p['data_pm'], "%Y-%m-%d").date()
                        dias_restantes = (dt - hoje).days
                        if dias_restantes <= 7:
                            uid = f"per_{p['id']}_pm"
                            alertas_pericias.append((dias_restantes, f"🔬 Perícia Médica | Cliente: {p.get('nome') or 'Não informado'} | Data PM: {dt.strftime('%d/%m/%Y')}", uid, 'pericia'))
                    if p.get('data_ps'):
                        dt = datetime.strptime(p['data_ps'], "%Y-%m-%d").date()
                        dias_restantes = (dt - hoje).days
                        if dias_restantes <= 7:
                            uid = f"per_{p['id']}_ps"
                            alertas_pericias.append((dias_restantes, f"🔬 Perícia Social | Cliente: {p.get('nome') or 'Não informado'} | Data PS: {dt.strftime('%d/%m/%Y')}", uid, 'pericia'))

            for e in exp:
                if e.get('status') == 'Pendente' and e.get('data_manifestacao'):
                    dt = datetime.strptime(e['data_manifestacao'], "%Y-%m-%d").date()
                    uid = f"exp_{e.get('id', 0)}"
                    if (dt - hoje).days <= 7:
                        alertas_expedientes.append(((dt - hoje).days, f"📂 Processo: {e['numero_processo']} | Cliente: {e.get('cliente', 'N/D')} | Prazo: {dt.strftime('%d/%m/%Y')} | Resp: {e['responsavel']}", uid, 'expediente'))

            for et in exp_trf:
                if et.get('status') == 'Pendente' and et.get('data_manifestacao'):
                    dt = datetime.strptime(et['data_manifestacao'], "%Y-%m-%d").date()
                    uid = f"trf_{et.get('id', 0)}"
                    if (dt - hoje).days <= 7:
                        alertas_expedientes_trf.append(((dt - hoje).days, f"⚖️ Processo: {et['numero_processo']} | Cliente: {et.get('cliente', 'N/D')} | Prazo: {dt.strftime('%d/%m/%Y')} | Resp: {et['responsavel']}", uid, 'expediente_trf'))

            for pc in parcelas_db:
                if pc.get('status') == 'Pendente' and pc.get('vencimento'):
                    dt = datetime.strptime(pc['vencimento'], "%Y-%m-%d").date()
                    uid = f"pag_{pc.get('id', 0)}"
                    if (dt - hoje).days <= 7:
                        alertas_pagamentos.append(((dt - hoje).days, f"💰 Cliente: {clientes_por_honorario.get(str(pc.get('honorario_id')), 'Não informado')} | Parcela {pc.get('numero_parcela')} | Vencimento: {dt.strftime('%d/%m/%Y')} | Valor: {formatar_moeda_br(pc.get('valor', 0))}", uid, 'pagamento'))

            total_alertas = len(alertas_pericias) + len(alertas_expedientes) + len(alertas_expedientes_trf) + len(alertas_pagamentos)

            if total_alertas > 0:
                st.subheader("🚨 Central de Alertas de Prazos e Vencimentos")
                st.caption("Alertas exibidos a partir de 7 dias antes do vencimento. Itens vencidos permanecem visíveis enquanto estiverem pendentes.")
                
                tab_per, tab_exp, tab_trf, tab_pag = st.tabs(["🔬 Perícias", "📂 Expedientes", "⚖️ Expedientes TRF", "💰 Pagamentos"])

                def renderizar_lista_alerta(lista_alertas, nome_cat):
                    lista_visivel = [
                        item for item in lista_alertas 
                        if item[2] not in st.session_state['ocultar_vencidos'] 
                        and item[2] not in st.session_state['ocultar_urgentes'] 
                        and item[2] not in st.session_state['ocultar_lembretes']
                    ]

                    if not lista_visivel:
                        st.info("Nenhum alerta pendente visível nesta categoria.")
                        return

                    if user_role == 'admin':
                        st.markdown(f"##### ⚡ Limpeza Visual (Apenas Tela)")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        
                        with col_b1:
                            if st.button(f"🔴 Ocultar Vencidos", key=f"btn_venc_{nome_cat}"):
                                for item in lista_alertas:
                                    if item[0] < 0:
                                        st.session_state['ocultar_vencidos'].add(item[2])
                                st.rerun()

                        with col_b2:
                            if st.button(f"🟠 Ocultar Críticos/Urgentes", key=f"btn_urg_{nome_cat}"):
                                for item in lista_alertas:
                                    if 0 <= item[0] <= 3:
                                        st.session_state['ocultar_urgentes'].add(item[2])
                                st.rerun()

                        with col_b3:
                            if st.button(f"🟢 Ocultar Lembretes", key=f"btn_lemb_{nome_cat}"):
                                for item in lista_alertas:
                                    if item[0] > 3:
                                        st.session_state['ocultar_lembretes'].add(item[2])
                                st.rerun()
                        st.markdown("---")

                    for dias, texto, uid, _ in sorted(lista_visivel, key=lambda x: x[0]):
                        if dias < 0: st.error(f"⚠️ **VENCIDO ({abs(dias)} dias):** {texto}")
                        elif dias == 1: st.error(f"🚨 **CRÍTICO (1 dia):** {texto}")
                        elif dias <= 3: st.warning(f"⚠️ **URGENTE ({dias} dias):** {texto}")
                        else: st.info(f"📅 **LEMBRETE ({dias} dias):** {texto}")

                with tab_per:
                    renderizar_lista_alerta(alertas_pericias, "pericias")
                with tab_exp:
                    renderizar_lista_alerta(alertas_expedientes, "expedientes")
                with tab_trf:
                    renderizar_lista_alerta(alertas_expedientes_trf, "expedientes_trf")
                with tab_pag:
                    renderizar_lista_alerta(alertas_pagamentos, "pagamentos")
            else:
                st.info("🎉 Nenhum prazo pendente vencido ou com vencimento nos próximos 7 dias!")
        except Exception as e: 
            st.error(f"Erro ao carregar central de alertas: {e}")

    elif menu_escolha == "Gerenciar Baixas":
        if user_role != 'admin':
            st.error('Acesso exclusivo aos administradores.')
            st.stop()
        st.title('Gerenciar Baixas de Parcelas')
        st.caption('Consulte, corrija ou cancele baixas. Cada alteração é preservada na auditoria. Parcelas históricas não geram repasses.')
        try:
            cliente_fin = cliente_storage_servidor()
            eventos_ativos = dejure_logs_repasses_ativos(cliente_fin)
            todas_parcelas = {}
            inicio_par = 0
            while True:
                lote_par = cliente_fin.table('parcelas').select('*').range(inicio_par, inicio_par + 999).execute().data or []
                todas_parcelas.update({str(p['id']): p for p in lote_par})
                if len(lote_par) < 1000:
                    break
                inicio_par += 1000
        except Exception as exc:
            st.error(f'Falha ao consultar baixas: {exc}')
            st.stop()
        # Clientes vinculados aos contratos, inclusive contratos integralmente quitados.
        try:
            contratos_baixas = {}
            inicio_h = 0
            while True:
                lote_h = cliente_fin.table('honorarios').select('id,cliente,servico').range(inicio_h, inicio_h + 999).execute().data or []
                for h in lote_h:
                    contratos_baixas[str(h['id'])] = h
                if len(lote_h) < 1000:
                    break
                inicio_h += 1000
        except Exception as exc:
            st.error(f'Não foi possível carregar os nomes dos clientes: {exc}')
            st.stop()

        def nome_cliente_baixa(parcela):
            contrato = contratos_baixas.get(str(parcela.get('honorario_id')), {})
            return str(contrato.get('cliente') or 'Cliente não identificado').strip()

        # Todos os contratos aparecem, mesmo quando nenhuma parcela foi paga.
        # O status não pode ser usado para filtrar os clientes nesta etapa.
        parcelas_com_contrato = {pid: par for pid, par in todas_parcelas.items()
                                 if str(par.get('honorario_id')) in contratos_baixas}
        clientes_com_baixas = sorted({nome_cliente_baixa(p) for p in parcelas_com_contrato.values()}, key=str.casefold)
        if not clientes_com_baixas:
            st.info('Nenhum contrato com parcelas foi encontrado. Confira se o cadastro foi salvo em Pagamentos.')
            st.stop()
        cliente_escolhido_baixas = st.selectbox('1. Selecione o cliente', clientes_com_baixas,
                                               key='gerenciar_baixas_cliente')
        parcelas_todas_cliente = {pid: p for pid, p in parcelas_com_contrato.items()
                                  if nome_cliente_baixa(p) == cliente_escolhido_baixas}
        parcelas_cliente_baixas = {pid: p for pid, p in parcelas_todas_cliente.items()
                                  if str(p.get('status') or '').strip().casefold() == 'pago'}
        st.caption(f'{len(parcelas_todas_cliente)} parcela(s) cadastrada(s) para este cliente; '
                   f'{len(parcelas_cliente_baixas)} marcada(s) como pagas.')
        referencia_baixas = st.date_input('Mês de referência para destacar parcelas a receber',
                                          value=date.today().replace(day=1), key='referencia_baixas_status')
        st.subheader('Todas as parcelas do cliente')
        st.caption('Inclui parcelas históricas e parcelas em andamento, pagas ou pendentes. '
                   'Somente parcelas pagas podem ter baixa editada ou cancelada.')
        linhas_visao = []
        for pid, par in sorted(parcelas_todas_cliente.items(),
                               key=lambda item: (str(item[1].get('vencimento') or ''), str(item[1].get('numero_parcela') or ''))):
            contrato = contratos_baixas.get(str(par.get('honorario_id')), {})
            linhas_visao.append({
                'Cliente': nome_cliente_baixa(par),
                'Serviço': contrato.get('servico') or '-',
                'Parcela': str(par.get('numero_parcela') or pid),
                'Vencimento': formatar_data_br(par.get('vencimento')),
                'Valor': formatar_moeda_br(float(par.get('valor') or 0)),
                'Situação': dejure_status_parcela_visual(par.get('status'), par.get('vencimento'), referencia_baixas, 'receber'),
                'ID': pid,
            })
        if linhas_visao:
            st.dataframe(pd.DataFrame(linhas_visao).style.map(dejure_cor_status_visual, subset=['Situação']),
                         use_container_width=True, hide_index=True)
        st.caption('🟢 Recebida: baixa registrada. 🔴 A receber no mês: vencimento na referência selecionada. 🟡 A receber: pendente fora desse mês.')
        if not parcelas_cliente_baixas:
            st.info('Este cliente não tem parcelas pagas para editar ou cancelar. '
                    'As parcelas pendentes estão listadas acima e permanecem no controle de cobrança.')
        opcoes = {}
        for log in eventos_ativos:
            try:
                info = json.loads(log.get('detalhes') or '{}')
                pid = info.get('parcela_id')
                if pid is None or str(pid) not in parcelas_cliente_baixas:
                    continue
                parcela = parcelas_cliente_baixas[str(pid)]
                if str(parcela.get('status', '')).lower() != 'pago':
                    continue
                rotulo = f"{nome_cliente_baixa(parcela)} | Parcela {parcela.get('numero_parcela', pid)} | R$ {float(parcela.get('valor') or 0):,.2f} | Baixa {info.get('data_baixa', '')}"
                opcoes[rotulo] = (log, info, parcela)
            except (ValueError, TypeError, AttributeError):
                continue
        if not opcoes:
            st.info('Este cliente não possui baixas com repasses ativos. Veja abaixo as parcelas pagas sem repasse registrado.')
        else:
            escolha_baixa = st.selectbox('2. Selecione a parcela para editar ou cancelar a baixa', list(opcoes))
            log_baixa, info_baixa, parcela_baixa = opcoes[escolha_baixa]
            pid_baixa = parcela_baixa['id']
            st.write(f"**Contrato:** {info_baixa.get('contrato', '-')}  |  **Parcela:** {pid_baixa}")
            st.write(f"**Valor bruto:** {formatar_moeda_br(float(info_baixa.get('valor_bruto') or 0))}")
            st.write(f"**Leônidas:** {formatar_moeda_br(float(info_baixa.get('leonidas') or 0))}  |  **Nelson:** {formatar_moeda_br(float(info_baixa.get('nelson') or 0))}")
            st.write(f"**Colaborador:** {info_baixa.get('colaborador_parcela') or 'Nenhum'}")
            st.caption('As opções abaixo referem-se a baixas normais. Parcelas históricas são administradas na seção específica ao final desta tela.')
            aba_corrigir, aba_cancelar = st.tabs(['Editar baixa', 'Cancelar baixa'])
            with aba_corrigir:
                if str(info_baixa.get('regra', '')).startswith('Entrada'):
                    st.warning('Baixas de entrada possuem descontos específicos. Para evitar rateios incorretos, a correção automática está disponível somente para parcelas comuns.')
                else:
                    with st.form('form_editar_baixa_master'):
                        data_anterior = str(info_baixa.get('data_baixa') or date.today().isoformat())[:10]
                        try:
                            data_padrao = date.fromisoformat(data_anterior)
                        except ValueError:
                            data_padrao = date.today()
                        nova_data = st.date_input('Data efetiva do recebimento', data_padrao)
                        colab_atual = str(info_baixa.get('colaborador_parcela') or '').strip()
                        # Lista de usuários cadastrados, sem necessidade de digitar o nome.
                        usuarios_colab = sorted({str(dados.get('name') or login).strip()
                            for login, dados in credentials['usernames'].items()
                            if str(dados.get('name') or login).strip()
                            and str(dados.get('role') or '').lower() not in ('inativo', 'bloqueado')}, key=str.casefold)
                        opcoes_colab = ['Nenhum colaborador'] + usuarios_colab
                        if colab_atual and colab_atual not in opcoes_colab:
                            opcoes_colab.append(colab_atual)  # Preserva o beneficiário de registros antigos.
                        selecao_colab = st.selectbox('Colaborador beneficiado', opcoes_colab,
                            index=opcoes_colab.index(colab_atual) if colab_atual in opcoes_colab else 0)
                        novo_colab = '' if selecao_colab == 'Nenhum colaborador' else selecao_colab
                        valor_atual = float(info_baixa.get('valor_colaborador_parcela') or 0)
                        novo_valor = st.number_input('Valor do colaborador (R$)', min_value=0.0, value=valor_atual, step=10.0, format='%.2f')
                        justificativa_ed = st.text_area('Motivo da correção (obrigatório)')
                        confirmar_ed = st.form_submit_button('Salvar correção', type='primary')
                    if confirmar_ed:
                        bruto_c = round(float(info_baixa.get('valor_bruto') or 0), 2)
                        if not justificativa_ed.strip():
                            st.error('Informe o motivo da correção.')
                        elif novo_valor > bruto_c or (novo_valor > 0 and not novo_colab.strip()) or (novo_colab.strip() and novo_valor <= 0):
                            st.error('Informe nome e valor válidos; o valor do colaborador não pode superar a parcela.')
                        else:
                            novo_reg = dict(info_baixa)
                            saldo_c = round(bruto_c - novo_valor, 2)
                            leo_c = round(saldo_c * 0.60, 2)
                            nel_c = round(saldo_c - leo_c, 2)
                            novo_reg.update({'data_baixa': nova_data.isoformat(), 'colaborador_parcela': novo_colab.strip() or None,
                                'valor_colaborador_parcela': round(novo_valor, 2), 'valor_operador': round(novo_valor, 2),
                                'operador': novo_colab.strip() or 'Não aplicável', 'leonidas': leo_c, 'nelson': nel_c,
                                'valor_prospectador': 0.0, 'fundo_colab': 0.0, 'rateio_colaboradores': {},
                                'soma_distribuida': bruto_c, 'prova_real_ok': True,
                                'regra': 'Parcela: repasse livre a colaborador' if novo_valor else 'Parcela: sócios',
                                'revisao_log_id': log_baixa['id'], 'motivo_correcao': justificativa_ed.strip()})
                            try:
                                dejure_registrar_evento_repasse(cliente_fin, username, 'Correção de Baixa', novo_reg)
                                st.cache_data.clear()
                                st.success('Baixa corrigida. Extratos e Balanço consideram apenas a versão atual.')
                                st.rerun()
                            except Exception as exc:
                                st.error(f'Não foi possível salvar a correção: {exc}')
            with aba_cancelar:
                st.warning('O cancelamento devolve a parcela a Pendente e retira seu repasse dos relatórios. O histórico da baixa permanece na auditoria.')
                with st.form('form_cancelar_baixa_master'):
                    motivo_cancel = st.text_area('Justificativa do cancelamento (obrigatória)')
                    confirmar_texto = st.text_input('Digite CANCELAR para confirmar')
                    confirmar_cancel = st.form_submit_button('Cancelar baixa', type='primary')
                if confirmar_cancel:
                    if not motivo_cancel.strip() or confirmar_texto.strip() != 'CANCELAR':
                        st.error('Informe a justificativa e digite CANCELAR.')
                    else:
                        try:
                            # Registrar evento antes da alteração do status, preservando trilha financeira.
                            evento_cancel = {'parcela_id': pid_baixa, 'log_anterior_id': log_baixa['id'],
                                'data_baixa': date.today().isoformat(), 'motivo_cancelamento': motivo_cancel.strip(),
                                'valor_bruto_anterior': info_baixa.get('valor_bruto'),
                                'leonidas_anterior': info_baixa.get('leonidas'), 'nelson_anterior': info_baixa.get('nelson')}
                            dejure_registrar_evento_repasse(cliente_fin, username, 'Cancelamento de Baixa', evento_cancel)
                            cliente_fin.table('parcelas').update({'status': 'Pendente'}).eq('id', pid_baixa).execute()
                            st.cache_data.clear()
                            st.success('Baixa cancelada. A parcela voltou a Pendente.')
                            st.rerun()
                        except Exception as exc:
                            st.error(f'Falha ao cancelar: {exc}. Confira o status e a auditoria antes de tentar novamente.')

        st.divider()
        st.subheader('Regularizar parcela paga sem baixa financeira')
        st.caption('Para parcelas importadas como pagas ou marcadas indevidamente como pagas, sem repasse financeiro ativo. A correção não gera nem cancela repasses.')
        ids_com_repasse = {str(par['id']) for _, _, par in opcoes.values()}
        sem_repasse_cliente = {pid: par for pid, par in parcelas_cliente_baixas.items()
                              if pid not in ids_com_repasse}
        if sem_repasse_cliente:
            rotulos_sem = {
                f"{nome_cliente_baixa(par)} | Parcela {par.get('numero_parcela', pid)} | "
                f"{formatar_moeda_br(float(par.get('valor') or 0))} | Vencimento {formatar_data_br(par.get('vencimento'))}": pid
                for pid, par in sem_repasse_cliente.items()
            }
            selecao_sem = st.selectbox('Parcela paga sem repasse', list(rotulos_sem), key='regularizar_sem_repasse')
            pid_sem = rotulos_sem[selecao_sem]
            with st.form('form_regularizar_status_sem_repasse'):
                st.warning('Use apenas se confirmar que a parcela NÃO foi recebida. Parcelas históricas efetivamente pagas devem permanecer como Pagas.')
                motivo_sem = st.text_area('Justificativa da correção (obrigatória)', key='motivo_sem_repasse')
                confirma_sem = st.checkbox('Confirmo que esta parcela ainda não foi recebida', key='confirma_sem_repasse')
                salvar_sem = st.form_submit_button('Corrigir status para Pendente', type='primary')
            if salvar_sem:
                if not confirma_sem or not motivo_sem.strip():
                    st.error('Confirme que não houve recebimento e informe a justificativa.')
                else:
                    try:
                        # Verificação final evita reverter parcela com repasse ativo em outra tela.
                        repasses_atuais = dejure_logs_repasses_ativos(cliente_fin)
                        possui_repasse = any(str(json.loads(l.get('detalhes') or '{}').get('parcela_id')) == str(pid_sem)
                                              for l in repasses_atuais)
                        if possui_repasse:
                            st.error('Esta parcela possui repasse ativo. Utilize a opção Cancelar baixa acima.')
                        else:
                            cliente_fin.table('parcelas').update({'status': 'Pendente'}).eq('id', pid_sem).execute()
                            registrar_auditoria(username, 'Regularizar status de parcela', 'Pagamentos',
                                                json.dumps({'parcela_id': pid_sem, 'cliente': cliente_escolhido_baixas,
                                                            'status_anterior': 'Pago', 'status_novo': 'Pendente',
                                                            'motivo': motivo_sem.strip()}, ensure_ascii=False))
                            st.cache_data.clear()
                            st.success('Parcela corrigida para Pendente, sem alterar repasses.')
                            st.rerun()
                    except Exception as exc:
                        st.error(f'Falha ao corrigir parcela: {exc}')
        else:
            st.info('Nenhuma parcela paga sem repasse para este cliente.')

        st.divider()
        st.subheader('Parcelas históricas — inclusão no Balanço')
        st.caption('Selecione uma parcela recebida anteriormente e marque ou desmarque sua inclusão contábil. Não gera novo repasse nem altera o status Pago.')
        try:
            historicos_estado = dejure_historicos_balanco(cliente_fin)
            logs_importacao = []
            pag_inicio = 0
            while True:
                lote = (cliente_fin.table('logs_auditoria').select('detalhes').eq('modulo', 'Pagamentos')
                        .eq('acao', 'Importar Parcelamento Histórico (sem repasses)')
                        .range(pag_inicio, pag_inicio + 999).execute().data or [])
                logs_importacao.extend(lote)
                if len(lote) < 1000:
                    break
                pag_inicio += 1000
            ids_honorarios = set()
            for log in logs_importacao:
                try:
                    inf = json.loads(log.get('detalhes') or '{}')
                    if inf.get('tipo') == 'parcelamento_historico_sem_repasses':
                        ids_honorarios.add(str(inf.get('honorario_id')))
                except (ValueError, TypeError, AttributeError):
                    continue
            # O cadastro registra os IDs das parcelas, evitando confusão com baixas normais.
            ids_historicos = {str(pid) for pid, d in historicos_estado.items() if d.get('data_recebimento')}
            for pid, par in todas_parcelas.items():
                if str(par.get('honorario_id')) in ids_honorarios and str(par.get('status', '')).lower() == 'pago':
                    ids_historicos.add(pid)
            lista_hist = {pid: todas_parcelas[pid] for pid in ids_historicos if pid in parcelas_cliente_baixas and str(todas_parcelas[pid].get('status', '')).lower() == 'pago'}
            if lista_hist:
                labels_hist = {f"{nome_cliente_baixa(par)} | Parcela {par.get('numero_parcela')} | {formatar_moeda_br(float(par.get('valor') or 0))}": pid for pid, par in sorted(lista_hist.items(), key=lambda kv: str(kv[0]))}
                escolha_hist = st.selectbox('Parcela histórica', list(labels_hist), key='baixa_historico_selecao')
                id_hist = labels_hist[escolha_hist]
                par_hist = lista_hist[id_hist]
                estado_hist = historicos_estado.get(id_hist, {})
                with st.form('form_editar_inclusao_historica'):
                    marcar_hist = st.checkbox('Incluir esta parcela histórica no Balanço Financeiro', value=bool(estado_hist.get('incluir_balanco', False)))
                    try:
                        data_hist_padrao = date.fromisoformat(str(estado_hist.get('data_recebimento') or '')[:10])
                    except ValueError:
                        data_hist_padrao = date.today()
                    data_hist_ed = st.date_input('Data real do recebimento pelo escritório', value=data_hist_padrao)
                    comp_hist_atual = str(estado_hist.get('competencia_balanco') or data_hist_padrao.strftime('%Y-%m'))
                    try:
                        comp_hist_data = date.fromisoformat(comp_hist_atual[:7] + '-01')
                    except ValueError:
                        comp_hist_data = data_hist_padrao.replace(day=1)
                    competencia_hist_ed = st.date_input('Mês de competência no balanço (escolha qualquer dia do mês)', value=comp_hist_data, key='competencia_edicao_hist')
                    st.caption('O mês escolhido define a prestação de contas, independentemente da data do pagamento do cliente.')
                    motivo_hist_ed = st.text_input('Justificativa da alteração (obrigatória)')
                    salvar_hist_ed = st.form_submit_button('Salvar escolha', type='primary')
                if salvar_hist_ed:
                    if not motivo_hist_ed.strip():
                        st.error('Informe a justificativa.')
                    elif data_hist_ed > date.today():
                        st.error('A data do recebimento não pode ser futura.')
                    else:
                        try:
                            dejure_salvar_historico_balanco(cliente_fin, username, par_hist['id'], marcar_hist,
                                par_hist.get('valor') or 0, data_hist_ed.isoformat(), motivo_hist_ed.strip(), competencia_hist_ed.strftime('%Y-%m'))
                            st.cache_data.clear()
                            st.success('Escolha atualizada no Balanço, sem gerar repasse.')
                            st.rerun()
                        except Exception as e:
                            st.error(f'Erro ao salvar: {e}')
            else:
                st.info('Nenhuma parcela histórica paga encontrada.')
        except Exception as e:
            st.error(f'Não foi possível consultar parcelas históricas: {e}')

    elif menu_escolha == "Gerenciar Protocolos":
        st.title("Gerenciamento de Protocolos")
        if username != "master" or user_role != "admin" or st.session_state.get("authentication_status") is not True:
            st.error("Acesso exclusivo do usuário Master.")
            st.stop()
        st.caption("Corrija ou exclua registros de protocolo. A exclusão retira o ponto da Visão Geral e do ranking; não exclui o processo nem seus documentos.")
        try:
            cliente_prot = cliente_storage_servidor()
            eventos_prot = []
            for inicio_prot in range(0, 20000, 1000):
                lote_prot = (cliente_prot.table("dejure_protocolos").select("*")
                              .order("protocolado_em", desc=True)
                              .range(inicio_prot, inicio_prot + 999).execute()).data or []
                eventos_prot.extend(lote_prot)
                if len(lote_prot) < 1000:
                    break
            if not eventos_prot:
                st.info("Nenhum protocolo registrado.")
            else:
                pesquisa_prot = st.text_input("Pesquisar por processo ou protocolante", key="master_busca_protocolo")
                filtrados_prot = [e for e in eventos_prot if pesquisa_prot.casefold() in
                                  (str(e.get("processo_id", "")) + " " + str(e.get("protocolado_por", ""))).casefold()]
                st.dataframe([{"Processo ID": e.get("processo_id"), "Protocolante": e.get("protocolado_por"),
                               "Data": e.get("protocolado_em")} for e in filtrados_prot],
                             use_container_width=True, hide_index=True)
                if filtrados_prot:
                    escolhas_prot = {f"Processo {e.get('processo_id')} | {e.get('protocolado_por', 'N/D')} | {e.get('protocolado_em', '')}": e
                                     for e in filtrados_prot}
                    chave_prot = st.selectbox("Selecione o protocolo", list(escolhas_prot), key="master_protocolo_selecionado")
                    evento_prot = escolhas_prot[chave_prot]
                    id_processo_prot = evento_prot.get("processo_id")
                    with st.form("master_editar_protocolo"):
                        nomes_prot = sorted({str(v.get("name") or login) for login, v in credentials["usernames"].items()
                                             if login != "master" and v.get("role") not in ("inativo", "bloqueado")})
                        atual_prot = str(evento_prot.get("protocolado_por") or "")
                        if atual_prot not in nomes_prot:
                            nomes_prot.insert(0, atual_prot)
                        nome_novo_prot = st.selectbox("Protocolante", nomes_prot, index=nomes_prot.index(atual_prot))
                        try:
                            data_original_prot = date.fromisoformat(str(evento_prot.get("protocolado_em"))[:10])
                        except (ValueError, TypeError):
                            data_original_prot = date.today()
                        data_nova_prot = st.date_input("Data do protocolo", value=data_original_prot)
                        motivo_prot = st.text_area("Motivo da correção (obrigatório)")
                        salvar_prot = st.form_submit_button("Salvar correção", type="primary")
                        if salvar_prot:
                            if not motivo_prot.strip():
                                st.error("Informe o motivo da correção.")
                            else:
                                try:
                                    anterior_prot = dict(evento_prot)
                                    data_antiga = str(evento_prot.get("protocolado_em") or "")
                                    sufixo_hora = data_antiga[10:] if len(data_antiga) > 10 else "T12:00:00+00:00"
                                    novos_prot = {"protocolado_por": nome_novo_prot,
                                                  "protocolado_em": data_nova_prot.isoformat() + sufixo_hora}
                                    cliente_prot.table("dejure_protocolos").update(novos_prot).eq("processo_id", id_processo_prot).execute()
                                    registrar_auditoria(username, "Corrigir protocolo", "Gerenciar Protocolos",
                                        f"Processo {id_processo_prot}; antes={anterior_prot}; depois={novos_prot}; motivo={motivo_prot.strip()}")
                                    st.cache_data.clear()
                                    st.success("Protocolo corrigido. O ranking será recalculado na Página Inicial.")
                                    st.rerun()
                                except Exception as erro_prot:
                                    st.error(f"Erro ao corrigir protocolo: {erro_prot}")
                    st.divider()
                    st.subheader("Excluir registro de protocolo")
                    st.warning("Esta ação remove o registro de pontuação. O processo permanece cadastrado.")
                    motivo_exclusao_prot = st.text_input("Justificativa da exclusão", key="master_motivo_exclusao_prot")
                    confirmar_exclusao_prot = st.checkbox("Confirmo a exclusão deste protocolo e a retirada do ponto do ranking.",
                                                         key="master_confirma_exclusao_prot")
                    if st.button("Excluir protocolo", type="primary", disabled=not confirmar_exclusao_prot,
                                 key="master_excluir_protocolo"):
                        if not motivo_exclusao_prot.strip():
                            st.error("Informe a justificativa da exclusão.")
                        else:
                            try:
                                # Exclui apenas o evento, não o processo nem seus documentos.
                                cliente_prot.table("dejure_protocolos").delete().eq("processo_id", id_processo_prot).execute()
                                # Um processo sem protocolo não deve continuar marcado como protocolado.
                                cliente_prot.table("meus_processos").update({"status": "Peça Aprovada"}).eq(
                                    "id", id_processo_prot).eq("status", "Protocolado").execute()
                                registrar_auditoria(username, "Excluir protocolo", "Gerenciar Protocolos",
                                    f"Processo {id_processo_prot}; registro={evento_prot}; motivo={motivo_exclusao_prot.strip()}")
                                st.cache_data.clear()
                                st.success("Registro excluído. O ponto não será mais contabilizado na Visão Geral.")
                                st.rerun()
                            except Exception as erro_prot:
                                st.error(f"Falha ao excluir: {erro_prot}. Confira o registro antes de tentar novamente.")
        except Exception as erro_prot:
            st.error(f"Não foi possível consultar os protocolos: {erro_prot}")

    elif menu_escolha == "Balanço Financeiro":
        # Proteção no servidor, além de ocultar o item do menu.
        if user_role != 'admin':
            st.error('Acesso exclusivo aos administradores.')
            st.stop()

        st.title('Balanço Financeiro DEJURE')
        st.caption('Os valores dos sócios são calculados conforme as regras financeiras do escritório.')
        from collections import defaultdict
        from decimal import Decimal, ROUND_HALF_UP

        def centavos(valor):
            try:
                return int((Decimal(str(valor or 0)) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            except Exception:
                return 0

        def moeda_c(valor):
            return formatar_moeda_br(valor / 100)

        def data_segura(valor):
            try:
                return date.fromisoformat(str(valor)[:10])
            except (ValueError, TypeError):
                return None

        def consulta_toda(tabela, colunas='*', filtros=None):
            registros = []
            inicio = 0
            while True:
                q = cliente_storage_servidor().table(tabela).select(colunas)
                for campo, valor in (filtros or []):
                    q = q.eq(campo, valor)
                lote = q.range(inicio, inicio + 999).execute().data or []
                registros.extend(lote)
                if len(lote) < 1000:
                    break
                inicio += 1000
            return registros

        def add_meses(data, meses):
            return data + relativedelta(months=meses)

        def registrar_despesa(dados):
            return cliente_storage_servidor().table('dejure_despesas').insert(dados).execute()

        def materializar_programacoes(programacoes, despesas_existentes):
            # Lançamentos persistidos por competência: não há duplicidade, mesmo em acessos simultâneos.
            existentes = {(str(d.get('programacao_id')), str(d.get('competencia'))[:7])
                          for d in despesas_existentes if d.get('programacao_id') is not None}
            limite = add_meses(date.today().replace(day=1), 24)
            for prog in programacoes:
                if not prog.get('ativo', True):
                    continue
                inicio = data_segura(prog.get('inicio'))
                if not inicio:
                    continue
                inicio = inicio.replace(day=1)
                quantidade = int(prog.get('quantidade') or 0)
                # Parceladas: quantidade definida. Fixas: até 24 meses à frente, sem data final.
                ultimo = add_meses(inicio, quantidade - 1) if quantidade else limite
                ultimo = min(ultimo, limite)
                cursor = inicio
                indice = 0
                while cursor <= ultimo:
                    indice += 1
                    chave = (str(prog['id']), cursor.strftime('%Y-%m'))
                    if chave not in existentes:
                        dia = min(int(prog.get('dia_vencimento') or 1), __import__('calendar').monthrange(cursor.year, cursor.month)[1])
                        venc = cursor.replace(day=dia)
                        valor_lanc = Decimal(str(prog['valor']))
                        if quantidade and indice == quantidade:
                            valor_lanc = Decimal(str(prog.get('valor_ultima') or prog['valor']))
                        registro = {
                            'tipo': prog['tipo'], 'descricao': prog['descricao'],
                            'valor': str(valor_lanc), 'competencia': cursor.isoformat(),
                            'vencimento': venc.isoformat(), 'situacao': 'Pendente',
                            'pago_em': None, 'observacoes': prog.get('observacoes') or '',
                            'criado_por': prog.get('criado_por') or 'Sistema',
                            'programacao_id': prog['id'], 'numero_parcela_despesa': indice
                        }
                        # UNIQUE (programacao_id, competencia) previne duplicações.
                        cliente_storage_servidor().table('dejure_despesas').upsert(
                            registro, on_conflict='programacao_id,competencia', ignore_duplicates=True).execute()
                        existentes.add(chave)
                    cursor = add_meses(cursor, 1)

        try:
            programacoes = consulta_toda('dejure_despesas_programacoes')
            despesas = consulta_toda('dejure_despesas')
            materializar_programacoes(programacoes, despesas)
            despesas = consulta_toda('dejure_despesas')
            repasses_logs = dejure_logs_repasses_ativos(cliente_storage_servidor())
            parcelas = consulta_toda('parcelas')
            historicos_balanco = dejure_historicos_balanco(cliente_storage_servidor())
        except Exception as erro_bal:
            st.error('Não foi possível carregar o balanço. Execute o SQL de atualização das despesas no Supabase.')
            st.exception(erro_bal)
            st.stop()

        abas = st.tabs(['Painel por sócio', 'Cadastrar despesas', 'Gerenciar despesas', 'Projeção de parcelas', 'Despesas programadas', 'Prestação de contas'])
        hoje_fin = date.today()
        with abas[1]:
            st.subheader('Cadastrar despesas')
            st.caption('Despesas fixas são repetidas mensalmente até o ADM encerrar. Parceladas geram vencimentos mensais independentes.')
            # Seletores fora do formulário: Streamlit atualiza os campos
            # imediatamente ao escolher Parcelada, sem precisar clicar em Salvar.
            tipo = st.selectbox('Tipo de despesa', ['Fixa', 'Variável', 'Outras'], key='dj_despesa_tipo')
            forma = st.selectbox(
                'Forma de lançamento', ['Única', 'Parcelada', 'Mensal recorrente'],
                key='dj_despesa_forma',
                help='Parcelada: informe o total e a quantidade. Mensal recorrente: repete até o ADM encerrar.'
            )
            with st.form('form_despesa_dejure', clear_on_submit=True):
                descricao = st.text_input('Descrição', max_chars=180)
                valor = st.number_input('Valor (R$)', min_value=0.01, step=10.0, format='%.2f')
                competencia = st.date_input('Primeiro mês de competência', hoje_fin.replace(day=1))
                vencimento = st.date_input('Primeiro vencimento', hoje_fin)
                if forma == 'Parcelada':
                    quantidade = st.number_input('Quantidade de parcelas', min_value=2, max_value=120, value=2, step=1)
                    st.caption('O valor informado é o TOTAL da compra; o sistema divide entre as parcelas.')
                else:
                    quantidade = 1
                situacao = st.selectbox('Situação inicial', ['Pendente', 'Paga']) if forma == 'Única' else 'Pendente'
                observacoes = st.text_area('Observações (opcional)')
                salvar = st.form_submit_button('Cadastrar despesa', type='primary')
            if salvar:
                if not descricao.strip():
                    st.error('Informe a descrição da despesa.')
                elif vencimento.year != competencia.year or vencimento.month != competencia.month:
                    st.error('O primeiro vencimento deve pertencer ao mês da primeira competência.')
                else:
                    try:
                        if forma == 'Única':
                            registrar_despesa({
                                'tipo': tipo, 'descricao': descricao.strip(),
                                'valor': str(Decimal(str(valor)).quantize(Decimal('0.01'))),
                                'competencia': competencia.replace(day=1).isoformat(),
                                'vencimento': vencimento.isoformat(), 'situacao': situacao,
                                'observacoes': observacoes.strip(), 'criado_por': str(username),
                                'pago_em': hoje_fin.isoformat() if situacao == 'Paga' else None
                            })
                        else:
                            total_c = centavos(valor)
                            qtd = int(quantidade) if forma == 'Parcelada' else 0
                            por_parcela = total_c // qtd if qtd else total_c
                            ultima = total_c - por_parcela * (qtd - 1) if qtd else total_c
                            dados_prog = {
                                'tipo': tipo, 'descricao': descricao.strip(),
                                'valor': str(Decimal(por_parcela) / 100),
                                'valor_ultima': str(Decimal(ultima) / 100),
                                'inicio': competencia.replace(day=1).isoformat(),
                                'dia_vencimento': vencimento.day, 'quantidade': qtd,
                                'ativo': True, 'observacoes': observacoes.strip(), 'criado_por': str(username)
                            }
                            criado = cliente_storage_servidor().table('dejure_despesas_programacoes').insert(dados_prog).execute().data or []
                            if criado:
                                materializar_programacoes(criado, despesas)
                        registrar_auditoria(username, 'Cadastrar despesa', 'Balanço Financeiro', f'{descricao.strip()} - {forma}')
                        st.success('Despesa cadastrada com sucesso.')
                        st.rerun()
                    except Exception as e:
                        st.error(f'Falha ao cadastrar despesa: {e}')

        with abas[2]:
            st.subheader('Lançamentos de despesas')
            if despesas:
                # Primeiro selecione a despesa (programação), depois apenas uma de suas parcelas.
                # Despesas avulsas são identificadas pelo ID do próprio lançamento.
                grupos_d = {}
                for d in despesas:
                    pid = d.get('programacao_id')
                    chave = ('programacao', str(pid)) if pid is not None else ('avulsa', str(d['id']))
                    grupos_d.setdefault(chave, []).append(d)
                opcoes_grupos = {}
                for chave, itens in grupos_d.items():
                    primeiro = itens[0]
                    descricao_grupo = next((str(p.get('descricao') or '') for p in programacoes
                                             if chave[0] == 'programacao' and str(p.get('id')) == chave[1]),
                                            str(primeiro.get('descricao') or 'Sem descrição'))
                    rotulo = f"{descricao_grupo} | {'Parcelada / Recorrente' if chave[0] == 'programacao' else 'Única'} | Ref. {chave[1]}"
                    opcoes_grupos[rotulo] = chave
                escolha_grupo = st.selectbox('1. Selecione a despesa que deseja gerenciar',
                                            sorted(opcoes_grupos, key=str.casefold), key='bal_grupo_despesa')
                chave_escolhida = opcoes_grupos[escolha_grupo]
                despesas_filtradas = sorted(grupos_d[chave_escolhida],
                                           key=lambda d: (str(d.get('competencia') or ''), str(d.get('vencimento') or ''), str(d['id'])))
                st.caption(f'{len(despesas_filtradas)} lançamento(s) desta despesa. Nenhuma outra despesa está incluída nesta lista.')
                linhas_d = [{
                    'ID': d['id'], 'Tipo': d.get('tipo'), 'Descrição': d.get('descricao'),
                    'Valor': moeda_c(centavos(d.get('valor'))), 'Competência': str(d.get('competencia') or '')[:7],
                    'Vencimento': formatar_data_br(d.get('vencimento')),
                    'Situação': dejure_status_parcela_visual(d.get('situacao'), d.get('vencimento'), hoje_fin, 'pagar'),
                    'Parcela': d.get('numero_parcela_despesa') or '—'
                } for d in despesas_filtradas]
                st.dataframe(pd.DataFrame(linhas_d).style.map(dejure_cor_status_visual, subset=['Situação']), hide_index=True, use_container_width=True)
                opcoes_d = {f"#{d['id']} | Parcela {d.get('numero_parcela_despesa') or 'única'} | {str(d.get('competencia') or '')[:7]} | {moeda_c(centavos(d.get('valor')))}": d for d in despesas_filtradas}
                escolha_d = st.selectbox('2. Selecione a parcela / lançamento para editar',
                                         list(opcoes_d), key='bal_despesa_edicao')
                alvo = opcoes_d[escolha_d]
                st.info('As alterações abaixo afetam somente o lançamento selecionado, não as demais parcelas.')
                with st.form('bal_editar_despesa'):
                    novo_tipo = st.selectbox('Categoria', ['Fixa', 'Variável', 'Outras'], index=['Fixa','Variável','Outras'].index(alvo.get('tipo')) if alvo.get('tipo') in ['Fixa','Variável','Outras'] else 2)
                    nova_desc = st.text_input('Descrição', value=str(alvo.get('descricao') or ''))
                    novo_valor = st.number_input('Valor (R$)', min_value=0.01, value=max(0.01, centavos(alvo.get('valor')) / 100), format='%.2f')
                    nova_comp = st.date_input('Competência', value=data_segura(alvo.get('competencia')) or hoje_fin)
                    novo_venc = st.date_input('Vencimento', value=data_segura(alvo.get('vencimento')) or hoje_fin)
                    nova_sit = st.selectbox('Situação', ['Pendente','Paga'], index=1 if alvo.get('situacao') == 'Paga' else 0)
                    nova_obs = st.text_area('Observações', value=str(alvo.get('observacoes') or ''))
                    atualizar = st.form_submit_button('Salvar alterações')
                if atualizar:
                    if not nova_desc.strip():
                        st.error('Descrição obrigatória.')
                    else:
                        try:
                            cliente_storage_servidor().table('dejure_despesas').update({
                                'tipo': novo_tipo, 'descricao': nova_desc.strip(),
                                'valor': str(Decimal(str(novo_valor)).quantize(Decimal('0.01'))),
                                'competencia': nova_comp.replace(day=1).isoformat(), 'vencimento': novo_venc.isoformat(),
                                'situacao': nova_sit, 'observacoes': nova_obs.strip(),
                                'pago_em': (alvo.get('pago_em') or hoje_fin.isoformat()) if nova_sit == 'Paga' else None
                            }).eq('id', alvo['id']).execute()
                            registrar_auditoria(username, 'Atualizar despesa', 'Balanço Financeiro', f"ID {alvo['id']}")
                            st.success('Lançamento atualizado.')
                            st.rerun()
                        except Exception as e:
                            st.error(f'Falha ao atualizar: {e}')
                with st.expander('Excluir lançamento individual'):
                    st.warning('Para encerrar despesas fixas, use a aba Despesas programadas. A exclusão de um lançamento não encerra a recorrência.')
                    confirmar = st.checkbox('Confirmo a exclusão do lançamento selecionado', key='bal_confirma_exclusao')
                    if st.button('Excluir lançamento', disabled=not confirmar):
                        try:
                            if alvo.get('programacao_id'):
                                st.error('Lançamentos programados não podem ser excluídos individualmente; altere a situação ou encerre a programação.')
                            else:
                                cliente_storage_servidor().table('dejure_despesas').delete().eq('id', alvo['id']).execute()
                                registrar_auditoria(username, 'Excluir despesa', 'Balanço Financeiro', f"ID {alvo['id']} - {alvo.get('descricao')}")
                                st.success('Lançamento excluído.')
                                st.rerun()
                        except Exception as e:
                            st.error(f'Falha ao excluir: {e}')
            else:
                st.info('Nenhuma despesa cadastrada.')

        with abas[4]:
            st.subheader('Despesas fixas e parceladas programadas')
            if programacoes:
                st.dataframe(pd.DataFrame([{
                    'ID': p['id'], 'Descrição': p['descricao'], 'Tipo': p['tipo'],
                    'Valor mensal': moeda_c(centavos(p['valor'])),
                    'Início': str(p['inicio'])[:7],
                    'Parcelas': p.get('quantidade') or 'Recorrente',
                    'Situação': 'Ativa' if p.get('ativo', True) else 'Encerrada'
                } for p in programacoes]), hide_index=True, use_container_width=True)
                opcoes_prog = {f"#{p['id']} | {p['descricao']}": p for p in programacoes}
                escolha_prog = st.selectbox('Selecionar programação', list(opcoes_prog))
                prog = opcoes_prog[escolha_prog]
                st.caption('Ao encerrar, os lançamentos pendentes do mês atual em diante serão removidos. Os pagos e os meses anteriores ficam preservados.')
                confirma_prog = st.checkbox('Confirmo o encerramento desta programação')
                if st.button('Encerrar despesa fixa / programação', disabled=not confirma_prog or not prog.get('ativo', True)):
                    try:
                        cliente_storage_servidor().table('dejure_despesas_programacoes').update({'ativo': False}).eq('id', prog['id']).execute()
                        # Preserve históricos; remova apenas futuras cobranças ainda não pagas.
                        cliente_storage_servidor().table('dejure_despesas').delete().eq('programacao_id', prog['id']).eq('situacao', 'Pendente').gte('competencia', hoje_fin.replace(day=1).isoformat()).execute()
                        registrar_auditoria(username, 'Encerrar despesa programada', 'Balanço Financeiro', f"ID {prog['id']} - {prog['descricao']}")
                        st.success('Programação encerrada; histórico preservado.')
                        st.rerun()
                    except Exception as e:
                        st.error(f'Falha ao encerrar programação: {e}')
            else:
                st.info('Nenhuma despesa recorrente ou parcelada cadastrada.')

        repasses = []
        vistos = set()
        for log in sorted(repasses_logs, key=lambda x: str(x.get('data_hora') or '')):
            try:
                r = json.loads(log.get('detalhes') or '{}')
                pid = r.get('parcela_id')
                # Evita duplicação de um mesmo pagamento no histórico de auditoria.
                if pid is not None and str(pid) in vistos:
                    continue
                if pid is not None:
                    vistos.add(str(pid))
                dt = data_segura(r.get('data_baixa')) or data_segura(log.get('data_hora'))
                if dt:
                    repasses.append({'data': dt, 'leonidas': centavos(r.get('leonidas')),
                                     'nelson': centavos(r.get('nelson')), 'contrato': r.get('contrato','')})
            except (ValueError, TypeError, AttributeError):
                continue

        # Recebimentos históricos são lançamentos contábeis opcionais, NÃO repasses.
        historicos_incluidos = []
        for p in parcelas:
            h = historicos_balanco.get(str(p.get('id')), {})
            if not h.get('incluir_balanco') or str(p.get('status', '')).lower() != 'pago':
                continue
            dt = data_segura(str(h.get('competencia_balanco') or str(h.get('data_recebimento') or '')[:7])[:7] + '-01')
            if dt:
                valor_c = centavos(p.get('valor'))
                leo_c = (valor_c * 60 + 50) // 100
                historicos_incluidos.append({'data': dt, 'leonidas': leo_c,
                    'nelson': valor_c - leo_c, 'parcela_id': p.get('id')})

        # Competência e prestação de contas são datas distintas. Recebimentos de outubro
        # pertencem ao balanço de outubro, ainda que os sócios fechem em novembro.
        def janela_prestacao(mes):
            proximo = mes.replace(day=1) + relativedelta(months=1)
            return proximo.replace(day=1), proximo.replace(day=5)

        with abas[0]:
            # A prestação de contas dos dias 1 a 5 refere-se ao mês anterior.
            # O painel NUNCA soma competências anteriores à escolhida.
            competencia_padrao = hoje_fin.replace(day=1) - relativedelta(months=1)
            mes_ref = st.date_input('Mês de competência da prestação de contas',
                                    value=competencia_padrao, key='bal_mes_ref')
            inicio = mes_ref.replace(day=1)
            fim = inicio + relativedelta(months=1)
            prest_inicio, prest_fim = janela_prestacao(inicio)
            st.info(f'Prestação de contas: {prest_inicio:%d/%m/%Y} a {prest_fim:%d/%m/%Y} '
                    f'| Movimentações consideradas: somente {inicio:%m/%Y}. '
                    'Receitas e despesas de outras competências não entram neste demonstrativo.')
            def no_periodo(dt):
                return inicio <= dt < fim
            rep = [r for r in repasses if no_periodo(r['data'])]
            desp = [d for d in despesas if (data_segura(d.get('competencia')) is not None and no_periodo(data_segura(d.get('competencia'))))]
            # Competência é a referência contábil; apenas despesas pagas afetam o saldo realizado.
            hist_periodo = [h for h in historicos_incluidos if no_periodo(h['data'])]
            total_leo = sum(r['leonidas'] for r in rep) + sum(h['leonidas'] for h in hist_periodo)
            total_nel = sum(r['nelson'] for r in rep) + sum(h['nelson'] for h in hist_periodo)
            despesas_pagas = sum(centavos(d.get('valor')) for d in desp if d.get('situacao') == 'Paga')
            despesas_pendentes = sum(centavos(d.get('valor')) for d in desp if d.get('situacao') != 'Paga')
            # Centavos ímpares são atribuídos a Leônidas para manter a soma exata.
            metade_nel = despesas_pagas // 2
            metade_leo = despesas_pagas - metade_nel
            l1,l2,l3,l4 = st.columns(4)
            st.caption('Recebimentos históricos incluídos neste período: ' + moeda_c(sum(h['leonidas'] + h['nelson'] for h in hist_periodo)) + '. São registros contábeis, não novos repasses aos sócios.')
            l1.metric('Honorários dos sócios', moeda_c(total_leo + total_nel))
            l2.metric('Despesas pagas', moeda_c(despesas_pagas))
            l3.metric('Despesas pendentes', moeda_c(despesas_pendentes))
            l4.metric('Resultado realizado', moeda_c(total_leo + total_nel - despesas_pagas))
            st.subheader('Painel individual de receitas, despesas e saldo')
            df_s = pd.DataFrame([
                {'Sócio': 'Leônidas', 'Honorários recebidos': moeda_c(total_leo), 'Despesas (50%)': moeda_c(metade_leo), 'Saldo realizado': moeda_c(total_leo - metade_leo)},
                {'Sócio': 'Nelson', 'Honorários recebidos': moeda_c(total_nel), 'Despesas (50%)': moeda_c(metade_nel), 'Saldo realizado': moeda_c(total_nel - metade_nel)}
            ])
            for nome, receita, despesa_s in [('Leônidas', total_leo, metade_leo), ('Nelson', total_nel, metade_nel)]:
                st.markdown(f'#### {nome}')
                p1, p2, p3 = st.columns(3)
                p1.metric('Receitas', moeda_c(receita))
                p2.metric('Despesas pagas', moeda_c(despesa_s))
                p3.metric('Saldo', moeda_c(receita - despesa_s))
            st.dataframe(df_s, hide_index=True, use_container_width=True)
            st.caption('Saldo realizado = repasses registrados menos metade das despesas marcadas como pagas. Despesas pendentes são mostradas separadamente.')
            st.subheader(f'Despesas desta prestação de contas — {inicio:%m/%Y}')
            st.caption(f'Somente despesas da competência {inicio:%m/%Y}. Consulta individual por sócio; despesas pendentes não reduzem o saldo realizado.')
            if desp:
                linhas_conferencia = []
                for d in sorted(desp, key=lambda item: (str(item.get('competencia') or ''), str(item.get('vencimento') or ''), str(item.get('id') or ''))):
                    total_c = centavos(d.get('valor'))
                    parte_n = total_c // 2
                    parte_l = total_c - parte_n
                    pago = str(d.get('situacao') or '').strip().casefold() == 'paga'
                    vencimento_item = data_segura(d.get('vencimento'))
                    # Pago prevalece; vermelho indica parcela ainda não paga
                    # com vencimento dentro da competência em prestação de contas.
                    status_visual = ('🟢 Paga' if pago else
                                     '🔴 A pagar no mês' if vencimento_item and inicio <= vencimento_item < fim else
                                     '🟡 A pagar')
                    linhas_conferencia.append({
                        'ID': d.get('id'),
                        'Descrição': d.get('descricao') or '',
                        'Categoria': d.get('tipo') or '',
                        'Competência': str(d.get('competencia') or '')[:7],
                        'Vencimento': formatar_data_br(d.get('vencimento')),
                        'Parcela': d.get('numero_parcela_despesa') or '—',
                        'Situação': status_visual,
                        'Valor total': moeda_c(total_c),
                        'Leônidas': moeda_c(parte_l),
                        'Nelson': moeda_c(parte_n),
                        'Afeta saldo realizado': 'Sim' if pago else 'Não',
                    })
                def cor_status_prestacao(valor):
                    texto = str(valor)
                    if texto.startswith('🟢'):
                        return 'background-color: #123d2b; color: #9ff3c1; font-weight: bold;'
                    if texto.startswith('🔴'):
                        return 'background-color: #552025; color: #ffb1b1; font-weight: bold;'
                    if texto.startswith('🟡'):
                        return 'background-color: #493d16; color: #ffe18a; font-weight: bold;'
                    return ''
                tabela_conferencia = pd.DataFrame(linhas_conferencia)
                st.dataframe(tabela_conferencia.style.map(cor_status_prestacao, subset=['Situação']),
                             hide_index=True, use_container_width=True)
                st.caption('🟢 Paga: despesa quitada. 🔴 A pagar no mês: não paga, com vencimento na competência selecionada. 🟡 A pagar: não paga, fora dessa competência.')
                st.caption(
                    f'Total de despesas pagas: {moeda_c(despesas_pagas)} '
                    f'(Leônidas: {moeda_c(metade_leo)}; Nelson: {moeda_c(metade_nel)}). '
                    f'Despesas pendentes: {moeda_c(despesas_pendentes)} (não descontadas).'
                )
            else:
                st.info('Não existem despesas lançadas no período selecionado.')
            if desp:
                resumo_tipo = defaultdict(int)
                for d in desp:
                    resumo_tipo[str(d.get('tipo') or 'Outras')] += centavos(d.get('valor'))
                st.subheader('Despesas por categoria (pagas e pendentes)')
                st.dataframe(pd.DataFrame([{'Categoria': k, 'Total': moeda_c(v)} for k,v in resumo_tipo.items()]), hide_index=True, use_container_width=True)
            st.subheader('Extrato dos repasses no período')
            if rep:
                st.dataframe(pd.DataFrame([{'Data': r['data'].strftime('%d/%m/%Y'), 'Contrato': r['contrato'], 'Leônidas': moeda_c(r['leonidas']), 'Nelson': moeda_c(r['nelson'])} for r in rep]), hide_index=True, use_container_width=True)
            else:
                st.info('Nenhum repasse encontrado neste período.')

        with abas[5]:
            st.subheader('Calendário de prestação de contas')
            st.caption('Os movimentos são agrupados pelo mês de competência. A prestação de contas '
                       'ocorre entre os dias 1 e 5 do mês seguinte. Este calendário não confirma '
                       'automaticamente que os sócios receberam suas partes.')
            mes_fech = st.date_input('Competência para prestação de contas',
                                      value=hoje_fin.replace(day=1), key='prest_competencia').replace(day=1)
            janela_inicio, janela_fim = janela_prestacao(mes_fech)
            st.info(f'Movimentação de {mes_fech:%m/%Y} — prestar contas entre '
                    f'{janela_inicio:%d/%m/%Y} e {janela_fim:%d/%m/%Y}.')
            rep_fech = [r for r in repasses if r['data'].year == mes_fech.year and r['data'].month == mes_fech.month]
            hist_fech = [h for h in historicos_incluidos if h['data'].year == mes_fech.year and h['data'].month == mes_fech.month]
            desp_fech = [d for d in despesas if data_segura(d.get('competencia')) is not None
                         and data_segura(d.get('competencia')).year == mes_fech.year
                         and data_segura(d.get('competencia')).month == mes_fech.month]
            receitas_l = sum(x['leonidas'] for x in rep_fech) + sum(x['leonidas'] for x in hist_fech)
            receitas_n = sum(x['nelson'] for x in rep_fech) + sum(x['nelson'] for x in hist_fech)
            despesas_quitadas = sum(centavos(d.get('valor')) for d in desp_fech if d.get('situacao') == 'Paga')
            despesas_a_pagar = sum(centavos(d.get('valor')) for d in desp_fech if d.get('situacao') != 'Paga')
            desp_n = despesas_quitadas // 2
            desp_l = despesas_quitadas - desp_n
            st.dataframe(pd.DataFrame([
                {'Sócio': 'Leônidas', 'Receitas': moeda_c(receitas_l), 'Despesas pagas': moeda_c(desp_l), 'Saldo': moeda_c(receitas_l - desp_l)},
                {'Sócio': 'Nelson', 'Receitas': moeda_c(receitas_n), 'Despesas pagas': moeda_c(desp_n), 'Saldo': moeda_c(receitas_n - desp_n)},
            ]), hide_index=True, use_container_width=True)
            st.metric('Despesas da competência ainda pendentes', moeda_c(despesas_a_pagar))
            st.warning('A prestação de contas é uma conferência entre os sócios, não uma baixa automática. '
                       'Antes de fechar, confira despesas pendentes, recebimentos históricos e repasses. '
                       'A competência de parcelas históricas pode ser ajustada em Gerenciar Baixas.')
            if janela_inicio <= hoje_fin <= janela_fim:
                st.success('Estamos no período habitual de prestação de contas desta competência.')
            elif hoje_fin > janela_fim:
                st.caption('O período habitual de prestação de contas desta competência já passou.')
            else:
                st.caption('O período habitual de prestação de contas desta competência ainda não começou.')

        with abas[3]:
            st.subheader('Projeção de recebimentos por sócio')
            st.caption('Estimativa das parcelas pendentes, por mês e no período total. A projeção utiliza a regra interna de divisão dos sócios, sem aplicar desconto automático de colaboradores às parcelas futuras.')
            meses = st.slider('Meses à frente', min_value=1, max_value=24, value=12)
            base = hoje_fin.replace(day=1)
            proj = []
            total_bruto = total_despesas = total_leo_bruto = total_nel_bruto = 0
            total_leo_liquido = total_nel_liquido = total_parcelas = 0
            for i in range(meses):
                mi = base + relativedelta(months=i)
                mf = mi + relativedelta(months=1)
                parcelas_mes = [p for p in parcelas if str(p.get('status') or '').lower() == 'pendente' and (data_segura(p.get('vencimento')) is not None and mi <= data_segura(p.get('vencimento')) < mf)]
                bruto = sum(centavos(p.get('valor')) for p in parcelas_mes)
                despesas_mes = sum(centavos(d.get('valor')) for d in despesas if d.get('situacao') != 'Paga' and (data_segura(d.get('competencia')) is not None and mi <= data_segura(d.get('competencia')) < mf))
                estim_leo = (bruto * 60 + 50) // 100
                estim_nel = bruto - estim_leo
                custo_nel = despesas_mes // 2
                custo_leo = despesas_mes - custo_nel
                liquido_leo = estim_leo - custo_leo
                liquido_nel = estim_nel - custo_nel
                total_parcelas += len(parcelas_mes)
                total_bruto += bruto
                total_despesas += despesas_mes
                total_leo_bruto += estim_leo
                total_nel_bruto += estim_nel
                total_leo_liquido += liquido_leo
                total_nel_liquido += liquido_nel
                proj.append({'Mês': mi.strftime('%m/%Y'), 'Parcelas': len(parcelas_mes),
                             'A receber (bruto)': moeda_c(bruto),
                             'Leônidas (parcelas)': moeda_c(estim_leo),
                             'Nelson (parcelas)': moeda_c(estim_nel),
                             'Despesas pendentes': moeda_c(despesas_mes),
                             'Leônidas (após despesas)': moeda_c(liquido_leo),
                             'Nelson (após despesas)': moeda_c(liquido_nel)})
            st.markdown('#### Total projetado para o período')
            col_p1, col_p2, col_p3 = st.columns(3)
            col_p1.metric('Total de parcelas a receber', moeda_c(total_bruto))
            col_p2.metric('Leônidas — parcelas', moeda_c(total_leo_bruto))
            col_p3.metric('Nelson — parcelas', moeda_c(total_nel_bruto))
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.metric('Despesas pendentes previstas', moeda_c(total_despesas))
            col_d2.metric('Leônidas — após despesas', moeda_c(total_leo_liquido))
            col_d3.metric('Nelson — após despesas', moeda_c(total_nel_liquido))
            st.markdown('#### Projeção mês a mês')
            proj.append({'Mês': 'TOTAL DO PERÍODO', 'Parcelas': total_parcelas,
                         'A receber (bruto)': moeda_c(total_bruto),
                         'Leônidas (parcelas)': moeda_c(total_leo_bruto),
                         'Nelson (parcelas)': moeda_c(total_nel_bruto),
                         'Despesas pendentes': moeda_c(total_despesas),
                         'Leônidas (após despesas)': moeda_c(total_leo_liquido),
                         'Nelson (após despesas)': moeda_c(total_nel_liquido)})
            st.dataframe(pd.DataFrame(proj), hide_index=True, use_container_width=True)
            st.info('Valores por sócio são projeções, não repasses realizados. Eventuais pagamentos a colaboradores definidos na baixa futura reduzirão os valores efetivos. Os saldos após despesas consideram somente despesas pendentes cadastradas para cada mês.')
            st.warning('Parcelas vencidas antes do mês atual não entram nesta projeção. Despesas fixas ativas são projetadas mensalmente.')

    elif menu_escolha == "Distribuição de Processos":
        if user_role != 'admin':
            st.error("⛔ Acesso restrito. Este módulo é exclusivo para perfis Administradores.")
            st.stop()
        
        st.title("📥 Módulo: Distribuição de Processos")
        st.caption("Gerencie os clientes enviados para distribuição e atribua-os aos colaboradores responsáveis.")
        
        try:
            res_dist = supabase.table("distribuicao_processos").select("*").execute()
            lista_dist = res_dist.data if res_dist.data else []
            
            if not lista_dist:
                st.info("Nenhum cliente na fila de distribuição no momento.")
            else:
                df_dist = pd.DataFrame(lista_dist)
                
                if 'data_envio' in df_dist.columns:
                    df_dist['data_envio'] = df_dist['data_envio'].apply(formatar_data_br)
                if 'data_distribuicao' in df_dist.columns:
                    df_dist['data_distribuicao'] = df_dist['data_distribuicao'].apply(formatar_data_br)

                if 'status' in df_dist.columns:
                    exibir_tabela(df_dist.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                else:
                    exibir_tabela(df_dist, use_container_width=True, hide_index=True)

                st.markdown("---")
                
                tab_dist_cad, tab_dist_exc = st.tabs(["⚖️ Distribuir Processo", "🗑️ Excluir da Fila"])
                
                with tab_dist_cad:
                    pendentes_dist = [d for d in lista_dist if d.get('status') == 'Pendente']
                    if not pendentes_dist:
                        st.success("🎉 Todos os processos da fila já foram distribuídos!")
                    else:
                        dict_pendentes = {f"ID: {p['id']} | Cliente: {p['cliente_nome']} (CPF: {p.get('cpf_cnpj', 'N/D')})": p for p in pendentes_dist}
                        sel_dist_str = st.selectbox("Selecione o Cliente / Processo para Distribuir:", list(dict_pendentes.keys()), key="sel_dist_proc_atribuir")
                        obj_sel_dist = dict_pendentes[sel_dist_str]

                        lista_usuarios_dist = []
                        for u in credentials['usernames'].values():
                            n_u = u.get('name', '')
                            if n_u:
                                lista_usuarios_dist.append(n_u)

                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            adv_responsavel = st.selectbox("Selecione o Responsável:", lista_usuarios_dist, key="sel_resp_distribuicao")
                        with col_d2:
                            obs_dist = st.text_input("Observações da Distribuição", value="", key="input_obs_distrib")

                        if st.button("Confirmar e Distribuir Processo", type="primary", key="btn_conf_distrib"):
                            try:
                                supabase.table("distribuicao_processos").update({
                                    "responsavel": adv_responsavel,
                                    "status": "Distribuído",
                                    "data_distribuicao": date.today().strftime("%Y-%m-%d"),
                                    "observacoes_distribuicao": obs_dist
                                }).eq("id", obj_sel_dist['id']).execute()

                                supabase.table("meus_processos").insert({
                                    "numero_processo": obj_sel_dist.get('cpf_cnpj', 'N/D'),
                                    "cliente": obj_sel_dist.get('cliente_nome', 'Cliente'),
                                    "cliente_nome": obj_sel_dist.get('cliente_nome', 'Cliente'),
                                    "descricao": f"Processo distribuído por {name}. Obs: {obs_dist}",
                                    "status": "Aguardando Documentação",
                                    "responsavel": adv_responsavel,
                                    "solicitou_revisao": False
                                }).execute()

                                registrar_auditoria(username, "Distribuir Processo", "Distribuição", f"Cliente {obj_sel_dist['cliente_nome']} atribuído a {adv_responsavel}")
                                st.cache_data.clear()
                                confirmar_operacao(f"✅ Processo distribuído e enviado automaticamente para 'Meus Processos' de **{adv_responsavel}**!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao distribuir processo: {e}")

                with tab_dist_exc:
                    st.subheader("🗑️ Remover Registro da Fila de Distribuição")
                    dict_all_dist = {f"ID: {d['id']} | Cliente: {d['cliente_nome']} (Status: {d.get('status', 'Pendente')})": d['id'] for d in lista_dist}
                    sel_exc_dist_str = st.selectbox("Selecione o registro para excluir:", list(dict_all_dist.keys()), key="sel_exc_fila_dist")
                    id_para_excluir = dict_all_dist[sel_exc_dist_str]

                    if st.checkbox("Confirmo a exclusão permanente deste registro da fila de distribuição.", key="chk_conf_exc_dist"):
                        if st.button("🗑️ EXCLUIR REGISTRO SELECIONADO", type="primary", key="btn_exec_exc_dist"):
                            try:
                                supabase.table("distribuicao_processos").delete().eq("id", id_para_excluir).execute()
                                registrar_auditoria(username, "Excluir da Fila de Distribuição", "Distribuição", f"Registro ID {id_para_excluir} excluído.")
                                st.cache_data.clear()
                                confirmar_operacao("✅ Registro excluído da fila com sucesso!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir registro: {e}")
        except Exception as e:
            st.error(f"Erro ao carregar fila de distribuição: {e}")

    elif menu_escolha == "Auditoria" and user_role == 'admin':
        st.title("🛡️ Central de Auditoria do Sistema")
        st.caption("Acompanhe as ações gerais do sistema e os registros de acesso dos usuários.")
        
        tab_geral, tab_acessos = st.tabs(["🛡️ Auditoria Geral", "🔑 Logs de Acesso (Login / Logout)"])
        
        with tab_geral:
            st.subheader("Histórico de Ações Gerais")
            if st.button("🔥 ZERAR LOGS GERAIS", key="btn_zerar_geral"):
                try:
                    supabase.table("logs_auditoria").delete().neq("id", 0).execute()
                    confirmar_operacao("Logs gerais zerados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

            try:
                res_logs = supabase.table("logs_auditoria").select("*").neq("modulo", "Acesso").order("data_hora", desc=True).limit(100).execute()
                if res_logs.data:
                    df_logs = pd.DataFrame(res_logs.data)
                    exibir_tabela(df_logs, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum registro de auditoria geral encontrado.")
            except Exception as e:
                st.error(f"Erro ao carregar logs gerais: {e}")

        with tab_acessos:
            st.subheader("Histórico de Entradas e Saídas (Login / Logout)")
            if st.button("🔥 ZERAR LOGS DE ACESSO", key="btn_zerar_acesso"):
                try:
                    supabase.table("logs_auditoria").delete().eq("modulo", "Acesso").execute()
                    confirmar_operacao("Logs de acesso zerados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

            try:
                res_acessos = supabase.table("logs_auditoria").select("*").eq("modulo", "Acesso").order("data_hora", desc=True).limit(100).execute()
                if res_acessos.data:
                    df_acessos = pd.DataFrame(res_acessos.data)
                    exibir_tabela(df_acessos, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum registro de acesso encontrado.")
            except Exception as e:
                st.error(f"Erro ao carregar logs de acesso: {e}")

    else:
        # --- DOCUMENTOS E HISTÓRICO DE REVISÕES ---
        def revisao_administradores():
            return {u['name']: login for login, u in credentials['usernames'].items()
                    if u.get('role') == 'admin' and u.get('name')}

        def revisao_usuarios_ativos():
            # Contas disponíveis para receber correções; a conta master também pode receber.
            return {u.get('name') or login: login for login, u in credentials['usernames'].items()
                    if u.get('name') and u.get('role') not in ('inativo', 'bloqueado')}

        def revisao_arquivos(processo_id):
            return (supabase.table('revisao_documentos').select('*')
                    .eq('processo_id', processo_id).order('criado_em', desc=True).execute().data or [])

        def revisao_eventos(processo_id):
            return (supabase.table('revisao_eventos').select('*')
                    .eq('processo_id', processo_id).order('criado_em', desc=True).execute().data or [])

        # Cota preventiva: considera TODOS os buckets registrados em storage.objects.
        # A função RPC é instalada pelo SQL complementar e liberada apenas ao service_role.
        LIMITE_ARQUIVO_REVISAO = 10 * 1024 * 1024
        ALERTA_STORAGE = 700 * 1024 * 1024
        BLOQUEIO_STORAGE = 900 * 1024 * 1024

        def revisao_consumo_storage():
            resposta = cliente_storage_servidor().rpc('dejure_storage_uso_bytes').execute()
            valor = resposta.data
            if isinstance(valor, list):
                valor = valor[0] if valor else None
            if isinstance(valor, dict):
                valor = next(iter(valor.values()), None)
            if valor is None:
                raise RuntimeError('Consulta de armazenamento sem resultado. Execute o SQL de monitoramento.')
            return int(valor)

        def revisao_painel_storage():
            if user_role != 'admin':
                return
            st.subheader('Armazenamento de Documentos')
            try:
                uso = revisao_consumo_storage()
                st.metric('Espaço ocupado nos buckets do Supabase', f'{uso / (1024**2):,.1f} MB'.replace(',', 'X').replace('.', ',').replace('X', '.'))
                st.progress(min(1.0, uso / BLOQUEIO_STORAGE), text=f'{uso / BLOQUEIO_STORAGE:.0%} do limite preventivo de 900 MB')
                if uso >= BLOQUEIO_STORAGE:
                    st.error('Uploads de peças bloqueados: uso igual ou superior a 900 MB.')
                elif uso >= ALERTA_STORAGE:
                    st.warning('Atenção: uso de armazenamento acima de 700 MB.')
                else:
                    st.caption('Monitoramento preventivo ativo. Alertas a partir de 700 MB; bloqueio a partir de 900 MB.')
                st.caption('Mede arquivos registrados em todos os buckets Storage deste projeto, não o banco de dados nem outras cotas do plano Free.')
            except Exception as erro:
                st.error(f'Não foi possível consultar o armazenamento: {erro}. Por segurança, novos uploads ficam bloqueados.')

        def revisao_inventario_storage():
            """Lista todos os objetos do bucket privado, inclusive pastas paginadas."""
            cliente = cliente_storage_servidor()
            bucket = cliente.storage.from_('pecas-juridicas')
            itens = []
            pendentes = ['']
            while pendentes:
                pasta = pendentes.pop()
                deslocamento = 0
                while True:
                    lote = bucket.list(pasta, {'limit': 100, 'offset': deslocamento}) or []
                    for item in lote:
                        nome = item.get('name', '')
                        if not nome or nome == '.emptyFolderPlaceholder':
                            continue
                        caminho = f'{pasta}/{nome}' if pasta else nome
                        metadados = item.get('metadata') or {}
                        # Pastas do Storage não possuem metadata de objeto.
                        if not metadados and not item.get('id'):
                            pendentes.append(caminho)
                        else:
                            itens.append({
                                'caminho': caminho,
                                'bytes': int(metadados.get('size') or 0),
                                'criado_em': item.get('created_at') or '',
                                'tipo_mime': metadados.get('mimetype') or ''
                            })
                    if len(lote) < 100:
                        break
                    deslocamento += len(lote)
            return sorted(itens, key=lambda x: x['caminho'])

        def revisao_central_armazenamento():
            if user_role != 'admin' or st.session_state.get('authentication_status') is not True:
                st.error('Acesso exclusivo para administradores.')
                return
            st.subheader('Inventário e exclusão de arquivos')
            st.warning('A exclusão é definitiva. Baixe uma cópia antes de excluir. '
                       'Arquivos excluídos não poderão mais ser baixados no histórico de revisões.')
            try:
                arquivos = revisao_inventario_storage()
                registros = (cliente_storage_servidor().table('revisao_documentos')
                             .select('id,processo_id,nome_arquivo,caminho_storage,enviado_por,tipo')
                             .execute().data or [])
                por_caminho = {r.get('caminho_storage'): r for r in registros}
                total = sum(a['bytes'] for a in arquivos)
                c1, c2 = st.columns(2)
                c1.metric('Arquivos no bucket peças jurídicas', len(arquivos))
                c2.metric('Tamanho listado neste bucket', f'{total / 1048576:.2f} MB')
                st.caption('O medidor acima da Central de Revisões considera todos os buckets. '
                           'Este inventário lista somente o bucket privado pecas-juridicas.')
                busca = st.text_input('Filtrar por nome, processo ou usuário', key='inv_busca')
                linhas = []
                for a in arquivos:
                    r = por_caminho.get(a['caminho'], {})
                    linha = {
                        'Arquivo': r.get('nome_arquivo') or a['caminho'].split('/')[-1],
                        'Processo ID': str(r.get('processo_id') or a['caminho'].split('/')[0]),
                        'Enviado por': r.get('enviado_por') or 'Não identificado',
                        'Tipo': r.get('tipo') or a['tipo_mime'],
                        'Tamanho (MB)': round(a['bytes'] / 1048576, 3),
                        'Criado em': a['criado_em'],
                        'Caminho': a['caminho']
                    }
                    if not busca or busca.casefold() in ' '.join(str(v) for v in linha.values()).casefold():
                        linhas.append(linha)
                if not linhas:
                    st.info('Nenhum arquivo encontrado para o filtro informado.')
                    return
                exibir_tabela(pd.DataFrame(linhas), use_container_width=True, hide_index=True)
                opcoes = {f"{x['Arquivo']} | processo {x['Processo ID']} | {x['Caminho']}": x for x in linhas}
                escolha = st.selectbox('Selecione um arquivo para baixar ou excluir', list(opcoes), key='inv_arquivo')
                selecionado = opcoes[escolha]
                caminho = selecionado['Caminho']
                if st.button('Preparar download', key='inv_preparar'):
                    try:
                        dados = cliente_storage_servidor().storage.from_('pecas-juridicas').download(caminho)
                        st.session_state['inv_download'] = (caminho, dados)
                    except Exception as e:
                        st.error(f'Não foi possível baixar o arquivo: {e}')
                download = st.session_state.get('inv_download')
                if download and download[0] == caminho:
                    st.download_button('Baixar arquivo selecionado', data=download[1],
                                       file_name=selecionado['Arquivo'], key='inv_baixar')
                st.divider()
                st.markdown('**Excluir arquivo selecionado**')
                st.caption('A exclusão remove o objeto do Storage e seu registro em revisao_documentos. '
                           'O histórico de eventos do processo é preservado.')
                confirmacao = st.checkbox('Confirmo a exclusão definitiva deste arquivo específico',
                                           key=f'inv_conf_{caminho}')
                if st.button('Excluir definitivamente', type='primary', disabled=not confirmacao,
                             key='inv_excluir'):
                    try:
                        # Verificação no momento da ação, nunca confiar apenas na interface.
                        if user_role != 'admin' or st.session_state.get('authentication_status') is not True:
                            raise PermissionError('Operação não autorizada.')
                        cliente = cliente_storage_servidor()
                        cliente.storage.from_('pecas-juridicas').remove([caminho])
                        registro = por_caminho.get(caminho)
                        erro_db = None
                        if registro:
                            try:
                                cliente.table('revisao_documentos').delete().eq('id', registro['id']).execute()
                            except Exception as e:
                                erro_db = e
                        registrar_auditoria(username, 'Exclusão definitiva de documento', 'Armazenamento',
                            f"Bucket pecas-juridicas; caminho: {caminho}; processo: {selecionado['Processo ID']}; "
                            f"tamanho_bytes: {int(selecionado['Tamanho (MB)'] * 1048576)}")
                        st.session_state.pop('inv_download', None)
                        st.cache_data.clear()
                        if erro_db:
                            st.error(f'Arquivo removido do Storage, mas não foi possível limpar o registro no banco: {erro_db}')
                        else:
                            confirmar_operacao('Arquivo excluído do Storage. O espaço liberado aparecerá após atualização da medição.')
                            st.rerun()
                    except Exception as e:
                        st.error(f'Falha ao excluir: {e}. Verifique o arquivo no Storage antes de tentar novamente.')
            except Exception as e:
                st.error(f'Não foi possível listar o armazenamento: {e}')

        def revisao_upload(arquivo, processo_id, tipo):
            if arquivo is None:
                return None
            from uuid import uuid4
            nome = os.path.basename(arquivo.name)
            ext = os.path.splitext(nome)[1].lower()
            if ext not in ('.pdf', '.doc', '.docx'):
                raise ValueError('Formato não permitido. Utilize PDF, DOC ou DOCX.')
            conteudo = arquivo.getvalue()
            if len(conteudo) > LIMITE_ARQUIVO_REVISAO:
                raise ValueError('O limite é de 10 MB por arquivo.')
            # Falha fechada: sem medição confiável, não há novo upload.
            uso_atual = revisao_consumo_storage()
            if uso_atual >= BLOQUEIO_STORAGE or uso_atual + len(conteudo) > BLOQUEIO_STORAGE:
                raise ValueError('Upload bloqueado: o armazenamento atingiria o limite preventivo de 900 MB. Contate um administrador.')
            caminho = f"{processo_id}/{uuid4().hex}{ext}"
            cliente_storage_servidor().storage.from_('pecas-juridicas').upload(
                caminho, conteudo, {'content-type': {
                    '.pdf': 'application/pdf', '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }[ext], 'upsert': 'false'})
            try:
                supabase.table('revisao_documentos').insert({
                    'processo_id': processo_id, 'nome_arquivo': nome,
                    'caminho_storage': caminho, 'tipo': tipo, 'enviado_por': username
                }).execute()
            except Exception:
                cliente_storage_servidor().storage.from_('pecas-juridicas').remove([caminho])
                raise
            return caminho

        def revisao_evento(processo_id, acao, destino='', observacoes=''):
            supabase.table('revisao_eventos').insert({
                'processo_id': processo_id, 'acao': acao, 'usuario': username,
                'destinatario': destino or None, 'observacoes': observacoes or None
            }).execute()

        def revisao_mostrar_documentos(processo_id):
            for doc in revisao_arquivos(processo_id):
                with st.container(border=True):
                    st.write(f"{doc.get('nome_arquivo')} — {doc.get('tipo')} — {doc.get('enviado_por')}")
                    st.caption(str(doc.get('criado_em', '')))
                    if st.button('Baixar arquivo', key=f"download_rev_{doc['id']}"):
                        try:
                            arquivo = cliente_storage_servidor().storage.from_('pecas-juridicas').download(doc['caminho_storage'])
                            st.session_state[f"arquivo_rev_{doc['id']}"] = arquivo
                        except Exception as e:
                            st.error(f'Não foi possível acessar o documento: {e}')
                    if st.session_state.get(f"arquivo_rev_{doc['id']}") is not None:
                        st.download_button('Salvar documento', data=st.session_state[f"arquivo_rev_{doc['id']}"],
                            file_name=doc['nome_arquivo'], key=f"salvar_rev_{doc['id']}")

        def revisao_mostrar_historico(processo_id):
            for ev in revisao_eventos(processo_id):
                st.markdown(f"**{ev.get('acao')}** — {ev.get('usuario')} — {ev.get('criado_em')}")
                if ev.get('destinatario'):
                    st.caption(f"Destinatário: {ev['destinatario']}")
                if ev.get('observacoes'):
                    st.write(ev['observacoes'])

        menu_principal = menu_escolha
        st.title(f"{menu_principal}")

        if menu_principal == "Clientes":
            acoes = ["Consultar Clientes", "Cadastrar Cliente", "Importar Excel", "Editar Cliente", "Exportar Base (Backup)"]
            if user_role == 'admin': acoes.insert(4, "Excluir Cliente")
        elif menu_principal == "Prospectados Pendentes":
            acoes = ["Consultar Prospectados Pendentes", "Cadastrar Prospectado Pendente", "Editar Prospectado Pendente"]
            if user_role == 'admin': acoes.append("Excluir Prospectado Pendente")
        elif menu_principal == "Meus Processos":
            acoes = ["Consultar Meus Processos", "Cadastrar Processo"]
            if user_role == 'admin': acoes.extend(['Central de Revisões', 'Armazenamento'])
        elif menu_principal == "Pagamentos":
            acoes = ["Ver Parcelas", "Cadastrar Contrato", "Editar Contrato"]
            if user_role == 'admin': acoes = ["Ver Parcelas", "Cadastrar Contrato", "Cadastrar Parcelamento em Andamento", "RPV / Retroativos", "Baixar Parcela", "Extrato de Repasses", "Relatório por Período", "Editar Contrato", "Excluir Contrato"]
        elif menu_principal == "Perícias":
            acoes = ["Ver Perícias", "Cadastrar Perícia", "Importar Excel", "Editar Perícia"]
            if user_role == 'admin': acoes.append("Excluir Perícia")
        elif menu_principal == "Expedientes":
            acoes = ["Consultar Expedientes", "Cadastrar Expediente", "Importar Excel", "Editar Expediente"]
            if user_role == 'admin': acoes.append("Excluir Expediente")
        elif menu_principal == "Expedientes TRF":
            acoes = ["Consultar Expedientes TRF", "Cadastrar Expediente TRF", "Importar Excel", "Editar Expediente TRF"]
            if user_role == 'admin': acoes.append("Excluir Expediente TRF")
        elif menu_principal == "Pendências":
            acoes = ["Consultar Pendências", "Cadastrar Pendência", "Importar Excel", "Editar Pendência"]
            if user_role == 'admin': acoes.append("Excluir Pendência")
        elif menu_principal == "Equipe Dejure":
            acoes = ["Nossa Equipe"]
        elif menu_principal == "Segurança":
            acoes = ["Meu Perfil", "Alterar Senha"]
            if user_role == 'admin': acoes = ["Meu Perfil", "Gerenciar Usuários", "Cadastrar Novo Usuário", "Alterar Senha"]
            if username == "master": acoes.append("Reiniciar IDs de Teste")
        else:
            acoes = []

        if not st.session_state['submenu_atual'] or st.session_state['submenu_atual'] not in acoes:
            if acoes: st.session_state['submenu_atual'] = acoes[0]

        if acoes:
            cols = st.columns(len(acoes))
            for idx, acao in enumerate(acoes):
                with cols[idx]:
                    if st.button(acao, use_container_width=True, type="primary" if st.session_state['submenu_atual'] == acao else "secondary"):
                        st.session_state['submenu_atual'] = acao
                        limpar_flags_cadastro()
                        st.rerun()

        st.markdown("---")
        sub = st.session_state['submenu_atual']

        # --- MÓDULO CLIENTES ---
        if menu_principal == "Clientes":
            lista_prospectadores = ["Nenhum / Sem Prospectador", "Prospectador Externo"]
            for u in credentials['usernames'].values():
                nome_u = u.get('name', '')
                if nome_u and nome_u not in lista_prospectadores:
                    lista_prospectadores.append(nome_u)

            ufs = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
            estados_civis = ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"]

            if sub == "Cadastrar Cliente":
                st.header("👤 Cadastro Completo de Cliente")
                st.caption("Preencha as informações do cliente. Campos marcados com (*) são obrigatórios.")
                
                campos_cli = ['cli_nome', 'cli_doc', 'cli_prof', 'cli_ec', 'cli_tfixo', 'cli_cel', 'cli_email', 'cli_end', 'cli_cep', 'cli_logradouro', 'cli_numero', 'cli_bairro', 'cli_complemento', 'cli_cid', 'cli_uf', 'cli_gov', 'cli_obs']
                for campo in campos_cli:
                    if campo not in st.session_state:
                        st.session_state[campo] = ""

                if st.session_state.get('cad_cli_sucesso'):
                    st.success("🎉 Cliente cadastrado com sucesso!")
                    
                    st.markdown("##### 📤 Deseja enviar este cliente para a Distribuição de Processos?")
                    col_ds1, col_ds2 = st.columns(2)
                    with col_ds1:
                        if st.button("📤 Enviar para Distribuição", type="primary", use_container_width=True):
                            try:
                                cli_id_cad = st.session_state.get('ultimo_cliente_cadastrado_id')
                                cli_nome_cad = st.session_state.get('ultimo_cliente_cadastrado_nome')
                                cli_doc_cad = st.session_state.get('ultimo_cliente_cadastrado_doc')
                                cli_tel_cad = st.session_state.get('ultimo_cliente_cadastrado_tel')
                                cli_obs_cad = st.session_state.get('ultimo_cliente_cadastrado_obs')

                                supabase.table("distribuicao_processos").insert({
                                    "cliente_nome": cli_nome_cad,
                                    "cpf_cnpj": cli_doc_cad,
                                    "telefone": cli_tel_cad,
                                    "cadastrado_por": name,
                                    "status": "Pendente",
                                    "data_envio": date.today().strftime("%Y-%m-%d"),
                                    "observacoes": cli_obs_cad if cli_obs_cad else None
                                }).execute()
                                registrar_auditoria(username, "Enviar para Distribuição", "Clientes", f"Cliente: {cli_nome_cad} enviado para distribuição.")
                                st.cache_data.clear()
                                confirmar_operacao("✅ Cliente enviado para a Distribuição de Processos com sucesso!")
                                time.sleep(1)
                                limpar_flags_cadastro()
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Erro ao enviar para distribuição: {ex}")

                    with col_ds2:
                        if st.button("➕ Cadastrar Outro Cliente", use_container_width=True):
                            limpar_flags_cadastro()
                            st.rerun()
                else:
                    c_top1, c_top2 = st.columns(2)
                    with c_top1:
                        prospectador_sel = st.selectbox("Prospectador / Indicado Por *", lista_prospectadores, key="cad_cli_prosp_select")

                    nome_prosp_ext_val = ""
                    tel_prosp_ext_val = ""

                    if prospectador_sel == "Prospectador Externo":
                        st.markdown("##### 🤝 Informações Obrigatórias do Prospectador Externo")
                        cp_e1, cp_e2 = st.columns(2)
                        with cp_e1:
                            nome_prosp_ext_val = st.text_input("Nome do Prospectador Externo *", key="cad_cli_pe_nome")
                        with cp_e2:
                            tel_prosp_ext_val = st.text_input("Telefone do Prospectador Externo (com DDD) *", key="cad_cli_pe_tel")
                        st.markdown("---")

                    st.subheader("📋 Informações Pessoais & Profissionais")
                    c1, c2 = st.columns(2)
                    with c1:
                        n = st.text_input("Nome Completo *", key="cli_nome")
                        doc = st.text_input("CPF / CNPJ *", key="cli_doc")
                        
                        doc_limpo = ''.join(filter(str.isdigit, str(doc)))
                        if doc.strip():
                            if len(doc_limpo) == 11:
                                if not validar_cpf(doc_limpo):
                                    st.error("⚠️ CPF inválido!")
                                else:
                                    st.success("✅ CPF válido.")
                            elif len(doc_limpo) == 14:
                                st.success("✅ CNPJ informado.")
                            elif len(doc_limpo) > 0:
                                st.warning("⚠️ CPF/CNPJ incompleto (deve ter 11 ou 14 dígitos).")

                        profissao = st.text_input("Profissão *", key="cli_prof")
                    with c2:
                        estado_civil = st.selectbox("Estado Civil *", estados_civis, key="cli_ec")

                    st.subheader("📞 Contatos & Endereço")
                    c3, c4 = st.columns(2)
                    with c3:
                        tel_fixo = st.text_input("Telefone Fixo (Opcional - ex: 8432221100)", key="cli_tfixo")
                        celular = st.text_input("Celular / WhatsApp (com DDD, ex: 84999887766) *", key="cli_cel")
                        email = st.text_input("E-mail", key="cli_email")
                        
                        if email.strip():
                            if not validar_email(email):
                                st.error("⚠️ Formato de e-mail inválido (ex: nome@dominio.com)")
                            else:
                                st.success("✅ E-mail válido.")

                    with c4:
                        st.text_input("CEP *", key="cli_cep", max_chars=9, placeholder="00000-000")
                        if st.button("Buscar CEP", key="buscar_cep_cadastro"):
                            aplicar_cep_campos("cli_")
                            st.rerun()
                        if st.session_state.get("cli_cep_mensagem"):
                            st.caption(st.session_state["cli_cep_mensagem"])
                        logradouro = st.text_input("Logradouro *", key="cli_logradouro")
                        numero = st.text_input("Número *", key="cli_numero")
                        bairro = st.text_input("Bairro *", key="cli_bairro")
                        complemento = st.text_input("Complemento (opcional)", key="cli_complemento")
                        cid = st.text_input("Cidade *", key="cli_cid")
                        uf = st.selectbox("Estado (UF) *", ufs, index=ufs.index(st.session_state.get("cli_uf", "RN")) if st.session_state.get("cli_uf", "RN") in ufs else 0, key="cli_uf")
                        end = endereco_legado(logradouro, numero, bairro)

                    st.subheader("🔐 Acesso & Observações")
                    c5, c6 = st.columns(2)
                    with c5:
                        gov = st.text_input("Senha Gov.br", key="cli_gov")
                    with c6:
                        obs = st.text_area("Observações", key="cli_obs")
                    
                    col_b_cad, col_b_vol = st.columns(2)
                    with col_b_cad:
                        salvar_cli = st.button("Salvar Cliente", type="primary", use_container_width=True)
                    with col_b_vol:
                        voltar_cli = st.button("⬅️ Voltar", use_container_width=True)

                    if voltar_cli:
                        st.session_state['submenu_atual'] = "Consultar Clientes"
                        st.rerun()

                    if salvar_cli:
                        errs = []
                        if not n.strip(): errs.append("O campo **Nome Completo** é obrigatório.")
                        if not profissao.strip(): errs.append("O campo **Profissão** é obrigatório.")
                        if not logradouro.strip() or not bairro.strip() or not numero.strip():
                            errs.append("Preencha logradouro, bairro e número.")
                        if len(re.sub(r"\D", "", st.session_state.get("cli_cep", ""))) != 8:
                            errs.append("Informe um CEP válido com 8 dígitos.")
                        if not cid.strip(): errs.append("O campo **Cidade** é obrigatório.")
                        
                        if tel_fixo.strip() and not validar_telefone_fixo(tel_fixo):
                            errs.append("O **Telefone Fixo** informado deve conter exatamente 10 dígitos (DDD + 8 números).")
                            
                        if not celular.strip():
                            errs.append("O campo **Celular / WhatsApp** é obrigatório.")
                        elif not validar_celular(celular):
                            errs.append("O **Celular** deve conter 11 dígitos no padrão (DDD + 9 + 8 números).")

                        if email.strip() and not validar_email(email):
                            errs.append("O **E-mail** informado possui formato inválido.")

                        if doc.strip():
                            doc_l = ''.join(filter(str.isdigit, str(doc)))
                            if len(doc_l) == 11 and not validar_cpf(doc_l): 
                                errs.append("O **CPF** informado é inválido!")
                            elif len(doc_l) != 11 and len(doc_l) != 14:
                                errs.append("O **CPF/CNPJ** deve conter exatamente 11 dígitos (CPF) ou 14 dígitos (CNPJ).")
                        else:
                            errs.append("O campo **CPF/CNPJ** é obrigatório.")

                        if prospectador_sel == "Prospectador Externo":
                            if not nome_prosp_ext_val.strip():
                                errs.append("O campo **Nome do Prospectador Externo** é obrigatório.")
                            if not tel_prosp_ext_val.strip():
                                errs.append("O campo **Telefone do Prospectador Externo** é obrigatório.")
                            elif not (validar_telefone_fixo(tel_prosp_ext_val) or validar_celular(tel_prosp_ext_val)):
                                errs.append("O **Telefone do Prospectador Externo** deve conter DDD + número válido (10 ou 11 dígitos).")

                        if errs:
                            for e in errs:
                                st.error(f"⚠️ {e}")
                        else:
                            try:
                                tel_f_fmt = formatar_telefone(tel_fixo) if tel_fixo.strip() else None
                                cel_fmt = formatar_telefone(celular)

                                prosp_final = prospectador_sel
                                if prospectador_sel == "Prospectador Externo":
                                    tel_prosp_fmt = formatar_telefone(tel_prosp_ext_val)
                                    prosp_final = f"Prospectador Externo: {nome_prosp_ext_val.strip()} ({tel_prosp_fmt})"

                                payload = {
                                    "nome": n.strip(),
                                    "cpf_cnpj": doc.strip(),
                                    "telefone": tel_f_fmt,
                                    "celular": cel_fmt,
                                    "email": email.strip() if email.strip() else None,
                                    "endereco": end.strip(),
                                    "cep": re.sub(r"\D", "", st.session_state["cli_cep"]),
                                    "logradouro": logradouro.strip(),
                                    "numero": numero.strip(),
                                    "bairro": bairro.strip(),
                                    "complemento": complemento.strip() or None,
                                    "cidade": cid.strip(),
                                    "uf": uf,
                                    "profissao": profissao.strip(),
                                    "estado_civil": estado_civil,
                                    "indicado_por": prosp_final if prosp_final else None,
                                    "senha_gov": gov.strip() if gov.strip() else None,
                                    "observacoes": obs.strip() if obs.strip() else None
                                }

                                res_ins = supabase.table("clientes_cadastrados").insert(payload).execute()
                                cli_cad_id = res_ins.data[0]['id'] if res_ins.data else None

                                registrar_auditoria(username, "Cadastrar Cliente", "Clientes", f"Cliente: {n.strip()}")
                                st.cache_data.clear()
                                
                                st.session_state['cad_cli_sucesso'] = True
                                confirmar_operacao('Cliente cadastrado com sucesso!')
                                st.session_state['ultimo_cliente_cadastrado_id'] = cli_cad_id
                                st.session_state['ultimo_cliente_cadastrado_nome'] = n.strip()
                                st.session_state['ultimo_cliente_cadastrado_doc'] = doc.strip()
                                st.session_state['ultimo_cliente_cadastrado_tel'] = cel_fmt
                                st.session_state['ultimo_cliente_cadastrado_obs'] = obs.strip() if obs.strip() else ""

                                st.rerun()
                            except Exception as ex:
                                st.error(f"⚠️ Erro ao salvar no banco de dados. Verifique o painel do Supabase: {ex}")

            elif sub == "Importar Excel":
                st.header("📥 Importar Clientes via Planilha Excel")
                st.caption("O arquivo deve conter as colunas: nome, cpf_cnpj, telefone, celular, email, endereco, cidade, uf, profissao, estado_civil, indicado_por, senha_gov, observacoes")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_cli")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("clientes_cadastrados", file_up)

            elif sub == "Consultar Clientes":
                st.header("📋 Base Completa de Clientes")
                res = carregar_dados("clientes_cadastrados")
                if res: 
                    df_cli = pd.DataFrame(res)
                    exibir_tabela(df_cli, use_container_width=True, hide_index=True)
                else: 
                    st.info("Nenhum cliente cadastrado.")

                if res:
                    st.markdown("---")
                    st.subheader("📤 Enviar cliente cadastrado para Distribuição")
                    st.caption("Selecione um cliente da lista acima. O sistema verifica se ele já está na fila antes de enviar.")
                    opcoes_envio = {f"ID: {c['id']} — {c.get('nome', 'Sem nome')}": c for c in res}
                    selecionado_envio = st.selectbox(
                        "Cliente a enviar:", list(opcoes_envio.keys()), key="cliente_envio_distribuicao"
                    )
                    cliente_envio = opcoes_envio[selecionado_envio]
                    if st.button("📤 Enviar para Distribuição", type="primary", key="btn_envio_cliente_existente"):
                        try:
                            nome_envio = str(cliente_envio.get("nome") or "").strip()
                            doc_envio = str(cliente_envio.get("cpf_cnpj") or "").strip()
                            fila_atual = supabase.table("distribuicao_processos").select(
                                "id,cliente_nome,cpf_cnpj,status"
                            ).execute().data or []

                            def normalizar_documento(valor):
                                return "".join(ch for ch in str(valor or "") if ch.isdigit())

                            doc_normalizado = normalizar_documento(doc_envio)
                            ja_enviado = any(
                                (doc_normalizado and normalizar_documento(item.get("cpf_cnpj")) == doc_normalizado)
                                or (not doc_normalizado and
                                    str(item.get("cliente_nome") or "").strip().casefold() == nome_envio.casefold())
                                for item in fila_atual
                            )
                            if ja_enviado:
                                st.warning("⚠️ Este cliente já consta na Distribuição de Processos. Nenhum registro duplicado foi criado.")
                            else:
                                telefone_envio = cliente_envio.get("celular") or cliente_envio.get("telefone") or None
                                supabase.table("distribuicao_processos").insert({
                                    "cliente_nome": nome_envio,
                                    "cpf_cnpj": doc_envio or None,
                                    "telefone": telefone_envio,
                                    "cadastrado_por": name,
                                    "status": "Pendente",
                                    "data_envio": date.today().strftime("%Y-%m-%d"),
                                    "observacoes": cliente_envio.get("observacoes") or None
                                }).execute()
                                registrar_auditoria(
                                    username, "Enviar para Distribuição", "Clientes",
                                    f"Cliente existente: {nome_envio} (ID: {cliente_envio['id']})"
                                )
                                st.cache_data.clear()
                                confirmar_operacao(f"✅ {nome_envio} enviado para a Distribuição de Processos!")
                                st.rerun()
                        except Exception as ex:
                            st.error(f"Erro ao enviar cliente para distribuição: {ex}")

            elif sub == "Editar Cliente":
                st.header("✏️ Editar Cadastro de Cliente")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    cdict = {f"ID: {c['id']} — {c['nome']}": c for c in res}
                    sel = st.selectbox("Selecione o Cliente:", list(cdict.keys()))
                    obj = cdict[sel]

                    prosp_salvo = obj.get('indicado_por', '')
                    is_prosp_ext_salvo = str(prosp_salvo).startswith("Prospectador Externo:")

                    nome_ext_init = ""
                    tel_ext_init = ""
                    if is_prosp_ext_salvo:
                        idx_sel_prosp = lista_prospectadores.index("Prospectador Externo")
                        try:
                            match = re.search(r"Prospectador Externo:\s*(.*?)\s*\((.*?)\)", prosp_salvo)
                            if match:
                                nome_ext_init = match.group(1)
                                tel_ext_init = match.group(2)
                        except:
                            pass
                    else:
                        idx_sel_prosp = lista_prospectadores.index(prosp_salvo) if prosp_salvo in lista_prospectadores else 0

                    c_top_ed1, c_top_ed2 = st.columns(2)
                    with c_top_ed1:
                        eprospectador_sel = st.selectbox("Prospectador / Indicado Por *", lista_prospectadores, index=idx_sel_prosp, key="ed_cli_prosp_select")

                    enome_prosp_ext_val = ""
                    etel_prosp_ext_val = ""
                    if eprospectador_sel == "Prospectador Externo":
                        st.markdown("##### 🤝 Informações do Prospectador Externo")
                        cep_e1, cep_e2 = st.columns(2)
                        with cep_e1:
                            enome_prosp_ext_val = st.text_input("Nome do Prospectador Externo *", value=nome_ext_init, key="ed_cli_pe_nome")
                        with cep_e2:
                            etel_prosp_ext_val = st.text_input("Telefone do Prospectador Externo (com DDD) *", value=tel_ext_init, key="ed_cli_pe_tel")
                        st.markdown("---")

                    # Busca fora do formulário: o Streamlit permite atualizar campos imediatamente.
                    chave_ed = f"ed_{obj['id']}_"
                    for campo, coluna in (("cep", "cep"), ("logradouro", "logradouro"),
                                          ("numero", "numero"), ("bairro", "bairro"),
                                          ("complemento", "complemento"), ("cid", "cidade"), ("uf", "uf")):
                        st.session_state.setdefault(chave_ed + campo, obj.get(coluna) or (obj.get("endereco", "") if campo == "logradouro" else ("RN" if campo == "uf" else "")))
                    st.text_input("CEP do cliente", key=chave_ed + "cep", max_chars=9)
                    if st.button("Buscar CEP para edição", key=f"buscar_cep_ed_{obj['id']}"):
                        aplicar_cep_campos(chave_ed)
                        st.rerun()
                    if st.session_state.get(chave_ed + "cep_mensagem"):
                        st.caption(st.session_state[chave_ed + "cep_mensagem"])
                    with st.form("fe_cli"):
                        st.subheader("📋 Informações Pessoais & Profissionais")
                        c1, c2 = st.columns(2)
                        with c1:
                            en = st.text_input("Nome Completo *", value=obj.get('nome',''))
                            edoc = st.text_input("CPF / CNPJ *", value=obj.get('cpf_cnpj',''))
                            eprofi = st.text_input("Profissão *", value=obj.get('profissao',''))
                        with c2:
                            idx_ec = estados_civis.index(obj.get('estado_civil')) if obj.get('estado_civil') in estados_civis else 0
                            eestado_civil = st.selectbox("Estado Civil *", estados_civis, index=idx_ec)

                        st.subheader("📞 Contatos & Endereço")
                        c3, c4 = st.columns(2)
                        with c3:
                            etel_fixo = st.text_input("Telefone Fixo (Opcional)", value=obj.get('telefone','') or '')
                            ecelular = st.text_input("Celular / WhatsApp *", value=obj.get('celular',''))
                            eemail = st.text_input("E-mail", value=obj.get('email','') or '')
                        with c4:
                            elog = st.text_input("Logradouro *", key=chave_ed + "logradouro")
                            enum = st.text_input("Número *", key=chave_ed + "numero")
                            ebairro = st.text_input("Bairro *", key=chave_ed + "bairro")
                            ecomp = st.text_input("Complemento", key=chave_ed + "complemento")
                            ecid = st.text_input("Cidade *", key=chave_ed + "cid")
                            euf = st.selectbox("Estado (UF) *", ufs, key=chave_ed + "uf")
                            eend = endereco_legado(elog, enum, ebairro)

                        st.subheader("🔐 Acesso & Observações")
                        c5, c6 = st.columns(2)
                        with c5:
                            egov = st.text_input("Senha Gov.br", value=obj.get('senha_gov','') or '')
                        with c6:
                            eobs = st.text_area("Observações", value=obj.get('observacoes','') or '')

                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            atualizar_cli = st.form_submit_button("Atualizar Cliente", type="primary", use_container_width=True)
                        with col_e2:
                            voltar_ed_cli = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if atualizar_cli:
                            errs = []
                            if not en.strip(): errs.append("O campo **Nome Completo** é obrigatório.")
                            if not eprofi.strip(): errs.append("O campo **Profissão** é obrigatório.")
                            if not elog.strip() or not enum.strip() or not ebairro.strip():
                                errs.append("Preencha logradouro, número e bairro.")
                            if len(re.sub(r"\D", "", st.session_state.get(chave_ed + "cep", ""))) != 8:
                                errs.append("Informe um CEP válido com 8 dígitos.")
                            if not ecid.strip(): errs.append("O campo **Cidade** é obrigatório.")
                            
                            if etel_fixo.strip() and not validar_telefone_fixo(etel_fixo):
                                errs.append("O **Telefone Fixo** deve conter exatamente 10 dígitos.")

                            if not ecelular.strip():
                                errs.append("O campo **Celular / WhatsApp** é obrigatório.")
                            elif not validar_celular(ecelular):
                                errs.append("O **Celular** deve conter 11 dígitos com o 9 na frente.")

                            if eemail.strip() and not validar_email(eemail):
                                errs.append("O **E-mail** informado possui formato inválido.")

                            if edoc.strip():
                                doc_l = ''.join(filter(str.isdigit, str(edoc)))
                                if len(doc_l) == 11 and not validar_cpf(doc_l): 
                                    errs.append("O **CPF** informado é inválido!")
                                elif len(doc_l) != 11 and len(doc_l) != 14:
                                    errs.append("O **CPF/CNPJ** deve conter exatamente 11 dígitos (CPF) ou 14 dígitos (CNPJ).")
                            else:
                                errs.append("O campo **CPF/CNPJ** é obrigatório.")

                            if eprospectador_sel == "Prospectador Externo":
                                if not enome_prosp_ext_val.strip():
                                    errs.append("O campo **Nome do Prospectador Externo** é obrigatório.")
                                if not etel_prosp_ext_val.strip():
                                    errs.append("O campo **Telefone do Prospectador Externo** é obrigatório.")
                                elif not (validar_telefone_fixo(etel_prosp_ext_val) or validar_celular(etel_prosp_ext_val)):
                                    errs.append("O **Telefone do Prospectador Externo** deve conter DDD + número válido (10 ou 11 dígitos).")

                            if errs:
                                for e in errs:
                                    st.error(f"⚠️ {e}")
                            else:
                                try:
                                    eprosp_final = eprospectador_sel
                                    if eprospectador_sel == "Prospectador Externo":
                                        etel_ext_fmt = formatar_telefone(etel_prosp_ext_val)
                                        eprosp_final = f"Prospectador Externo: {enome_prosp_ext_val.strip()} ({etel_ext_fmt})"

                                    payload_ed = {
                                        "nome": en.strip(),
                                        "cpf_cnpj": edoc.strip(),
                                        "telefone": formatar_telefone(etel_fixo) if etel_fixo.strip() else None,
                                        "celular": formatar_telefone(ecelular),
                                        "email": eemail.strip() if eemail.strip() else None,
                                        "endereco": eend.strip(),
                                        "cep": re.sub(r"\D", "", st.session_state[chave_ed + "cep"]),
                                        "logradouro": elog.strip(),
                                        "numero": enum.strip(),
                                        "bairro": ebairro.strip(),
                                        "complemento": ecomp.strip() or None,
                                        "cidade": ecid.strip(),
                                        "uf": euf,
                                        "profissao": eprofi.strip(),
                                        "estado_civil": eestado_civil,
                                        "indicado_por": eprosp_final,
                                        "senha_gov": egov.strip() if egov.strip() else None,
                                        "observacoes": eobs.strip() if eobs.strip() else None
                                    }

                                    supabase.table("clientes_cadastrados").update(payload_ed).eq("id", obj['id']).execute()

                                    registrar_auditoria(username, "Editar Cliente", "Clientes", f"ID: {obj['id']} - {en.strip()}")
                                    st.cache_data.clear()
                                    confirmar_operacao("🎉 Cliente atualizado com sucesso!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"⚠️ Erro ao atualizar no Supabase: {ex}")

                        if voltar_ed_cli:
                            st.session_state['submenu_atual'] = "Consultar Clientes"
                            st.rerun()
                else: 
                    st.info("Nenhum cliente para editar.")

            elif sub == "Excluir Cliente" and user_role == 'admin':
                st.header("🗑️ Excluir Cliente")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    cdict = {f"ID: {c['id']} — {c['nome']}": c['id'] for c in res}
                    sel = st.selectbox("Cliente:", list(cdict.keys()))
                    if st.checkbox("Confirmo exclusão permanente deste cliente.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("clientes_cadastrados").delete().eq("id", cdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Cliente", "Clientes", f"ID: {cdict[sel]}")
                        st.cache_data.clear(); confirmar_operacao("Excluído!"); st.rerun()
                    
                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de toda a base de clientes.")
                    if st.checkbox("Confirmo a exclusão de TODOS os registros de clientes do sistema."):
                        if st.button("🔥 EXCLUIR TODOS OS CLIENTES", type="primary"):
                            supabase.table("clientes_cadastrados").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS CLIENTES", "Clientes", "Exclusão em massa executada.")
                            st.cache_data.clear(); confirmar_operacao("Todos os registros foram excluídos com sucesso!"); st.rerun()
                else: st.info("Nenhum cliente cadastrado.")

            elif sub == "Exportar Base (Backup)":
                st.header("📥 Backup de Clientes")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    registrar_auditoria(username, "Backup Clientes", "Clientes", "Download da base realizado.")
                    st.download_button("Baixar CSV", data=pd.DataFrame(res).to_csv(index=False).encode('utf-8'), file_name=f"clientes_{date.today()}.csv", mime="text/csv", type="primary")
                else: st.info("Sem dados.")

        # --- MÓDULO PROSPECTADOS PENDENTES ---
        elif menu_principal == "Prospectados Pendentes":
            if sub == "Cadastrar Prospectado Pendente":
                st.header("📍 Cadastrar Novo Prospectado Pendente")
                st.caption("Clientes indicados que ainda não foram visitados. Nome e Prospectador são obrigatórios (*).")

                with st.form("form_cad_pros_pend", clear_on_submit=True):
                    cp_nome = st.text_input("Nome do Cliente *")
                    cp_tel = st.text_input("Telefone Fixo (Opcional)")
                    cp_cel = st.text_input("Celular (Opcional)")
                    cp_prosp = st.text_input("Prospectador *")
                    cp_cel_pros = st.text_input("Celular do Prospectado (Opcional)")

                    col_bp1, col_bp2 = st.columns(2)
                    with col_bp1:
                        salvar_pros = st.form_submit_button("Salvar Prospectado Pendente", type="primary", use_container_width=True)
                    with col_bp2:
                        voltar_pros = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_pros:
                        errs_pros = []
                        if not cp_nome.strip(): errs_pros.append("O campo **Nome** é obrigatório.")
                        if not cp_prosp.strip(): errs_pros.append("O campo **Prospectador** é obrigatório.")

                        if cp_tel.strip() and not validar_telefone_fixo(cp_tel):
                            errs_pros.append("O **Telefone** deve conter exatamente 10 dígitos.")
                        if cp_cel.strip() and not validar_celular(cp_cel):
                            errs_pros.append("O **Celular** deve conter 11 dígitos com o 9 na frente.")
                        if cp_cel_pros.strip() and not validar_celular(cp_cel_pros):
                            errs_pros.append("O **Celular do Prospectado** deve conter 11 dígitos com o 9 na frente.")

                        if errs_pros:
                            for e in errs_pros:
                                st.error(f"⚠️ {e}")
                        else:
                            try:
                                supabase.table("prospectados_pendentes").insert({
                                    "nome": cp_nome.strip(),
                                    "telefone": formatar_telefone(cp_tel) if cp_tel.strip() else None,
                                    "celular": formatar_telefone(cp_cel) if cp_cel.strip() else None,
                                    "prospectador": cp_prosp.strip(),
                                    "celular_prospectados": formatar_telefone(cp_cel_pros) if cp_cel_pros.strip() else None,
                                    "atendido": False
                                }).execute()

                                registrar_auditoria(username, "Cadastrar Prospectado Pendente", "Prospectados Pendentes", f"Cliente: {cp_nome.strip()} - Prospectador: {cp_prosp.strip()}")
                                st.cache_data.clear()
                                st.session_state['cad_pros_pend_sucesso'] = True
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Erro ao salvar prospectado pendente: {ex}")

                    if voltar_pros:
                        st.session_state['submenu_atual'] = "Consultar Prospectados Pendentes"
                        st.rerun()

                if st.session_state.get('cad_pros_pend_sucesso'):
                    confirmar_operacao("🎉 Prospectado pendente cadastrado com sucesso!")
                    col_1, col_2 = st.columns(2)
                    with col_1:
                        if st.button("➕ Cadastrar Outro", key="btn_novo_pros_pend", type="primary", use_container_width=True):
                            st.session_state['cad_pros_pend_sucesso'] = False
                            st.rerun()
                    with col_2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_pros_pend", use_container_width=True):
                            st.session_state['cad_pros_pend_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Prospectados Pendentes"
                            st.rerun()

            elif sub == "Consultar Prospectados Pendentes":
                st.header("📋 Lista de Clientes Indicados (Não Visitados)")
                res_pros = carregar_dados("prospectados_pendentes")
                
                # Filtra para exibir apenas os que ainda não foram atendidos por padrão, ou dá opção de ver todos
                mostrar_todos = st.checkbox("Mostrar também os prospectados já atendidos", value=False)
                
                if res_pros:
                    if not mostrar_todos:
                        res_pros_filtrado = [p for p in res_pros if not p.get('atendido', False)]
                    else:
                        res_pros_filtrado = res_pros

                    if not res_pros_filtrado:
                        st.info("Nenhum prospectado pendente no momento. Todos foram atendidos! 🎉")
                    else:
                        st.markdown("##### ⚡ Marque a caixa **Atendido** para concluir a visita e remover o alerta da Visão Geral:")
                        
                        for p in res_pros_filtrado:
                            with st.container(border=True):
                                col_info1, col_info2, col_info3, col_info4 = st.columns([3, 2, 2, 1])
                                with col_info1:
                                    st.write(f"**Nome:** {p.get('nome')}")
                                    st.caption(f"Prospectador: {p.get('prospectador')}")
                                with col_info2:
                                    st.write(f"**Tel / Cel:** {p.get('telefone') or p.get('celular') or 'N/D'}")
                                with col_info3:
                                    st.write(f"**Cel. Prospectado:** {p.get('celular_prospectados') or 'N/D'}")
                                with col_info4:
                                    status_atual = p.get('atendido', False)
                                    check_atendido = st.checkbox("Atendido", value=status_atual, key=f"chk_atend_{p['id']}")
                                    
                                    if check_atendido != status_atual:
                                        try:
                                            supabase.table("prospectados_pendentes").update({"atendido": check_atendido}).eq("id", p['id']).execute()
                                            registrar_auditoria(username, "Marcar Atendido", "Prospectados Pendentes", f"ID {p['id']} alterado para atendido: {check_atendido}")
                                            st.cache_data.clear()
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Erro ao atualizar: {e}")
                else:
                    st.info("Nenhum prospectado pendente cadastrado no momento.")

            elif sub == "Editar Prospectado Pendente":
                st.header("✏️ Editar Prospectado Pendente")
                res_pros = carregar_dados("prospectados_pendentes")
                if res_pros:
                    pdict = {f"ID: {p['id']} | {p['nome']} (Prospectador: {p['prospectador']})": p for p in res_pros}
                    sel_p = st.selectbox("Selecione o Prospectado Pendente:", list(pdict.keys()))
                    obj_p = pdict[sel_p]

                    with st.form("form_ed_pros_pend"):
                        ep_nome = st.text_input("Nome do Cliente *", value=obj_p.get('nome', ''))
                        ep_tel = st.text_input("Telefone Fixo", value=obj_p.get('telefone', '') or '')
                        ep_cel = st.text_input("Celular", value=obj_p.get('celular', '') or '')
                        ep_prosp = st.text_input("Prospectador *", value=obj_p.get('prospectador', ''))
                        ep_cel_pros = st.text_input("Celular do Prospectado", value=obj_p.get('celular_prospectados', '') or '')
                        ep_atendido = st.checkbox("Marcar como Atendido", value=obj_p.get('atendido', False))

                        col_ep1, col_ep2 = st.columns(2)
                        with col_ep1:
                            salvar_ed_pros = st.form_submit_button("Atualizar Prospectado", type="primary", use_container_width=True)
                        with col_ep2:
                            voltar_ed_pros = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_pros:
                            errs_ed = []
                            if not ep_nome.strip(): errs_ed.append("O campo **Nome** é obrigatório.")
                            if not ep_prosp.strip(): errs_ed.append("O campo **Prospectador** é obrigatório.")

                            if ep_tel.strip() and not validar_telefone_fixo(ep_tel):
                                errs_ed.append("O **Telefone** deve conter exatamente 10 dígitos.")
                            if ep_cel.strip() and not validar_celular(ep_cel):
                                errs_ed.append("O **Celular** deve conter 11 dígitos.")
                            if ep_cel_pros.strip() and not validar_celular(ep_cel_pros):
                                errs_ed.append("O **Celular do Prospectado** deve conter 11 dígitos.")

                            if errs_ed:
                                for e in errs_ed:
                                    st.error(f"⚠️ {e}")
                            else:
                                try:
                                    supabase.table("prospectados_pendentes").update({
                                        "nome": ep_nome.strip(),
                                        "telefone": formatar_telefone(ep_tel) if ep_tel.strip() else None,
                                        "celular": formatar_telefone(ep_cel) if ep_cel.strip() else None,
                                        "prospectador": ep_prosp.strip(),
                                        "celular_prospectados": formatar_telefone(ep_cel_pros) if ep_cel_pros.strip() else None,
                                        "atendido": ep_atendido
                                    }).eq("id", obj_p['id']).execute()

                                    registrar_auditoria(username, "Editar Prospectado Pendente", "Prospectados Pendentes", f"ID: {obj_p['id']} - {ep_nome.strip()}")
                                    st.cache_data.clear()
                                    confirmar_operacao("🎉 Prospectado atualizado com sucesso!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Erro ao atualizar: {ex}")

                        if voltar_ed_pros:
                            st.session_state['submenu_atual'] = "Consultar Prospectados Pendentes"
                            st.rerun()
                else:
                    st.info("Nenhum prospectado pendente para editar.")

            elif sub == "Excluir Prospectado Pendente" and user_role == 'admin':
                st.header("🗑️ Excluir Prospectado Pendente")
                res_pros = carregar_dados("prospectados_pendentes")
                if res_pros:
                    pdict = {f"ID: {p['id']} | {p['nome']} (Prospectador: {p['prospectador']})": p['id'] for p in res_pros}
                    sel_p_del = st.selectbox("Selecione para excluir:", list(pdict.keys()))
                    
                    if st.checkbox("Confirmo exclusão permanente deste prospectado pendente."):
                        if st.button("EXCLUIR SELECIONADO", type="primary"):
                            supabase.table("prospectados_pendentes").delete().eq("id", pdict[sel_p_del]).execute()
                            registrar_auditoria(username, "Excluir Prospectado Pendente", "Prospectados Pendentes", f"ID: {pdict[sel_p_del]}")
                            st.cache_data.clear()
                            confirmar_operacao("✅ Excluído com sucesso!")
                            st.rerun()
                else:
                    st.info("Nenhum prospectado pendente cadastrado.")

        # --- MÓDULO MEUS PROCESSOS ---
        elif menu_principal == "Meus Processos":
            status_possiveis = [
                "Aguardando Documentação",
                "Produzindo Peça",
                "Aguardando Revisão",
                "Devolvida para Correção",
                "Peça Aprovada",
                "Protocolado",
                "Acompanhando Movimentações"
            ]

            if sub == "Cadastrar Processo":
                st.header("📂 Cadastrar Novo Processo")
                with st.form("form_cad_meu_proc", clear_on_submit=True):
                    c_proc = st.text_input("Número do Processo / Identificação *")
                    c_cli = st.text_input("Nome do Cliente *")
                    c_desc = st.text_area("Descrição / Objeto da Peça")
                    c_resp = st.text_input("Responsável Inicial", value=name)
                    
                    if st.form_submit_button("Salvar Processo", type="primary"):
                        if not c_proc.strip() or not c_cli.strip():
                            st.error("Preencha o Número do Processo e o Cliente.")
                        else:
                            try:
                                supabase.table("meus_processos").insert({
                                    "numero_processo": c_proc.strip(),
                                    "cliente": c_cli.strip(),
                                    "cliente_nome": c_cli.strip(),
                                    "descricao": c_desc.strip(),
                                    "status": "Aguardando Documentação",
                                    "responsavel": c_resp.strip(),
                                    "solicitou_revisao": False
                                }).execute()
                                registrar_auditoria(username, "Cadastrar Processo", "Meus Processos", f"Proc: {c_proc}")
                                st.cache_data.clear()
                                confirmar_operacao("✅ Processo cadastrado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar processo: {e}")

            elif sub == "Consultar Meus Processos":
                st.header("📋 Gerenciamento de Processos")
                
                try:
                    if user_role == 'admin':
                        res_mp = carregar_dados("meus_processos")
                    else:
                        res_query = supabase.table("meus_processos").select("*").eq("responsavel", name).execute()
                        res_mp = res_query.data if res_query.data else []
                except Exception:
                    res_mp = []
                
                if not res_mp:
                    st.info("Nenhum processo cadastrado ou distribuído no momento.")
                else:
                    df_mp = pd.DataFrame(res_mp)
                    if 'data_atualizacao' in df_mp.columns:
                        df_mp['data_atualizacao'] = df_mp['data_atualizacao'].apply(formatar_data_br)
                    
                    if 'status' in df_mp.columns:
                        exibir_tabela(df_mp.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        exibir_tabela(df_mp, use_container_width=True, hide_index=True)

                    st.markdown("---")
                    st.subheader("⚡ Gerenciar ou Excluir Processo")

                    dict_ps = {f"ID: {p['id']} | Proc: {p['numero_processo']} - Cliente: {p['cliente']} (Resp: {p.get('responsavel', 'N/D')})": p for p in res_mp}
                    sel_proc_str = st.selectbox("Selecione o Processo:", list(dict_ps.keys()))
                    obj_proc = dict_ps[sel_proc_str]

                    if obj_proc.get('observacoes_revisao'):
                        st.warning(f"💬 **Feedback da Revisão (Admin):** {obj_proc.get('observacoes_revisao')}")

                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        idx_status = status_possiveis.index(obj_proc.get('status')) if obj_proc.get('status') in status_possiveis else 0
                        novo_status = st.selectbox("Alterar Status Atual:", status_possiveis, index=idx_status)
                    with col_g2:
                        nova_desc = st.text_area("Atualizar Observações / Andamento:", value=obj_proc.get('descricao', ''))

                    if novo_status == 'Protocolado' and obj_proc.get('status') != 'Protocolado':
                        st.info('Para protocolar, use o botão Registrar Protocolo abaixo. A pontuação será atribuída ao usuário conectado.')
                    if obj_proc.get('status') != 'Protocolado':
                        with st.expander('Registrar protocolo da ação', expanded=False):
                            st.caption(f'Protocolante: {name} ({username}). O registro vale um ponto e não pode ser duplicado.')
                            confirmar_protocolo = st.checkbox('Confirmo que eu efetivamente protocolei esta ação.', key=f'confirmar_protocolo_{obj_proc["id"]}')
                            if st.button('Registrar Protocolo', key=f'registrar_protocolo_{obj_proc["id"]}', disabled=not confirmar_protocolo, type='primary'):
                                try:
                                    if user_role != 'admin' and obj_proc.get('responsavel') != name:
                                        raise PermissionError('Você não tem acesso autorizado a este processo.')
                                    cliente_storage_servidor().rpc('dejure_confirmar_protocolo', {
                                        'p_processo_id': int(obj_proc['id']),
                                        'p_usuario_login': str(username),
                                        'p_usuario_nome': str(name)
                                    }).execute()
                                    registrar_auditoria(username, 'Protocolo confirmado', 'Meus Processos', f'Processo ID {obj_proc["id"]}; protocolante {name}')
                                    st.cache_data.clear()
                                    confirmar_operacao('Protocolo registrado e ponto atribuído ao seu usuário.')
                                    st.rerun()
                                except Exception as erro:
                                    st.error(f'Não foi possível registrar o protocolo: {erro}')

                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                            try:
                                if novo_status == 'Protocolado' and obj_proc.get('status') != 'Protocolado':
                                    raise ValueError('Use Registrar Protocolo para identificar corretamente quem protocolou.')
                                supabase.table("meus_processos").update({
                                    "status": novo_status,
                                    "descricao": nova_desc
                                }).eq("id", obj_proc['id']).execute()
                                registrar_auditoria(username, "Atualizar Processo", "Meus Processos", f"ID {obj_proc['id']} alterado para {novo_status}")
                                st.cache_data.clear()
                                confirmar_operacao("✅ Processo atualizado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")

                    with col_btn2:
                        st.caption('Envio de peças disponível na seção abaixo.')

                    st.markdown('---')
                    st.subheader('Documentos e Revisão')
                    try:
                        with st.expander('Documentos anexados', expanded=True):
                            revisao_mostrar_documentos(obj_proc['id'])
                        with st.expander('Histórico de revisões'):
                            revisao_mostrar_historico(obj_proc['id'])
                        em_revisao = obj_proc.get('status') == 'Aguardando Revisão' or obj_proc.get('solicitou_revisao')
                        if em_revisao:
                            st.info('Esta peça está aguardando a análise do administrador escolhido.')
                        else:
                            admins = revisao_administradores()
                            if not admins:
                                st.warning('Não há administradores cadastrados para receber a revisão.')
                            else:
                                with st.form(f"form_enviar_peca_{obj_proc['id']}"):
                                    st.caption('Anexe a petição e escolha o administrador responsável pela revisão.')
                                    anexo = st.file_uploader('Petição ou documento (PDF, DOC, DOCX; até 10 MB)',
                                        type=['pdf','doc','docx'], key=f"anexo_peca_{obj_proc['id']}")
                                    admin_escolhido = st.selectbox('Administrador destinatário', list(admins))
                                    obs_envio = st.text_area('Observações para o administrador')
                                    enviar_peca = st.form_submit_button('Enviar para Revisão', type='primary')
                                if enviar_peca:
                                    if anexo is None and not revisao_arquivos(obj_proc['id']):
                                        st.error('Anexe pelo menos um documento antes de enviar.')
                                    else:
                                        try:
                                            if anexo:
                                                revisao_upload(anexo, obj_proc['id'], 'envio')
                                            supabase.table('meus_processos').update({
                                                'status': 'Aguardando Revisão', 'solicitou_revisao': True
                                            }).eq('id', obj_proc['id']).execute()
                                            supabase.table('revisao_atribuicoes').upsert({
                                                'processo_id': obj_proc['id'],
                                                'admin_username': admins[admin_escolhido],
                                                'responsavel_username': username,
                                                'situacao': 'Aguardando Revisão'
                                            }, on_conflict='processo_id').execute()
                                            revisao_evento(obj_proc['id'], 'Enviada para revisão', admin_escolhido, obs_envio)
                                            registrar_auditoria(username, 'Enviar peça para revisão', 'Meus Processos', f"ID {obj_proc['id']} para {admin_escolhido}")
                                            st.cache_data.clear()
                                            confirmar_operacao('Peça encaminhada ao administrador escolhido.')
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f'Falha no envio: {e}')
                    except Exception as e:
                        st.error(f'Módulo de documentos indisponível. Confira a configuração SQL e Storage: {e}')

                    with col_btn3:
                        if user_role == 'admin':
                            if st.button("🗑️ Excluir Processo", type="primary", use_container_width=True):
                                try:
                                    supabase.table("meus_processos").delete().eq("id", obj_proc['id']).execute()
                                    registrar_auditoria(username, "Excluir Processo (Admin)", "Meus Processos", f"Processo ID {obj_proc['id']} ({obj_proc['numero_processo']}) do usuário {obj_proc.get('responsavel')} excluído.")
                                    st.cache_data.clear()
                                    confirmar_operacao("✅ Processo excluído permanentemente da base de dados!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir processo: {e}")

            elif sub == 'Armazenamento' and user_role == 'admin':
                revisao_painel_storage()
                revisao_central_armazenamento()

            elif sub == "Central de Revisões" and user_role == 'admin':
                st.header('Central de Revisões')
                revisao_painel_storage()
                st.caption('Administradores podem acompanhar e revisar todas as peças, mesmo as destinadas a outro administrador.')
                try:
                    filtro_revisoes = st.radio('Exibir', ['Minhas Revisões', 'Todas as Revisões'], horizontal=True)
                    consulta_rev = (supabase.table('revisao_atribuicoes').select('*')
                        .eq('situacao', 'Aguardando Revisão'))
                    if filtro_revisoes == 'Minhas Revisões':
                        consulta_rev = consulta_rev.eq('admin_username', username)
                    atribuicoes = consulta_rev.execute().data or []
                    if not atribuicoes:
                        st.info('Nenhuma peça aguardando sua revisão.')
                    else:
                        for atrib in atribuicoes:
                            proc_id = atrib['processo_id']
                            dados = supabase.table('meus_processos').select('*').eq('id', proc_id).execute().data or []
                            if not dados:
                                continue
                            proc = dados[0]
                            with st.expander(f"{proc.get('cliente')} — {proc.get('numero_processo')} (ID {proc_id})", expanded=True):
                                st.write(f"**Responsável:** {proc.get('responsavel')}")
                                revisao_mostrar_documentos(proc_id)
                                with st.form(f'form_revisar_{proc_id}'):
                                    obs = st.text_area('Observações da revisão', key=f'obs_revisao_{proc_id}')
                                    arquivo_corrigido = st.file_uploader('Arquivo revisado (opcional)',
                                        type=['pdf','doc','docx'], key=f'arquivo_revisado_{proc_id}')
                                    acao = st.radio('Decisão', ['Devolver para Correção', 'Aprovar Peça'],
                                        key=f'acao_revisao_{proc_id}')
                                    usuarios_destino = revisao_usuarios_ativos()
                                    nomes_destino = list(usuarios_destino)
                                    nome_atual = proc.get('responsavel', '')
                                    indice_destino = nomes_destino.index(nome_atual) if nome_atual in nomes_destino else 0
                                    destinatario = st.selectbox('Devolver para qual usuário?', nomes_destino,
                                        index=indice_destino, key=f'destino_rev_{proc_id}',
                                        disabled=(acao != 'Devolver para Correção'))
                                    confirmar = st.form_submit_button('Confirmar decisão', type='primary')
                                if confirmar:
                                    if acao == 'Devolver para Correção' and not obs.strip() and arquivo_corrigido is None:
                                        st.error('Inclua observações e/ou um arquivo revisado para devolver.')
                                    else:
                                        try:
                                            if arquivo_corrigido:
                                                revisao_upload(arquivo_corrigido, proc_id, 'revisado')
                                            novo_status = 'Devolvida para Correção' if acao == 'Devolver para Correção' else 'Peça Aprovada'
                                            alteracoes = {
                                                'status': novo_status, 'solicitou_revisao': False,
                                                'observacoes_revisao': obs
                                            }
                                            if acao == 'Devolver para Correção':
                                                # O novo destinatário passa a visualizar o processo em Meus Processos.
                                                alteracoes['responsavel'] = destinatario
                                            supabase.table('meus_processos').update(alteracoes).eq('id', proc_id).execute()
                                            dados_atribuicao = {'situacao': novo_status}
                                            if acao == 'Devolver para Correção':
                                                dados_atribuicao['responsavel_username'] = usuarios_destino[destinatario]
                                            supabase.table('revisao_atribuicoes').update(dados_atribuicao).eq('processo_id', proc_id).execute()
                                            destino_registro = destinatario if acao == 'Devolver para Correção' else proc.get('responsavel','')
                                            revisao_evento(proc_id, acao, destino_registro, obs)
                                            registrar_auditoria(username, acao, 'Meus Processos',
                                                f'Processo ID {proc_id}; destinatário: {destino_registro}; revisor: {username}')
                                            st.cache_data.clear()
                                            confirmar_operacao(f'{acao} registrada com sucesso.')
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f'Falha ao concluir revisão: {e}')
                                with st.expander('Histórico'):
                                    revisao_mostrar_historico(proc_id)
                except Exception as e:
                    st.error(f'Não foi possível abrir a caixa de revisões. Confira a configuração SQL: {e}')

        # --- MÓDULO EQUIPE ---
        elif menu_principal == "Equipe Dejure":
            if sub == "Nossa Equipe":
                st.header("🧑‍⚖️ Equipe Dejure")
                st.caption("Conheça os profissionais que fazem parte do nosso escritório.")
                
                usuarios_equipe = []
                for uname, uinfo in credentials["usernames"].items():
                    if uname != "master" and uinfo.get("name"):
                        u_copy = uinfo.copy()
                        u_copy["username"] = uname
                        usuarios_equipe.append(u_copy)
                
                if not usuarios_equipe:
                    st.info("Nenhum membro da equipe encontrado.")
                else:
                    # O ranking de protocolos é exibido exclusivamente na Página Inicial.
                    # A seção Equipe Dejure permanece dedicada à apresentação da equipe.
                    destaque = None
                    outros_brutos = [u for u in usuarios_equipe if not u.get("destaque_mes")]

                    ordem_cargos = {"admin": 1, "advogado": 2, "bacharel": 3, "estagiario": 4}
                    outros = sorted(
                        outros_brutos, 
                        key=lambda x: (ordem_cargos.get(x.get("role", "estagiario"), 5), str(x.get("name", "")).lower())
                    )

                    if destaque:
                        col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
                        with col_d2:
                            with st.container(border=True):
                                st.markdown("<h3 style='text-align: center; color: #0A0A0A; background-color: #D4AF37; margin-top: 0; padding: 10px; border-radius: 5px;'>🏆 DESTAQUE DO MÊS SELECIONADO 🏆</h3>", unsafe_allow_html=True)
                                
                                foto = destaque.get("foto_url")
                                if foto:
                                    st.markdown(f"""
                                        <div style='width: 100%; height: 320px; overflow: hidden; border-radius: 5px; margin-bottom: 15px;'>
                                            <img src='{foto}' style='width: 100%; height: 100%; object-fit: cover;'>
                                        </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='width: 100%; height: 320px; display: flex; align-items: center; justify-content: center; background-color: #1A1A1A; border-radius: 5px; margin-bottom: 15px;'><h1 style='margin:0; font-size: 5em;'>👤</h1></div>", unsafe_allow_html=True)
                                
                                st.markdown(f"<h3 style='text-align: center; color: #E0E0E0; margin-bottom: 5px; font-size: 1.25rem;'>{destaque.get('name')}</h3>", unsafe_allow_html=True)
                                
                                if destaque.get("oab"):
                                    st.markdown(f"<p style='text-align: center; font-size: 1.0em; margin-bottom: 0;'>OAB: {destaque.get('oab')}</p>", unsafe_allow_html=True)
                                
                                if destaque.get("data_nascimento"):
                                    try:
                                        dt_obj = datetime.strptime(destaque.get("data_nascimento"), "%Y-%m-%d")
                                        st.markdown(f"<p style='text-align: center; font-size: 1.0em; margin-bottom: 0; color: #D4AF37;'>🎂 Aniversário: {dt_obj.strftime('%d/%m')}</p>", unsafe_allow_html=True)
                                    except: pass
                                
                                if destaque.get("observacoes_pessoais"):
                                    st.write("")
                                    st.info(destaque.get("observacoes_pessoais"))
                        
                        st.markdown("---")

                    if outros:
                        if destaque:
                            st.subheader("👥 Demais Integrantes da Equipe")
                            
                        cols = st.columns(4)
                        for i, u in enumerate(outros):
                            col = cols[i % 4]
                            with col:
                                with st.container(border=True):
                                    foto = u.get("foto_url")
                                    if foto:
                                        st.markdown(f"""
                                            <div style='width: 100%; height: 220px; overflow: hidden; border-radius: 5px; margin-bottom: 10px;'>
                                                <img src='{foto}' style='width: 100%; height: 100%; object-fit: cover;'>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div style='width: 100%; height: 220px; display: flex; align-items: center; justify-content: center; background-color: #1A1A1A; border-radius: 5px; margin-bottom: 10px;'><h1 style='margin:0; font-size: 4em;'>👤</h1></div>", unsafe_allow_html=True)
                                    
                                    st.markdown(f"<p style='text-align: center; color: #D4AF37; margin-bottom: 5px; font-size: 0.95rem; font-weight: bold; word-wrap: break-word; overflow-wrap: break-word;'>{u.get('name')}</p>", unsafe_allow_html=True)
                                    
                                    if u.get("oab"):
                                        st.markdown(f"<p style='text-align: center; font-size: 0.85em; margin-bottom: 5px;'>OAB: {u.get('oab')}</p>", unsafe_allow_html=True)
                                        
                                    if u.get("data_nascimento"):
                                        try:
                                            dt_obj = datetime.strptime(u.get("data_nascimento"), "%Y-%m-%d")
                                            st.markdown(f"<p style='text-align: center; font-size: 0.85em; margin-bottom: 5px; color: #D4AF37;'>🎂 Aniversário: {dt_obj.strftime('%d/%m')}</p>", unsafe_allow_html=True)
                                        except: pass
                                    
                                    if u.get("observacoes_pessoais"):
                                        st.write("")
                                        with st.expander("Ver perfil detalhado"):
                                            st.write(u.get("observacoes_pessoais"))

        # --- MÓDULO SEGURANÇA ---
        elif menu_principal == "Segurança":
            if sub == "Meu Perfil":
                st.header("👤 Meu Perfil de Usuário")
                st.caption(f"Gerencie suas informações pessoais e envie sua foto de perfil ({username}).")
                
                col_pf1, col_pf2 = st.columns([1, 2])
                
                with col_pf1:
                    if user_info.get("foto_url"):
                        st.markdown(f"""
                            <div style='width: 100%; max-width: 300px; margin: 0 auto; height: 300px; border-radius: 10px; overflow: hidden; border: 2px solid #333;'>
                                <img src='{user_info.get("foto_url")}' style='width: 100%; height: 100%; object-fit: cover;'>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Sem foto cadastrada.")
                
                with col_pf2:
                    with st.form("form_meu_perfil"):
                        p_nome = st.text_input("Nome Completo", value=user_info.get("name", ""))
                        p_tel = st.text_input("Telefone de Contato", value=user_info.get("telefone", ""))
                        p_oab = st.text_input("Registro OAB / Identificação Profissional", value=user_info.get("oab", ""))
                        
                        dt_nasc_atual = user_info.get("data_nascimento")
                        if dt_nasc_atual:
                            try:
                                val_data = datetime.strptime(dt_nasc_atual, "%Y-%m-%d").date()
                            except:
                                val_data = None
                        else:
                            val_data = None
                        
                        p_nasc = st.date_input("Data de Nascimento", value=val_data, min_value=date(1920, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
                        
                        file_foto = st.file_uploader("Escolher Foto do Computador ou Celular (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
                        
                        p_obs = st.text_area("Observações Pessoais (Minicurrículo, Gostos, etc.)", value=user_info.get("observacoes_pessoais", ""))
                        
                        if st.form_submit_button("Salvar Alterações no Perfil", type="primary"):
                            if username == "master":
                                st.warning("A conta Master de emergência não altera perfil no banco.")
                            else:
                                try:
                                    foto_final = user_info.get("foto_url")
                                    if file_foto is not None:
                                        foto_final = converter_imagem_base64(file_foto)
                                    
                                    str_nasc = p_nasc.strftime("%Y-%m-%d") if p_nasc else None

                                    supabase.table("usuarios_sistema").update({
                                        "nome_completo": p_nome,
                                        "name": p_nome,
                                        "telefone": p_tel,
                                        "oab": p_oab,
                                        "data_nascimento": str_nasc,
                                        "foto_url": foto_final,
                                        "observacoes_pessoais": p_obs
                                    }).eq("username", username).execute()
                                    
                                    registrar_auditoria(username, "Atualizar Perfil", "Segurança", "Dados de perfil atualizados.")
                                    st.cache_data.clear()
                                    confirmar_operacao("✅ Perfil atualizado com sucesso!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar perfil no banco de dados: {e}")

            elif sub == "Alterar Senha":
                st.header("🔐 Alterar Minha Senha")
                st.caption(f"Usuário: **{username}**")
                with st.form("form_alt_senha"):
                    senha_atual = st.text_input("Senha atual", type="password")
                    nova_senha = st.text_input("Nova senha", type="password")
                    conf_senha = st.text_input("Confirmar nova senha", type="password")
                    enviar_senha = st.form_submit_button("Salvar nova senha", type="primary")

                if enviar_senha:
                    hash_atual = credentials["usernames"].get(username, {}).get("password", "")
                    try:
                        senha_confere = bool(hash_atual) and bcrypt.checkpw(
                            senha_atual.encode("utf-8"), hash_atual.encode("utf-8")
                        )
                    except (ValueError, TypeError):
                        senha_confere = False

                    if not senha_confere:
                        st.error("A senha atual está incorreta.")
                    elif len(nova_senha) < 12:
                        st.error("A nova senha deve ter pelo menos 12 caracteres.")
                    elif nova_senha != conf_senha:
                        st.error("A confirmação não corresponde à nova senha.")
                    elif nova_senha == senha_atual or nova_senha == "mudar123":
                        st.error("Escolha uma senha nova, diferente da anterior e da senha padrão.")
                    else:
                        novo_hash = gerar_hash(nova_senha)
                        try:
                            if username == "master":
                                # Salvar o master pela primeira vez ou atualizar registro existente.
                                consulta = supabase.table("usuarios_sistema").select("id").eq("username", "master").execute()
                                if consulta.data:
                                    resposta = supabase.table("usuarios_sistema").update({
                                        "senha_hash": novo_hash, "password": novo_hash,
                                        "nome_completo": "Administrador Master [SENHA_ALTERADA]"
                                    }).eq("username", "master").execute()
                                else:
                                    resposta = supabase.table("usuarios_sistema").insert({
                                        "username": "master", "nome_completo": "Administrador Master [SENHA_ALTERADA]",
                                        "name": "Administrador Master", "senha_hash": novo_hash,
                                        "password": novo_hash, "role": "admin", "trocar_senha": False
                                    }).execute()
                            else:
                                resposta = supabase.table("usuarios_sistema").update({
                                    "senha_hash": novo_hash, "password": novo_hash
                                }).eq("username", username).execute()
                            if not resposta.data:
                                raise RuntimeError("O banco não confirmou a gravação da senha.")
                            registrar_auditoria(username, "Alterar Senha", "Segurança", "Senha alterada pelo próprio usuário.")
                            st.cache_data.clear()
                            confirmar_operacao("✅ Senha alterada! Saia e entre novamente com a nova senha.")
                        except Exception as erro:
                            st.error(f"Não foi possível salvar a senha: {erro}")

            elif sub == "Cadastrar Novo Usuário" and user_role == 'admin':
                st.header("➕ Cadastrar Novo Usuário no Sistema")
                with st.form("form_cad_user", clear_on_submit=True):
                    new_user = st.text_input("Nome de Usuário (login sem espaços, ex: joao)")
                    new_name = st.text_input("Nome Completo")
                    new_pass = st.text_input("Senha Inicial", type="password")
                    
                    perfis_opcoes = {
                        "👑 Sócio / Administrador": "admin",
                        "⚖️ Advogado(a)": "advogado",
                        "📜 Bacharel(a)": "bacharel",
                        "🎓 Estagiário(a)": "estagiario"
                    }
                    sel_perfil_label = st.selectbox("Perfil de Acesso", list(perfis_opcoes.keys()))
                    new_role = perfis_opcoes[sel_perfil_label]
                    
                    if st.form_submit_button("Cadastrar Usuário"):
                        if not new_user or not new_name or not new_pass:
                            st.error("Preencha todos os campos obrigatórios.")
                        else:
                            senha_hash = gerar_hash(new_pass)
                            try:
                                supabase.table("usuarios_sistema").insert({
                                    "username": new_user.strip().lower(),
                                    "nome_completo": new_name,
                                    "name": new_name,
                                    "senha_hash": senha_hash,
                                    "password": senha_hash,
                                    "role": new_role,
                                    "trocar_senha": True
                                }).execute()
                                registrar_auditoria(username, "Cadastrar Usuário", "Segurança", f"Novo usuário criado: {new_user} ({new_role})")
                                st.cache_data.clear()
                                st.session_state['cad_user_sucesso'] = True
                            except Exception as e:
                                st.error(f"Erro ao cadastrar usuário: {e}")

                if st.session_state.get('cad_user_sucesso'):
                    confirmar_operacao("🎉 Usuário cadastrado com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Usuário", key="btn_novo_user", type="primary", use_container_width=True):
                            st.session_state['cad_user_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_user", use_container_width=True):
                            st.session_state['cad_user_sucesso'] = False
                            st.session_state['submenu_atual'] = "Gerenciar Usuários"
                            st.rerun()

            elif sub == "Reiniciar IDs de Teste" and username == "master" and user_role == "admin":
                st.header("Reiniciar numeração de IDs")
                st.warning("A numeração só poderá ser reiniciada se a tabela estiver totalmente vazia. "
                           "Isso NÃO apaga dados e NÃO renumera registros existentes. "
                           "Não execute em tabelas cujos IDs antigos ainda sejam usados em outros registros.")
                tabelas_ids = {
                    "Clientes": "clientes_cadastrados",
                    "Prospectados pendentes": "prospectados_pendentes",
                    "Distribuição de processos": "distribuicao_processos",
                    "Meus processos": "meus_processos",
                    "Honorários": "honorarios",
                    "Parcelas": "parcelas",
                    "Perícias": "pericias",
                    "Expedientes": "expedientes",
                    "Expedientes TRF": "expedientes_trf",
                    "Pendências": "pendencias",
                }
                rotulo_id = st.selectbox("Selecione a tabela", list(tabelas_ids), key="reset_ids_tabela")
                tabela_id = tabelas_ids[rotulo_id]
                st.info(f"Tabela selecionada: {tabela_id}. O próximo registro poderá receber ID 1 somente se a tabela estiver vazia.")
                with st.form("confirmacao_reset_ids", clear_on_submit=True):
                    ciente = st.checkbox("Confirmo que a tabela está vazia e que verifiquei referências a IDs antigos.")
                    confirmacao = st.text_input("Digite REINICIAR para confirmar")
                    executar = st.form_submit_button("Confirmar reinício da numeração", type="primary")
                if executar:
                    if not ciente or confirmacao.strip() != "REINICIAR":
                        st.error("Operação cancelada. Marque a confirmação e digite REINICIAR.")
                    else:
                        try:
                            resposta = cliente_storage_servidor().rpc(
                                "dejure_reiniciar_ids_tabela_vazia", {"nome_tabela": tabela_id}
                            ).execute()
                            if resposta.data is not True:
                                raise RuntimeError("O Supabase não confirmou a operação.")
                            registrar_auditoria(username, "Reiniciar sequência de ID", "Segurança",
                                               f"Tabela vazia: {tabela_id}")
                            confirmar_operacao(f"Numeração reiniciada na tabela {tabela_id}.")
                        except Exception as erro:
                            st.error(f"Não foi possível reiniciar a numeração: {erro}")

            elif sub == "Gerenciar Usuários" and user_role == 'admin':
                st.header("🛡️ Gerenciamento de Usuários Ativos")
                try:
                    res_users = supabase.table("usuarios_sistema").select("*").execute()
                    if res_users.data:
                        df_u = pd.DataFrame(res_users.data)
                        colunas_visiveis = [c for c in ['id', 'username', 'nome_completo', 'name', 'role', 'trocar_senha', 'telefone', 'oab'] if c in df_u.columns]
                        
                        if 'data_nascimento' in df_u.columns:
                            df_u['data_nascimento'] = df_u['data_nascimento'].apply(formatar_data_br)

                        exibir_tabela(df_u[colunas_visiveis], use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        st.subheader("🗑️ Excluir Usuário (Para resetar)")
                        udict = {f"{u['username']} (ID: {u['id']})": u['id'] for u in res_users.data}
                        if udict:
                            sel_del = st.selectbox("Selecione o usuário:", list(udict.keys()))
                            if st.checkbox("Confirmo a exclusão permanente deste usuário.") and st.button("EXCLUIR USUÁRIO SELECIONADO", type="primary"):
                                uid_del = udict[sel_del]
                                supabase.table("usuarios_sistema").delete().eq("id", uid_del).execute()
                                registrar_auditoria(username, "Excluir Usuário", "Segurança", f"Usuário ID {uid_del} excluído.")
                                st.cache_data.clear()
                                confirmar_operacao("Usuário excluído com sucesso!")
                                st.rerun()
                except Exception as e:
                    st.error(f"Erro ao carregar usuários: {e}")

        # --- MÓDULO PAGAMENTOS ---
        elif menu_principal == "Pagamentos":
            if sub == "Cadastrar Contrato":
                st.header("📝 Novo Contrato e Parcelamento")
                cli_db = carregar_dados("clientes_cadastrados")
                nomes = [c['nome'] for c in cli_db]
                # Controles dinâmicos fora do formulário: Streamlit atualiza a cada alteração.
                modo_parcelamento = st.radio(
                    "Forma de parcelamento do saldo:",
                    ["Parcelas iguais (automático)", "Parcelas personalizadas (valores diferentes)"],
                    key="modo_parcelamento_honorarios",
                    horizontal=True
                )
                personalizado = modo_parcelamento == "Parcelas personalizadas (valores diferentes)"
                npar = int(st.number_input(
                    "Quantidade de parcelas do saldo", min_value=1, max_value=36,
                    value=3, step=1, key="hon_quantidade_parcelas_dinamica"
                ))

                # Dados e valores personalizados também ficam fora do st.form.
                # Isso evita que o formulário congele a renderização dos campos.
                cli_op = st.selectbox("Cliente:", ["Outro"] + nomes, key="hon_cliente_opcao") if nomes else "Outro"
                cli = st.text_input("Nome", key="hon_cliente_nome") if cli_op == "Outro" else cli_op
                serv = st.text_input("Serviço", key="hon_servico")
                vtot = campo_moeda_br("Valor Total do Contrato (R$)", "hon_valor_total")
                v_entrada = campo_moeda_br("Valor de Entrada (R$)", "hon_valor_entrada")
                saldo_preview = round(float(vtot or 0) - float(v_entrada or 0), 2)
                valores_parcelas = []

                if personalizado:
                    st.subheader(f"🧾 Preenchimento das {npar} parcelas personalizadas")
                    st.info(f"Quantidade selecionada: {npar} parcelas. Saldo a distribuir: {formatar_moeda_br(max(0.0, saldo_preview))}.")
                    # Cada campo aparece em sua própria linha, sem o limite visual de 3 colunas.
                    for i in range(npar):
                        valor_i = campo_moeda_br(
                            f"Parcela {i + 1} de {npar} — valor (R$)",
                            f"hon_parcela_personalizada_{i}"
                        )
                        valores_parcelas.append(round(float(valor_i or 0), 2))
                    soma_preview = round(sum(valores_parcelas), 2)
                    diferenca_preview = round(saldo_preview - soma_preview, 2)
                    st.write(f"**Campos exibidos: {len(valores_parcelas)} de {npar}**")
                    st.write(f"**Total das parcelas:** {formatar_moeda_br(soma_preview)}")
                    if diferenca_preview > 0:
                        st.warning(f"Faltam {formatar_moeda_br(diferenca_preview)} para completar o saldo.")
                    elif diferenca_preview < 0:
                        st.error(f"As parcelas ultrapassam o saldo em {formatar_moeda_br(abs(diferenca_preview))}.")
                    else:
                        st.success("A soma das parcelas corresponde ao saldo restante.")
                else:
                    st.caption(f"O saldo será dividido automaticamente em {npar} parcelas.")

                with st.form("fc_hon", clear_on_submit=False):
                    dt1 = st.date_input("Vencimento da 1ª Parcela (ou Entrada)", datetime.now())

                    col_b_h1, col_b_h2 = st.columns(2)
                    with col_b_h1:
                        salvar_hon = st.form_submit_button("Gerar Contrato e Parcelas", type="primary", use_container_width=True)
                    with col_b_h2:
                        voltar_hon = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_hon:
                        if vtot is None or v_entrada is None or (personalizado and any(campo_valor_invalido(st.session_state.get(f"hon_parcela_personalizada_{i}", "0")) for i in range(npar))):
                            st.error("Corrija os campos monetários antes de salvar.")
                            st.stop()
                        soma_parcelas = round(sum(valores_parcelas), 2) if modo_parcelamento == "Parcelas personalizadas (valores diferentes)" else round(saldo_preview, 2)
                        if not cli or not serv or vtot <= 0:
                            st.error("Preencha o cliente, o serviço e um valor total válido.")
                        elif v_entrada > vtot:
                            st.error("O valor da entrada não pode ser maior que o valor total do contrato.")
                        elif personalizado and round(soma_parcelas, 2) != round(saldo_preview, 2):
                            st.error(f"A soma das parcelas ({formatar_moeda_br(soma_parcelas)}) deve ser igual ao saldo restante ({formatar_moeda_br(saldo_preview)}). Ajuste os valores antes de gerar o contrato.")
                        else:
                            res = supabase.table("honorarios").insert({"cliente": cli, "servico": serv, "valor_total": float(vtot)}).execute()
                            if res.data:
                                h_id = res.data[0]['id']
                                saldo_restante = round(float(vtot) - float(v_entrada), 2)

                                if v_entrada > 0:
                                    supabase.table("parcelas").insert({
                                        "honorario_id": h_id,
                                        "numero_parcela": "Entrada",
                                        "valor": round(float(v_entrada), 2),
                                        "vencimento": dt1.strftime("%Y-%m-%d"),
                                        "status": "Pendente"
                                    }).execute()
                                    data_primeira_parcela = dt1 + relativedelta(months=1)
                                else:
                                    data_primeira_parcela = dt1

                                if saldo_restante > 0:
                                    if modo_parcelamento == "Parcelas iguais (automático)":
                                        valores_gerados = [round(saldo_restante / int(npar), 2) for _ in range(int(npar))]
                                        # Ajusta centavos na última parcela para que a soma seja exatamente o saldo.
                                        valores_gerados[-1] = round(saldo_restante - sum(valores_gerados[:-1]), 2)
                                    else:
                                        valores_gerados = valores_parcelas

                                    total_parcelas = len(valores_gerados)
                                    for i, valor_parcela in enumerate(valores_gerados):
                                        venc = (data_primeira_parcela + relativedelta(months=i)).strftime("%Y-%m-%d")
                                        supabase.table("parcelas").insert({
                                            "honorario_id": h_id,
                                            "numero_parcela": f"{i+1}/{total_parcelas}",
                                            "valor": round(float(valor_parcela), 2),
                                            "vencimento": venc,
                                            "status": "Pendente"
                                        }).execute()

                                registrar_auditoria(username, "Cadastrar Contrato com Entrada", "Pagamentos", f"Cliente: {cli} - Total: {formatar_moeda_br(vtot)} - Parcelamento: {modo_parcelamento}")
                                st.cache_data.clear()
                                st.session_state['cad_hon_sucesso'] = True
                                confirmar_operacao('Contrato e parcelas gerados com sucesso!')
                                st.rerun()

            elif sub == "RPV / Retroativos" and user_role == 'admin':
                st.header("🏛️ Gerenciar honorários vinculados a RPV / retroativos")
                st.info("Cadastre o percentual dos honorários sobre a RPV, mesmo sem conhecer seu valor. Honorários fixos (por exemplo, R$ 9.000,00) devem ser cadastrados separadamente em Contratos/Parcelamentos. Quando a RPV for liberada, informe seu valor bruto para calcular os honorários e gerar a parcela pendente.")
                try:
                    cli_rpv = cliente_storage_servidor()
                    # A lista nao depende do status das parcelas: contratos quitados continuam disponiveis.
                    # Unimos clientes cadastrados, titulares de contratos de honorarios e RPVs anteriores.
                    nomes_clientes_rpv = set()
                    for tabela_origem, coluna_nome in (
                        ('clientes_cadastrados', 'nome'),
                        ('honorarios', 'cliente'),
                    ):
                        for item in carregar_dados(tabela_origem):
                            nome_item = str(item.get(coluna_nome) or '').strip()
                            if nome_item:
                                nomes_clientes_rpv.add(nome_item)
                    inicio_nomes_rpv = 0
                    while True:
                        lote_nomes_rpv = (cli_rpv.table('dejure_rpv_recebiveis')
                                          .select('cliente').range(inicio_nomes_rpv, inicio_nomes_rpv + 999)
                                          .execute().data or [])
                        for item in lote_nomes_rpv:
                            nome_item = str(item.get('cliente') or '').strip()
                            if nome_item:
                                nomes_clientes_rpv.add(nome_item)
                        if len(lote_nomes_rpv) < 1000:
                            break
                        inicio_nomes_rpv += 1000
                    clientes_rpv = sorted(nomes_clientes_rpv, key=lambda nome: nome.casefold())
                    st.caption('Selecione um cliente que ja possui cadastro ou contrato de honorarios. Mesmo com todas as parcelas pagas, ele continua disponivel para cadastrar a RPV.')
                    with st.form('rpv_novo_registro'):
                        cliente_rpv = st.selectbox('Cliente', ['Selecione um cliente'] + clientes_rpv)
                        servico_rpv = st.text_input('Serviço / referência', value='Aposentadoria — RPV retroativa')
                        percentual_rpv = st.number_input('Percentual dos honorários sobre a RPV (%)', min_value=0.01, max_value=100.0, value=30.0, step=0.5, format='%.2f')
                        st.caption('O valor da RPV não precisa ser conhecido agora. Exemplo: contrato fixo de R$ 9.000,00 + 30% da RPV.')
                        numero_rpv = st.text_input('Número da RPV / processo (opcional)')
                        obs_rpv = st.text_area('Observações (opcional)')
                        salvar_rpv = st.form_submit_button('Cadastrar RPV sem vencimento', type='primary')
                    if salvar_rpv:
                        if cliente_rpv == 'Selecione um cliente' or not servico_rpv.strip():
                            st.error('Selecione um cliente e informe o serviço.')
                        else:
                            cli_rpv.table('dejure_rpv_recebiveis').insert({
                                'cliente': cliente_rpv, 'servico': servico_rpv.strip(),
                                'valor': None, 'percentual_rpv': float(percentual_rpv), 'numero_rpv': numero_rpv.strip(),
                                'observacoes': obs_rpv.strip(), 'status': 'Aguardando liberação',
                                'criado_por': username
                            }).execute()
                            registrar_auditoria(username, 'Cadastrar RPV', 'Pagamentos', f'Cliente: {cliente_rpv}; percentual sobre RPV: {percentual_rpv}%; valor desconhecido; sem vencimento')
                            st.cache_data.clear()
                            st.success('RPV cadastrada e incluída na Página Inicial.')
                            st.rerun()
                    registros_rpv = []
                    inicio_rpv = 0
                    while True:
                        lote = cli_rpv.table('dejure_rpv_recebiveis').select('*').order('id', desc=True).range(inicio_rpv, inicio_rpv + 999).execute().data or []
                        registros_rpv.extend(lote)
                        if len(lote) < 1000: break
                        inicio_rpv += 1000
                    st.subheader('RPVs cadastradas')
                    if registros_rpv:
                        st.dataframe(pd.DataFrame(registros_rpv)[[c for c in ['id','cliente','servico','numero_rpv','percentual_rpv','valor_rpv_bruto','valor','status','data_liberacao','parcela_id'] if c in registros_rpv[0]]], use_container_width=True, hide_index=True)
                        aguardando_rpv = [r for r in registros_rpv if r.get('status') == 'Aguardando liberação']
                        if aguardando_rpv:
                            opcoes_rpv = {f"#{r['id']} — {r['cliente']} — {r.get('percentual_rpv') or 0}% da RPV":r for r in aguardando_rpv}
                            escolhido_rpv = st.selectbox('Selecionar RPV para informar liberação', list(opcoes_rpv), key='rpv_escolher')
                            registro_rpv = opcoes_rpv[escolhido_rpv]
                            data_liberacao_rpv = st.date_input('Data da liberação', value=date.today(), key='rpv_data_liberacao')
                            valor_bruto_liberado = st.number_input('Valor bruto efetivamente liberado da RPV (R$)', min_value=0.0, value=0.0, step=100.0, format='%.2f', key='rpv_bruto_liberado')
                            from decimal import Decimal, ROUND_HALF_UP
                            honorarios_calculados = (Decimal(str(valor_bruto_liberado)) * Decimal(str(registro_rpv.get('percentual_rpv') or 0)) / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                            st.info(f'Honorários a receber pela RPV: {formatar_moeda_br(float(honorarios_calculados))}')
                            confirmar_rpv = st.checkbox('Confirmo que a RPV foi liberada e desejo gerar uma parcela PENDENTE para baixa normal.', key='rpv_confirmar')
                            if st.button('Registrar liberação e gerar parcela', type='primary', disabled=(not confirmar_rpv or honorarios_calculados <= 0)):
                                # Evita duplicação se uma tentativa anterior criou a parcela e falhou depois.
                                referencia = f"RPV-{registro_rpv['id']}"
                                ja_criada = cli_rpv.table('parcelas').select('id').eq('numero_parcela', referencia).limit(1).execute().data or []
                                if ja_criada:
                                    st.error('Já existe uma parcela gerada para esta RPV. Procure a administração para conciliar o registro antes de tentar novamente.')
                                else:
                                    contrato = cli_rpv.table('honorarios').insert({
                                        'cliente': registro_rpv['cliente'], 'servico': registro_rpv['servico'],
                                        'valor_total': float(honorarios_calculados)
                                    }).execute().data
                                    if not contrato:
                                        raise RuntimeError('Não foi possível criar o contrato de honorários.')
                                    parcela = cli_rpv.table('parcelas').insert({
                                        'honorario_id': contrato[0]['id'], 'numero_parcela': referencia,
                                        'valor': float(honorarios_calculados),
                                        'vencimento': data_liberacao_rpv.isoformat(), 'status': 'Pendente'
                                    }).execute().data
                                    if not parcela:
                                        raise RuntimeError('Contrato criado, mas a parcela não foi gerada. Verifique os registros antes de repetir.')
                                    cli_rpv.table('dejure_rpv_recebiveis').update({
                                        'status':'Liberada — aguardando baixa',
                                        'data_liberacao':data_liberacao_rpv.isoformat(),
                                        'valor_rpv_bruto':float(valor_bruto_liberado), 'valor':float(honorarios_calculados),
                                        'honorario_id':contrato[0]['id'], 'parcela_id':parcela[0]['id']
                                    }).eq('id', registro_rpv['id']).eq('status','Aguardando liberação').execute()
                                    registrar_auditoria(username, 'Liberação de RPV', 'Pagamentos', f"RPV ID {registro_rpv['id']}; parcela ID {parcela[0]['id']}; cliente {registro_rpv['cliente']}")
                                    st.cache_data.clear()
                                    st.success('RPV liberada. Parcela criada como Pendente. Use Pagamentos → Baixar Parcela quando o valor for efetivamente recebido.')
                                    st.rerun()
                    else:
                        st.info('Nenhuma RPV cadastrada.')
                except Exception as erro_rpv:
                    st.error(f'Não foi possível operar o controle de RPV: {erro_rpv}. Confira se o SQL de instalação foi executado.')

            elif sub == "Cadastrar Parcelamento em Andamento" and user_role == 'admin':
                st.header("📚 Cadastrar Parcelamento em Andamento")
                st.info("Registre o contrato completo, incluindo parcelas já recebidas fora do DEJURE. As parcelas históricas ficam como **Pago**, sem gerar novos repasses ou comissões. Somente as parcelas pendentes poderão passar pela baixa financeira normal.")
                cli_db_hist = carregar_dados("clientes_cadastrados")
                nomes_hist = sorted(set(c.get("nome", "") for c in cli_db_hist if c.get("nome")))
                cliente_hist_op = st.selectbox("Cliente", ["Outro"] + nomes_hist, key="hist_cliente_op")
                cliente_hist = st.text_input("Nome do cliente", key="hist_cliente_nome") if cliente_hist_op == "Outro" else cliente_hist_op
                servico_hist = st.text_input("Serviço / descrição do contrato", key="hist_servico")
                col_hist_1, col_hist_2, col_hist_3 = st.columns(3)
                with col_hist_1:
                    qtd_hist = int(st.number_input("Total de parcelas", min_value=1, max_value=120, value=10, step=1, key="hist_qtd"))
                with col_hist_2:
                    pagas_hist = int(st.number_input("Parcelas já recebidas", min_value=0, max_value=qtd_hist, value=0, step=1, key="hist_pagas"))
                with col_hist_3:
                    valor_total_hist = campo_moeda_br("Valor total negociado (R$)", "hist_total")
                st.markdown("#### 💰 Entrada do cliente")
                tem_entrada_hist = st.checkbox("O cliente deu uma entrada", key="hist_tem_entrada")
                entrada_hist = campo_moeda_br("Valor da entrada já recebida (R$)", "hist_entrada") if tem_entrada_hist else 0.0
                data_entrada_hist = st.date_input("Data do recebimento da entrada", value=date.today(), key="hist_data_entrada") if tem_entrada_hist else None
                st.caption("A entrada é um recebimento histórico, não gera repasses e será descontada do total antes de calcular as parcelas.")
                modo_hist = st.radio("Valores das parcelas", ["Parcelas iguais", "Informar valor de cada parcela"], horizontal=True, key="hist_modo")
                primeira_data_hist = st.date_input("Vencimento original da primeira parcela", value=date.today(), key="hist_primeiro_venc")
                st.caption("Os vencimentos seguintes são calculados mensalmente. Marque individualmente apenas as parcelas realmente recebidas; parcelas futuras não são pagas automaticamente.")
                if valor_total_hist is not None and valor_total_hist > 0:
                    centavos_hist = int((Decimal(str(valor_total_hist)) * 100).quantize(Decimal("1")))
                else:
                    centavos_hist = 0
                centavos_entrada_hist = int((Decimal(str(entrada_hist or 0)) * 100).quantize(Decimal("1")))
                saldo_parcelado_centavos_hist = centavos_hist - centavos_entrada_hist
                base_hist, sobra_hist = divmod(max(0, saldo_parcelado_centavos_hist), qtd_hist)
                st.write(f"**Entrada histórica:** {formatar_moeda_br(entrada_hist or 0)}  |  **Saldo parcelado:** {formatar_moeda_br(max(0, saldo_parcelado_centavos_hist) / 100)}")
                if centavos_entrada_hist >= centavos_hist and centavos_hist > 0:
                    st.warning("A entrada precisa ser menor que o valor total negociado, pois há parcelas a cadastrar.")
                recebida_flags_hist = []
                valores_hist = []
                datas_receb_hist = []
                incluir_balanco_hist = []
                competencia_balanco_hist = []
                for i_hist in range(qtd_hist):
                    valor_padrao_hist = (base_hist + (sobra_hist if i_hist == qtd_hist - 1 else 0)) / 100
                    venc_hist = primeira_data_hist + relativedelta(months=i_hist)
                    with st.expander(f"Parcela {i_hist+1}/{qtd_hist} — vencimento {venc_hist.strftime('%d/%m/%Y')}", expanded=(i_hist < 2)):
                        if modo_hist == "Informar valor de cada parcela":
                            v_hist = campo_moeda_br(f"Valor da parcela {i_hist+1} (R$)", f"hist_valor_{i_hist}")
                        else:
                            v_hist = valor_padrao_hist
                            st.write(f"Valor: **{formatar_moeda_br(v_hist)}**")
                        valores_hist.append(v_hist)
                        recebida_hist = st.checkbox(f"Parcela {i_hist+1} já foi efetivamente recebida", value=(i_hist < pagas_hist), key=f"hist_recebida_{i_hist}")
                        recebida_flags_hist.append(recebida_hist)
                        if recebida_hist:
                            data_rec = st.date_input(f"Data em que a parcela {i_hist+1} foi efetivamente recebida", value=venc_hist if venc_hist <= date.today() else date.today(), key=f"hist_data_rec_{i_hist}")
                            datas_receb_hist.append(data_rec)
                            incluir_balanco_hist.append(st.checkbox(f'Incluir parcela {i_hist+1} no Balanço Financeiro', value=False, key=f'hist_incluir_bal_{i_hist}'))
                            mes_hist = st.date_input(f'Mês em que a parcela {i_hist+1} deve constar no Balanço', value=data_rec.replace(day=1), key=f'hist_competencia_{i_hist}') if incluir_balanco_hist[-1] else data_rec.replace(day=1)
                            competencia_balanco_hist.append(mes_hist.strftime('%Y-%m'))
                        else:
                            datas_receb_hist.append(None)
                            incluir_balanco_hist.append(False)
                            competencia_balanco_hist.append(None)
                pagas_hist = sum(recebida_flags_hist)
                if any(recebida_flags_hist[i] and (primeira_data_hist + relativedelta(months=i)) > date.today() for i in range(qtd_hist)):
                    st.info("Há parcela com vencimento futuro marcada como recebida. Isso é permitido apenas se o pagamento realmente foi antecipado.")
                soma_hist = sum(Decimal(str(v or 0)) for v in valores_hist)
                st.markdown(f"**Recebido historicamente (entrada + parcelas):** {formatar_moeda_br(float(entrada_hist or 0) + sum(float(v or 0) for i, v in enumerate(valores_hist) if recebida_flags_hist[i]))}  |  **A receber:** {formatar_moeda_br(sum(float(v or 0) for i, v in enumerate(valores_hist) if not recebida_flags_hist[i]))}")
                if modo_hist == "Informar valor de cada parcela" and abs(soma_hist - Decimal(str(valor_total_hist or 0)) + Decimal(str(entrada_hist or 0))) > Decimal("0.009"):
                    st.warning("A soma das parcelas deve corresponder ao total negociado menos a entrada.")
                with st.form("form_confirmar_parcelamento_historico"):
                    confirm_hist = st.checkbox("Confirmo que as parcelas já recebidas são históricas e NÃO devem gerar novos repasses aos sócios.")
                    salvar_hist = st.form_submit_button("Salvar contrato e histórico de parcelas", type="primary", use_container_width=True)
                if salvar_hist:
                    if not confirm_hist:
                        st.error("Confirme a regra dos recebimentos históricos.")
                    elif not cliente_hist or not cliente_hist.strip() or not servico_hist.strip():
                        st.error("Informe o cliente e o serviço.")
                    elif valor_total_hist is None or valor_total_hist <= 0 or centavos_entrada_hist < 0 or centavos_entrada_hist >= centavos_hist or any(v is None or v <= 0 for v in valores_hist):
                        st.error("Informe valores positivos e válidos.")
                    elif abs(soma_hist - Decimal(str(valor_total_hist)) + Decimal(str(entrada_hist or 0))) > Decimal("0.009"):
                        st.error("A soma das parcelas deve ser igual ao valor do contrato menos a entrada.")
                    elif data_entrada_hist is not None and data_entrada_hist > date.today():
                        st.error("A data da entrada histórica não pode estar no futuro.")
                    elif any(d > date.today() for d in datas_receb_hist if d is not None):
                        st.error("A data de recebimento histórico não pode estar no futuro.")
                    else:
                        novo_h_id = None
                        try:
                            db_hist = cliente_storage_servidor()
                            contrato_hist = db_hist.table("honorarios").insert({"cliente": cliente_hist.strip(), "servico": servico_hist.strip(), "valor_total": float(valor_total_hist)}).execute()
                            if not contrato_hist.data:
                                raise RuntimeError("Não foi possível criar o contrato.")
                            novo_h_id = contrato_hist.data[0]["id"]
                            linhas_hist = []
                            for i_hist, valor_hist in enumerate(valores_hist):
                                linhas_hist.append({"honorario_id": novo_h_id, "numero_parcela": f"{i_hist+1}/{qtd_hist}", "valor": float(Decimal(str(valor_hist)).quantize(Decimal("0.01"))), "vencimento": (primeira_data_hist + relativedelta(months=i_hist)).isoformat(), "status": "Pago" if recebida_flags_hist[i_hist] else "Pendente"})
                            # A tabela parcelas é a mesma do fluxo normal: o Balanço considera somente pendentes na projeção.
                            for idx_linha, linha_hist in enumerate(linhas_hist):
                                retorno_par = db_hist.table("parcelas").insert(linha_hist).execute()
                                if not retorno_par.data:
                                    raise RuntimeError('A parcela não foi confirmada no banco.')
                                if recebida_flags_hist[idx_linha]:
                                    dejure_salvar_historico_balanco(db_hist, username, retorno_par.data[0]['id'],
                                        incluir_balanco_hist[idx_linha], linha_hist['valor'],
                                        datas_receb_hist[idx_linha].isoformat(), 'Cadastro inicial do parcelamento histórico', competencia_balanco_hist[idx_linha])
                            # Registro informativo separado dos repasses: módulo "Pagamentos", nunca "Repasses".
                            info_hist = {"tipo": "parcelamento_historico_sem_repasses", "honorario_id": novo_h_id, "cliente": cliente_hist.strip(), "total_parcelas": qtd_hist, "parcelas_ja_pagas": pagas_hist, "indices_parcelas_pagas": [i+1 for i, flag in enumerate(recebida_flags_hist) if flag], "entrada_historica": {"valor": float(entrada_hist or 0), "data_recebimento": data_entrada_hist.isoformat() if data_entrada_hist else None}, "recebimentos_historicos": [{"parcela": i+1, "data_recebimento": d.isoformat(), "valor": float(valores_hist[i])} for i, d in enumerate(datas_receb_hist) if d is not None]}
                            try:
                                registrar_auditoria(username, "Importar Parcelamento Histórico (sem repasses)", "Pagamentos", json.dumps(info_hist, ensure_ascii=False))
                            except Exception:
                                st.warning("Contrato salvo, mas não foi possível registrar os detalhes das datas no log de auditoria.")
                            st.cache_data.clear()
                            confirmar_operacao(f"Contrato cadastrado: {pagas_hist} parcela(s) histórica(s), {sum(incluir_balanco_hist)} incluída(s) no balanço, {qtd_hist-pagas_hist} pendente(s). Nenhum novo repasse foi gerado.")
                        except Exception as erro_hist:
                            # Evita contratos parciais se houver falha de conexão durante a gravação.
                            if novo_h_id is not None:
                                try:
                                    db_hist.table("parcelas").delete().eq("honorario_id", novo_h_id).execute()
                                    db_hist.table("honorarios").delete().eq("id", novo_h_id).execute()
                                except Exception:
                                    st.error(f"A gravação foi interrompida e pode ter restado um contrato parcial (ID {novo_h_id}). Verifique antes de tentar novamente.")
                            st.error(f"Não foi possível concluir o cadastro: {erro_hist}")

            elif sub == "Ver Parcelas":
                st.header("📋 Visualizar Parcelas")
                res_h = carregar_dados("honorarios")
                if res_h:
                    cdict = {f"{h['cliente']} — {h['servico']} (Total: {formatar_moeda_br(h.get('valor_total', 0))})": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(cdict.keys()))
                    res_p = supabase.table("parcelas").select("*").eq("honorario_id", cdict[sel]).execute()
                    if res_p.data: 
                        df_p = pd.DataFrame(res_p.data)
                        if 'vencimento' in df_p.columns:
                            df_p['vencimento'] = df_p['vencimento'].apply(formatar_data_br)
                        if 'valor' in df_p.columns:
                            df_p['valor'] = df_p['valor'].apply(formatar_moeda_br)
                        referencia_parcelas = st.date_input('Mês de referência para parcelas a receber',
                                                             value=date.today().replace(day=1), key='referencia_parcelas_receber')
                        df_p['Situação visual'] = [dejure_status_parcela_visual(p.get('status'), p.get('vencimento'), referencia_parcelas, 'receber') for p in res_p.data]
                        exibir_tabela(df_p.style.map(dejure_cor_status_visual, subset=['Situação visual']),
                                     use_container_width=True, hide_index=True)
                        st.caption('🟢 Recebida: parcela paga pelo cliente. 🔴 A receber no mês: parcela ainda não recebida com vencimento no mês selecionado. 🟡 A receber: demais parcelas pendentes.')
                    else: st.info("Sem parcelas.")
                else: st.info("Sem contratos.")

            elif sub == "Baixar Parcela" and user_role == 'admin':
                st.header("💰 Baixar Parcela e Calcular Rateio com Rateio dos Colaboradores")
                
                res_h = carregar_dados("honorarios")
                if not res_h:
                    st.info("Nenhum contrato cadastrado.")
                else:
                    cdict_h = {f"{h['cliente']} — {h['servico']}": h for h in res_h}
                    sel_contrato_str = st.selectbox("1. Selecione o Contrato:", list(cdict_h.keys()))
                    obj_contrato = cdict_h[sel_contrato_str]
                    val_total_contrato = float(obj_contrato.get('valor_total', 0.0))
                    
                    cli_nome_contrato = obj_contrato.get('cliente', '')
                    prosp_automatico_cli = "Nenhum / Sem Prospectador"
                    
                    try:
                        res_cli_info = supabase.table("clientes_cadastrados").select("indicado_por").eq("nome", cli_nome_contrato).execute()
                        if res_cli_info.data:
                            indic_cli = res_cli_info.data[0].get("indicado_por", "")
                            if str(indic_cli).startswith("Prospectador Externo:"):
                                prosp_automatico_cli = indic_cli
                    except Exception:
                        pass

                    res_p = supabase.table("parcelas").select("*").eq("honorario_id", obj_contrato['id']).eq("status", "Pendente").execute()
                    if not res_p.data:
                        st.success("✅ Este contrato não possui parcelas pendentes.")
                    else:
                        parcelas_pendentes = {f"{dejure_status_parcela_visual(p.get('status'), p.get('vencimento'), date.today(), 'receber')} | Parcela: {p['numero_parcela']} — {formatar_moeda_br(p['valor'])} (Venc: {formatar_data_br(p['vencimento'])})": p for p in res_p.data}
                        sel_parcela_str = st.selectbox("2. Selecione a Parcela a Baixar:", list(parcelas_pendentes.keys()))
                        parcela_obj = parcelas_pendentes[sel_parcela_str]
                        valor_bruto = float(parcela_obj['valor'])
                        
                        st.markdown("---")
                        
                        lista_usuarios = []
                        for u in credentials['usernames'].values():
                            nome_u = u.get('name', '')
                            papel_u = u.get('role', 'estagiario')
                            if nome_u:
                                lista_usuarios.append({"nome": nome_u, "papel": papel_u})
                        
                        nomes_opcoes = [u['nome'] for u in lista_usuarios]
                        is_entrada = (parcela_obj['numero_parcela'] == "Entrada")
                        
                        opcoes_prosp_baixa = ["Nenhum / Sem Prospectador", "Prospectador Externo"] + nomes_opcoes
                        if prosp_automatico_cli.startswith("Prospectador Externo:") and prosp_automatico_cli not in opcoes_prosp_baixa:
                            opcoes_prosp_baixa.insert(2, prosp_automatico_cli)

                        idx_prosp_init = 0
                        if prosp_automatico_cli in opcoes_prosp_baixa:
                            idx_prosp_init = opcoes_prosp_baixa.index(prosp_automatico_cli)

                        if is_entrada:
                            st.subheader("⚙️ Regra de Entrada (Com / Sem Prospecção)")
                            st.info("Entrada: descontar prospectador e operador; aplicar fundo de 5% sobre o saldo somente se o valor bruto negociado do contrato for igual ou superior a R$ 1.000,00; dividir o restante entre os sócios (60/40).")
                            
                            col_r1, col_r2 = st.columns(2)
                            with col_r1:
                                prosp_name = st.selectbox("👤 Prospectador:", opcoes_prosp_baixa, index=idx_prosp_init)
                            with col_r2:
                                resp_name = st.selectbox("⚖️ Operador (Trabalhou no Processo):", nomes_opcoes)
                            
                            val_prosp_input = 0.0
                            if prosp_name not in ["Nenhum / Sem Prospectador", resp_name]:
                                val_prosp_input = min(campo_moeda_br("💵 Valor de Captação deliberado (R$):", "pag_cap_entrada") or 0.0, valor_bruto)
                            elif prosp_name == resp_name:
                                st.warning("📌 **Acúmulo Detectado:** O Prospectador e Operador são os mesmos. A comissão incidirá direto no bruto.")

                            resp_role = "estagiario"
                            for u in lista_usuarios:
                                if u['nome'] == resp_name:
                                    resp_role = u['papel']
                                    break
                                    
                        else:
                            st.subheader("⚙️ Parcela recebida — repasse opcional a colaborador")
                            st.info("Não há desconto automático de 5% nas parcelas. Sem repasse a colaborador, a parcela inteira é dividida entre os dois sócios.")
                            incluir_colaborador = st.checkbox("Destinar parte desta parcela a um colaborador?", value=False, key=f"repasse_colab_{parcela_obj['id']}")
                            colaborador_parcela = ""
                            valor_colaborador_parcela = 0.0
                            if incluir_colaborador:
                                if nomes_opcoes:
                                    colaborador_parcela = st.selectbox("Colaborador que receberá o valor", nomes_opcoes, key=f"colab_parcela_{parcela_obj['id']}")
                                    valor_colaborador_parcela = campo_moeda_br("Valor destinado ao colaborador (R$)", f"valor_colab_parcela_{parcela_obj['id']}") or 0.0
                                else:
                                    st.error("Não há colaboradores cadastrados para selecionar.")
                            prosp_name = "Nenhum / Sem Prospectador"
                            resp_name = colaborador_parcela or "Não aplicável"
                            resp_role = "Não aplicável"
                            val_prosp_input = 0.0

                        colaboradores_fundo = [u['nome'] for u in lista_usuarios if u['papel'] in ['advogado', 'bacharel', 'estagiario'] and u['nome'] != resp_name]

                        val_prospectador = 0.0
                        val_operador = 0.0
                        fundo_colab = 0.0
                        val_leonidas = 0.0
                        val_nelson = 0.0
                        
                        if is_entrada:
                            saldo = valor_bruto
                            regra_aplicada = "Entrada"
                            
                            if prosp_name == resp_name:
                                regra_aplicada = "Entrada (Acúmulo)"
                                taxa = 0.60 if resp_role in ['admin', 'advogado'] else 0.40
                                val_operador = round(valor_bruto * taxa, 2)
                                val_prospectador = val_operador
                                saldo -= val_operador
                                
                                if val_total_contrato >= 1000.0 and saldo > 0:
                                    fundo_colab = round(saldo * 0.05, 2)
                                    saldo -= fundo_colab
                                    
                                val_leonidas = round(saldo * 0.60, 2)
                                val_nelson = round(saldo * 0.40, 2)
                                
                            else:
                                if prosp_name != "Nenhum / Sem Prospectador":
                                    val_prospectador = round(val_prosp_input, 2)
                                else:
                                    val_prospectador = 0.0
                                
                                saldo -= val_prospectador
                                
                                taxa_op = 0.25 if resp_role in ['admin', 'advogado'] else (0.15 if resp_role == 'bacharel' else 0.10)
                                val_operador = round(saldo * taxa_op, 2)
                                saldo -= val_operador
                                
                                if val_total_contrato >= 1000.0 and saldo > 0:
                                    fundo_colab = round(saldo * 0.05, 2)
                                    saldo -= fundo_colab
                                    
                                val_leonidas = round(saldo * 0.60, 2)
                                val_nelson = round(saldo * 0.40, 2)
                        else:
                            regra_aplicada = "Parcela: repasse livre a colaborador" if incluir_colaborador else "Parcela: sócios 60/40"
                            val_operador = round(valor_colaborador_parcela, 2) if incluir_colaborador else 0.0
                            saldo_remanescente_parcela = round(valor_bruto - val_operador, 2)
                            if saldo_remanescente_parcela >= 0:
                                val_leonidas = round(saldo_remanescente_parcela * 0.60, 2)
                                val_nelson = round(saldo_remanescente_parcela - val_leonidas, 2)
                            else:
                                val_leonidas = 0.0
                                val_nelson = 0.0
                            fundo_colab = 0.0

                        qtd_colab = len(colaboradores_fundo)
                        cota_individual_fundo = round(fundo_colab / qtd_colab, 2) if qtd_colab > 0 else 0.0
                        detalhes_rateio_colab = {c: cota_individual_fundo for c in colaboradores_fundo} if is_entrada and fundo_colab > 0 else {}

                        val_prosp_efetivo = 0.0 if "Acúmulo" in regra_aplicada else (val_prospectador if is_entrada and prosp_name != "Nenhum / Sem Prospectador" else 0.0)
                        soma_distribuida = round(val_prosp_efetivo + val_operador + fundo_colab + val_leonidas + val_nelson, 2)
                        diferenca = round(valor_bruto - soma_distribuida, 2)

                        valor_colab_invalido = (not is_entrada and incluir_colaborador and (not colaborador_parcela or val_operador <= 0 or val_operador > valor_bruto))
                        if diferenca != 0 and not valor_colab_invalido:
                            val_leonidas = round(val_leonidas + diferenca, 2)
                            soma_distribuida = round(val_prosp_efetivo + val_operador + fundo_colab + val_leonidas + val_nelson, 2)
                            diferenca = round(valor_bruto - soma_distribuida, 2)

                        st.markdown("#### 🧮 Prova Real do Rateio (Validação Entrada vs Saída)")
                        col_pr1, col_pr2, col_pr3 = st.columns(3)
                        col_pr1.metric("Recurso Bruto da Parcela", formatar_moeda_br(valor_bruto))
                        col_pr2.metric("Soma Total Distribuída", formatar_moeda_br(soma_distribuida))
                        
                        if diferenca == 0:
                            col_pr3.success("✅ **PROVA OK!**\nSoma 100% idêntica ao valor de entrada.")
                        else:
                            col_pr3.error(f"⚠️ **DIVERGÊNCIA:** Δ {formatar_moeda_br(diferenca)}")

                        with st.expander("🔍 Detalhamento dos Valores da Prova Real", expanded=True):
                            det_cols = st.columns(5)
                            det_cols[0].write(f"**Prospectador:**\n{formatar_moeda_br(val_prosp_efetivo)}")
                            det_cols[1].write(f"**{'Operador' if is_entrada else 'Colaborador'} ({resp_name}):**\n{formatar_moeda_br(val_operador)}")
                            det_cols[2].write(f"**Fundo 5% (somente entrada):**\n{formatar_moeda_br(fundo_colab)}")
                            det_cols[3].write(f"**Leônidas:**\n{formatar_moeda_br(val_leonidas)}")
                            det_cols[4].write(f"**Nelson:**\n{formatar_moeda_br(val_nelson)}")

                        if is_entrada and fundo_colab > 0:
                            st.markdown("##### 👥 Divisão do fundo de 5% entre colaboradores elegíveis")
                        if is_entrada and fundo_colab > 0 and colaboradores_fundo:
                            cols_colab = st.columns(min(len(colaboradores_fundo), 4))
                            for idx, c_nome in enumerate(colaboradores_fundo):
                                cols_colab[idx % 4].info(f"**{c_nome}**\nRecebe: {formatar_moeda_br(cota_individual_fundo)}")
                        elif is_entrada and fundo_colab > 0:
                            st.warning("⚠️ Nenhum colaborador elegível cadastrado para o fundo.")

                        if valor_colab_invalido:
                            st.error("Informe um colaborador e um valor maior que zero e não superior ao valor da parcela.")
                        if st.button("Confirmar Baixa e Gerar Repasse", type="primary", disabled=(valor_colab_invalido or diferenca != 0)):
                            repasse_dict = {
                                "parcela_id": parcela_obj['id'],
                                "contrato": sel_contrato_str,
                                "regra": regra_aplicada,
                                "valor_bruto": round(valor_bruto, 2),
                                "prospectador": prosp_name,
                                "valor_prospectador": round(val_prospectador, 2),
                                "operador": resp_name,
                                "papel_operador": resp_role,
                                "valor_operador": round(val_operador, 2),
                                "colaborador_parcela": colaborador_parcela if not is_entrada else None,
                                "valor_colaborador_parcela": round(val_operador, 2) if not is_entrada else 0.0,
                                "fundo_colab": round(fundo_colab, 2),
                                "rateio_colaboradores": detalhes_rateio_colab,
                                "cota_por_colaborador": cota_individual_fundo,
                                "leonidas": round(val_leonidas, 2),
                                "nelson": round(val_nelson, 2),
                                "soma_distribuida": round(soma_distribuida, 2),
                                "prova_real_ok": True if diferenca == 0 else False,
                                "data_baixa": date.today().strftime("%Y-%m-%d")
                            }
                            json_repasse = json.dumps(repasse_dict, ensure_ascii=False)
                            
                            try:
                                supabase.table("parcelas").update({"status": "Pago"}).eq("id", parcela_obj['id']).execute()
                                dejure_registrar_evento_repasse(supabase, username, "Baixa e Rateio", repasse_dict)
                                st.cache_data.clear()
                                confirmar_operacao("✅ Parcela baixada e repasse validado com sucesso! Consulte o Extrato de Repasses.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao processar baixa: {e}")

            elif sub == "Extrato de Repasses" and user_role == 'admin':
                st.header("📊 Extrato Geral de Repasses (Fee Splitting)")
                st.caption("Visão financeira completa sobre a divisão de honorários das parcelas baixadas com Prova Real Auditada.")
                
                try:
                    res_rep = type("Resultado", (), {"data": dejure_logs_repasses_ativos(supabase)})()
                    if not res_rep.data:
                        st.info("Nenhum repasse registrado ainda.")
                    else:
                        linhas = []
                        total_bruto_acum = 0.0
                        total_dist_acum = 0.0
                        provas_validas = 0
                        total_registros = 0

                        for log in res_rep.data:
                            try:
                                r = json.loads(log['detalhes'])
                                val_bruto = float(r.get('valor_bruto', 0))
                                val_prosp_exib = float(r.get('valor_prospectador', 0))
                                val_op_exib = float(r.get('valor_operador', 0))
                                fundo_exib = float(r.get('fundo_colab', 0))
                                leo_exib = float(r.get('leonidas', 0))
                                nel_exib = float(r.get('nelson', 0))
                                
                                rateio_colab = r.get('rateio_colaboradores', {})
                                txt_rateio_colab = ", ".join([f"{k}: {formatar_moeda_br(v)}" for k, v in rateio_colab.items()]) if rateio_colab else "-"

                                if "Acúmulo" in r.get('regra', ''):
                                    val_prosp_efetivo = 0.0
                                else:
                                    val_prosp_efetivo = val_prosp_exib if r.get('prospectador') not in ["Nenhum / Sem Prospectador", "N/A", ""] else 0.0

                                soma_dist = round(val_prosp_efetivo + val_op_exib + fundo_exib + leo_exib + nel_exib, 2)
                                dif = round(val_bruto - soma_dist, 2)
                                is_ok = (abs(dif) < 0.01)

                                total_registros += 1
                                if is_ok: provas_validas += 1
                                total_bruto_acum += val_bruto
                                total_dist_acum += soma_dist

                                linhas.append({
                                    "Data": datetime.strptime(log['data_hora'][:10], "%Y-%m-%d").strftime("%d/%m/%Y"),
                                    "Tipo Regra": r.get('regra', 'N/D'),
                                    "Contrato": r.get('contrato', '').split(' — ')[0],
                                    "Valor Bruto": formatar_moeda_br(val_bruto),
                                    "Prospectador": r.get('prospectador', ''),
                                    "Val. Prospector": formatar_moeda_br(val_prosp_exib if 'Acúmulo' not in r.get('regra','') else 0.0),
                                    "Operador": r.get('operador', ''),
                                    "Val. Operador": formatar_moeda_br(val_op_exib),
                                    "Fundo Colab. (5%)": formatar_moeda_br(fundo_exib),
                                    "Rateio Colaboradores (Não Operadores)": txt_rateio_colab,
                                    "Leônidas": formatar_moeda_br(leo_exib),
                                    "Nelson": formatar_moeda_br(nel_exib),
                                    "Soma Distribuída": formatar_moeda_br(soma_dist),
                                    "Prova Real": "✅ 100% Batido" if is_ok else f"⚠️ Δ {formatar_moeda_br(dif)}"
                                })
                            except Exception:
                                pass
                        
                        if linhas:
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Total Entrado (Bruto)", formatar_moeda_br(total_bruto_acum))
                            m2.metric("Total Repassado (Soma)", formatar_moeda_br(total_dist_acum))
                            pct_audit = (provas_validas / total_registros * 100) if total_registros > 0 else 100
                            m3.metric("Auditoria Prova Real", f"{pct_audit:.0f}% OK ({provas_validas}/{total_registros})")

                            st.markdown("---")
                            df_rep = pd.DataFrame(linhas)
                            exibir_tabela(df_rep, use_container_width=True, hide_index=True)
                            
                            st.download_button(
                                label="📥 Exportar Extrato Com Prova Real (CSV)",
                                data=df_rep.to_csv(index=False).encode('utf-8'),
                                file_name=f"extrato_repasses_provareal_{date.today()}.csv",
                                mime="text/csv",
                                type="primary"
                            )
                except Exception as e:
                    st.error(f"Erro ao carregar extratos: {e}")

            elif sub == "Relatório por Período" and user_role == 'admin':
                st.header("📅 Relatório Financeiro de Pagamentos por Período")
                st.caption("Gere balancetes e relatórios detalhados de entradas e divisões de honorários.")
                
                hoje_dt = date.today()
                primeiro_dia_mes = hoje_dt.replace(day=1)

                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    dt_inicio = st.date_input("Data Inicial", value=primeiro_dia_mes)
                with col_f2:
                    dt_fim = st.date_input("Data Final", value=hoje_dt)
                with col_f3:
                    lista_usuarios_rel = ["Todos os Colaboradores / Sócios"]
                    for u in credentials['usernames'].values():
                        n_user = u.get('name', '')
                        if n_user and n_user not in lista_usuarios_rel:
                            lista_usuarios_rel.append(n_user)
                    filtro_pessoa = st.selectbox("Filtrar por Pessoa:", lista_usuarios_rel)

                if dt_inicio > dt_fim:
                    st.error("A Data Inicial não pode ser posterior à Data Final.")
                else:
                    try:
                        res_rep = type("Resultado", (), {"data": dejure_logs_repasses_ativos(supabase)})()
                        if not res_rep.data:
                            st.info("Nenhum registro de repasse encontrado no banco de dados.")
                        else:
                            linhas_relatorio = []
                            sum_bruto = 0.0
                            sum_prosp = 0.0
                            sum_op = 0.0
                            sum_fundo = 0.0
                            sum_leonidas = 0.0
                            sum_nelson = 0.0
                            sum_distribuido = 0.0
                            count_provas_ok = 0
                            totais_por_colaborador = {}

                            for log in res_rep.data:
                                try:
                                    r = json.loads(log['detalhes'])
                                    dt_baixa_str = r.get('data_baixa', log['data_hora'][:10])
                                    dt_baixa_obj = datetime.strptime(dt_baixa_str, "%Y-%m-%d").date()

                                    if dt_inicio <= dt_baixa_obj <= dt_fim:
                                        prosp = r.get('prospectador', '')
                                        op = r.get('operador', '')
                                        rateio_colab = r.get('rateio_colaboradores', {})
                                        
                                        if filtro_pessoa != "Todos os Colaboradores / Sócios":
                                            if filtro_pessoa not in [prosp, op, "Leônidas", "Nelson"] and filtro_pessoa not in rateio_colab:
                                                continue

                                        v_bruto = float(r.get('valor_bruto', 0))
                                        v_prosp_raw = float(r.get('valor_prospectador', 0))
                                        v_op = float(r.get('valor_operador', 0))
                                        v_fundo = float(r.get('fundo_colab', 0))
                                        v_leo = float(r.get('leonidas', 0))
                                        v_nel = float(r.get('nelson', 0))

                                        v_prosp_efetivo = 0.0 if "Acúmulo" in r.get('regra', '') else (v_prosp_raw if prosp not in ["Nenhum / Sem Prospectador", "N/A", ""] else 0.0)
                                        soma_d = round(v_prosp_efetivo + v_op + v_fundo + v_leo + v_nel, 2)
                                        is_ok = abs(v_bruto - soma_d) < 0.01

                                        if is_ok: count_provas_ok += 1
                                        sum_bruto += v_bruto
                                        sum_prosp += v_prosp_efetivo
                                        sum_op += v_op
                                        sum_fundo += v_fundo
                                        sum_leonidas += v_leo
                                        sum_nelson += v_nel
                                        sum_distribuido += soma_d

                                        for colab_name, colab_val in rateio_colab.items():
                                            totais_por_colaborador[colab_name] = totais_por_colaborador.get(colab_name, 0.0) + float(colab_val)

                                        txt_colab_det = ", ".join([f"{k}: {formatar_moeda_br(v)}" for k, v in rateio_colab.items()]) if rateio_colab else "-"

                                        linhas_relatorio.append({
                                            "Data Baixa": dt_baixa_obj.strftime("%d/%m/%Y"),
                                            "Contrato / Cliente": r.get('contrato', '').split(' — ')[0],
                                            "Regra Aplicada": r.get('regra', 'N/D'),
                                            "Valor Bruto": formatar_moeda_br(v_bruto),
                                            "Prospectador": f"{prosp} ({formatar_moeda_br(v_prosp_efetivo)})" if v_prosp_efetivo > 0 else (prosp if prosp else "-"),
                                            "Operador": f"{op} ({formatar_moeda_br(v_op)})",
                                            "Fundo Colab. (5%)": formatar_moeda_br(v_fundo),
                                            "Rateio Individual Colaboradores": txt_colab_det,
                                            "Leônidas": formatar_moeda_br(v_leo),
                                            "Nelson": formatar_moeda_br(v_nel),
                                            "Total Distribuído": formatar_moeda_br(soma_d),
                                            "Prova Real": "✅ 100% Batido" if is_ok else "⚠️ Divergente"
                                        })
                                except Exception:
                                    pass

                            st.markdown("---")
                            st.subheader(f"📊 Resumo Financeiro do Período ({dt_inicio.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')})")
                            
                            c_rel1, c_rel2, c_rel3, c_rel4 = st.columns(4)
                            c_rel1.metric("Faturamento Bruto Entrado", formatar_moeda_br(sum_bruto))
                            c_rel2.metric("Total Sócios (60/40)", formatar_moeda_br(sum_leonidas + sum_nelson))
                            c_rel3.metric("Total Operadores & Prospectores", formatar_moeda_br(sum_op + sum_prosp))
                            c_rel4.metric("Fundo Colaboradores (5%)", formatar_moeda_br(sum_fundo))

                            with st.expander("👑 Divisão Detalhada dos Sócios e Fundo de Colaboradores no Período", expanded=True):
                                c_s1, c_s2, c_s3 = st.columns(3)
                                c_s1.metric("Leônidas", formatar_moeda_br(sum_leonidas))
                                c_s2.metric("Nelson", formatar_moeda_br(sum_nelson))
                                total_rel_regs = len(linhas_relatorio)
                                pct_rel_ok = (count_provas_ok / total_rel_regs * 100) if total_rel_regs > 0 else 100
                                c_s3.metric("Validação de Prova Real", f"{pct_rel_ok:.0f}% OK ({count_provas_ok}/{total_rel_regs})")

                                if totais_por_colaborador:
                                    st.markdown("---")
                                    st.markdown("##### 💵 Acumulado Recebido do Fundo (5%) Por Colaborador no Período:")
                                    cols_tot_c = st.columns(min(len(totais_por_colaborador), 4))
                                    for idx, (c_name, c_tot) in enumerate(totais_por_colaborador.items()):
                                        cols_tot_c[idx % 4].metric(c_name, formatar_moeda_br(c_tot))

                            st.markdown("---")
                            st.subheader("📝 Lista Detalhada dos Pagamentos Processados")
                            
                            if linhas_relatorio:
                                df_rel = pd.DataFrame(linhas_relatorio)
                                exibir_tabela(df_rel, use_container_width=True, hide_index=True)
                                
                                nome_arquivo = f"relatorio_pagamentos_{dt_inicio.strftime('%Y%m%d')}_a_{dt_fim.strftime('%Y%m%d')}.csv"
                                st.download_button(
                                    label="📥 Baixar Relatório Completo (CSV)",
                                    data=df_rel.to_csv(index=False).encode('utf-8'),
                                    file_name=nome_arquivo,
                                    mime="text/csv",
                                    type="primary"
                                )
                            else:
                                st.warning("Nenhum registro de pagamento encontrado para os filtros selecionados.")
                    except Exception as e:
                        st.error(f"Erro ao carregar relatório por período: {e}")

            elif sub == "Editar Contrato":
                st.header("✏️ Editar Contrato")
                res_h = carregar_dados("honorarios")
                if res_h:
                    hdict = {f"ID: {h['id']} | {h['cliente']}": h for h in res_h}
                    sel = st.selectbox("Contrato:", list(hdict.keys()))
                    obj = hdict[sel]
                    with st.form("fe_hon"):
                        ec, es, ev = st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Serviço", value=obj.get('servico','')), campo_moeda_br("Valor", f"ed_hon_valor_{obj['id']}", inicial=float(obj.get('valor_total') or 0), em_formulario=True)
                        
                        col_eh1, col_eh2 = st.columns(2)
                        with col_eh1:
                            salvar_ed_hon = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_eh2:
                            voltar_ed_hon = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_hon:
                            if ev is None:
                                st.error("Corrija o valor antes de salvar.")
                                st.stop()
                            supabase.table("honorarios").update({"cliente": ec, "servico": es, "valor_total": float(ev)}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Contrato", "Pagamentos", f"ID: {obj['id']}")
                            st.cache_data.clear(); confirmar_operacao("Atualizado!"); st.rerun()
                        if voltar_ed_hon:
                            st.session_state['submenu_atual'] = "Ver Parcelas"
                            st.rerun()

            elif sub == "Excluir Contrato" and user_role == 'admin':
                st.header("🗑️ Excluir Contrato")
                res_h = carregar_dados("honorarios")
                if res_h:
                    hdict = {f"{h['cliente']} — {h['servico']}": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(hdict.keys()))
                    if st.checkbox("Confirmo exclusão do contrato selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("honorarios").delete().eq("id", hdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Contrato", "Pagamentos", f"ID: {hdict[sel]}")
                        st.cache_data.clear(); confirmar_operacao("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os contratos e parcelas.")
                    if st.checkbox("Confirmo a exclusão de TODOS os contratos e parcelas cadastradas."):
                        if st.button("🔥 EXCLUIR TODOS OS CONTRATOS E PARCELAS", type="primary"):
                            supabase.table("parcelas").delete().neq("id", 0).execute()
                            supabase.table("honorarios").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS CONTRATOS", "Pagamentos", "Exclusão em massa.")
                            st.cache_data.clear(); confirmar_operacao("Todos os contratos e parcelas foram excluídos!"); st.rerun()
                else: st.info("Sem contratos cadastrados.")

        # --- MÓDULO PERÍCIAS ---
        elif menu_principal == "Perícias":
            if sub == "Cadastrar Perícia":
                st.header("🔬 Nova Perícia")
                with st.form("fc_per", clear_on_submit=True):
                    cpf = st.text_input("CPF")
                    nome = st.text_input("Nome *")
                    local_pm = st.text_input("Local PM")
                    dt_pm = st.date_input("Data PM", datetime.now())
                    hora_pm = st.text_input("Hora PM (ex: 14:30:00)")
                    local_ps = st.text_input("Local PS")
                    dt_ps = st.date_input("Data PS", datetime.now())
                    hora_ps = st.text_input("Hora PS (ex: 15:30:00)")
                    senha_inss = st.text_input("Senha INSS")
                    elaborador = st.text_input("Elaborador")
                    
                    col_bp1, col_bp2 = st.columns(2)
                    with col_bp1:
                        salvar_per = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_bp2:
                        voltar_per = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_per:
                        if not nome:
                            st.error("O campo Nome é obrigatório.")
                        else:
                            h_pm_fmt = formatar_hora_br(hora_pm) if hora_pm.strip() else None
                            h_ps_fmt = formatar_hora_br(hora_ps) if hora_ps.strip() else None

                            supabase.table("pericias").insert({
                                "cpf": cpf,
                                "nome": nome,
                                "local_pm": local_pm,
                                "data_pm": dt_pm.strftime("%Y-%m-%d"),
                                "hora_pm": h_pm_fmt,
                                "local_ps": local_ps,
                                "data_ps": dt_ps.strftime("%Y-%m-%d"),
                                "hora_ps": h_ps_fmt,
                                "senha_inss": senha_inss,
                                "elaborador": elaborador,
                                "status": "Pendente"
                            }).execute()
                            registrar_auditoria(username, "Cadastrar Perícia", "Perícias", f"Nome: {nome}")
                            st.cache_data.clear()
                            st.session_state['cad_per_sucesso'] = True
                            st.rerun()
                    if voltar_per:
                        st.session_state['submenu_atual'] = "Ver Perícias"
                        st.rerun()

                if st.session_state.get('cad_per_sucesso'):
                    confirmar_operacao("🎉 Perícia cadastrada com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Nova Perícia", key="btn_novo_per", type="primary", use_container_width=True):
                            st.session_state['cad_per_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_per", use_container_width=True):
                            st.session_state['cad_per_sucesso'] = False
                            st.session_state['submenu_atual'] = "Ver Perícias"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Perícias via Excel")
                st.caption("O arquivo deve conter as colunas: cpf, nome, local_pm, data_pm, hora_pm, local_ps, data_ps, hora_ps, senha_inss, elaborador, status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_per")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("pericias", file_up)

            elif sub == "Ver Perícias":
                st.header("📋 Lista de Perícias")
                res = carregar_dados("pericias")
                if res: 
                    df_per = pd.DataFrame(res)
                    
                    if 'data_pm' in df_per.columns: df_per['data_pm'] = df_per['data_pm'].apply(formatar_data_br)
                    if 'data_ps' in df_per.columns: df_per['data_ps'] = df_per['data_ps'].apply(formatar_data_br)
                    if 'hora_pm' in df_per.columns: df_per['hora_pm'] = df_per['hora_pm'].apply(formatar_hora_br)
                    if 'hora_ps' in df_per.columns: df_per['hora_ps'] = df_per['hora_ps'].apply(formatar_hora_br)

                    ordem_desejada = ['cpf', 'nome', 'local_pm', 'data_pm', 'hora_pm', 'local_ps', 'data_ps', 'hora_ps', 'senha_inss', 'elaborador', 'status']
                    colunas_existentes = [c for c in ordem_desejada if c in df_per.columns]
                    outras_colunas = [c for c in df_per.columns if c not in ordem_desejada and c != 'id']
                    df_per = df_per[['id'] + colunas_existentes + outras_colunas]

                    if 'status' in df_per.columns:
                        exibir_tabela(df_per.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        exibir_tabela(df_per, use_container_width=True, hide_index=True)
                else: 
                    st.info("Sem perícias cadastradas.")

            elif sub == "Editar Perícia":
                st.header("✏️ Editar Perícia")
                res = carregar_dados("pericias")
                if res:
                    pdict = {f"ID: {i['id']} | {i.get('nome', 'Sem Nome')}": i for i in res}
                    sel = st.selectbox("Perícia:", list(pdict.keys()))
                    obj = pdict[sel]
                    with st.form("fe_per"):
                        ecpf = st.text_input("CPF", value=obj.get('cpf',''))
                        enome = st.text_input("Nome", value=obj.get('nome',''))
                        elocal_pm = st.text_input("Local PM", value=obj.get('local_pm',''))
                        
                        dt_pm_val = datetime.now().date()
                        if obj.get('data_pm'):
                            try:
                                dt_pm_val = datetime.strptime(obj.get('data_pm'), "%Y-%m-%d").date()
                            except:
                                pass
                        edt_pm = st.date_input("Data PM", value=dt_pm_val)
                        ehora_pm = st.text_input("Hora PM (HH:MM:SS)", value=obj.get('hora_pm',''))

                        elocal_ps = st.text_input("Local PS", value=obj.get('local_ps',''))
                        dt_ps_val = datetime.now().date()
                        if obj.get('data_ps'):
                            try:
                                dt_ps_val = datetime.strptime(obj.get('data_ps'), "%Y-%m-%d").date()
                            except:
                                pass
                        edt_ps = st.date_input("Data PS", value=dt_ps_val)
                        ehora_ps = st.text_input("Hora PS (HH:MM:SS)", value=obj.get('hora_ps',''))

                        esenhainss = st.text_input("Senha INSS", value=obj.get('senha_inss',''))
                        eelab = st.text_input("Elaborador", value=obj.get('elaborador',''))
                        est_op = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluído", "Pago"], index=["Pendente", "Em Andamento", "Concluído", "Pago"].index(obj.get('status', 'Pendente')) if obj.get('status', 'Pendente') in ["Pendente", "Em Andamento", "Concluído", "Pago"] else 0)
                        
                        col_ep1, col_ep2 = st.columns(2)
                        with col_ep1:
                            salvar_ed_per = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)
                        with col_ep2:
                            voltar_ed_per = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_per:
                            supabase.table("pericias").update({
                                "cpf": ecpf,
                                "nome": enome,
                                "local_pm": elocal_pm,
                                "data_pm": edt_pm.strftime("%Y-%m-%d"),
                                "hora_pm": formatar_hora_br(ehora_pm) if ehora_pm.strip() else None,
                                "local_ps": elocal_ps,
                                "data_ps": edt_ps.strftime("%Y-%m-%d"),
                                "hora_ps": formatar_hora_br(ehora_ps) if ehora_ps.strip() else None,
                                "senha_inss": esenhainss,
                                "elaborador": eelab,
                                "status": est_op
                            }).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Perícia", "Perícias", f"ID: {obj['id']}")
                            st.cache_data.clear()
                            confirmar_operacao("Perícia atualizada com sucesso!")
                            st.rerun()
                        if voltar_ed_per:
                            st.session_state['submenu_atual'] = "Ver Perícias"
                            st.rerun()
                else: 
                    st.info("Sem perícias para editar.")

            elif sub == "Excluir Perícia" and user_role == 'admin':
                st.header("🗑️ Excluir Perícia")
                res = carregar_dados("pericias")
                if res:
                    pdict = {f"ID: {i['id']} | {i.get('nome', 'Sem Nome')}": i['id'] for i in res}
                    sel = st.selectbox("Perícia:", list(pdict.keys()))
                    if st.checkbox("Confirmo exclusão da perícia selecionada.") and st.button("EXCLUIR SELECIONADA", type="primary"):
                        supabase.table("pericias").delete().eq("id", pdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Perícia", "Perícias", f"ID: {pdict[sel]}")
                        st.cache_data.clear()
                        confirmar_operacao("Perícia excluída!")
                        st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODAS as perícias.")
                    if st.checkbox("Confirmo a exclusão de TODAS as perícias cadastradas."):
                        if st.button("🔥 EXCLUIR TODAS AS PERÍCIAS", type="primary"):
                            supabase.table("pericias").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODAS AS PERÍCIAS", "Perícias", "Exclusão em massa.")
                            st.cache_data.clear()
                            confirmar_operacao("Todas as perícias foram excluídas!")
                            st.rerun()
                else: 
                    st.info("Sem perícias cadastradas.")

        # --- MÓDULO EXPEDIENTES ---
        elif menu_principal == "Expedientes":
            if sub == "Cadastrar Expediente":
                st.header("📂 Novo Expediente")
                with st.form("fc_exp", clear_on_submit=True):
                    proc, cli, desc, dt, resp = st.text_input("Processo"), st.text_input("Cliente"), st.text_input("Descrição"), st.date_input("Prazo", datetime.now()), st.text_input("Responsável")
                    
                    col_bx1, col_bx2 = st.columns(2)
                    with col_bx1:
                        salvar_exp = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_bx2:
                        voltar_exp = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_exp:
                        supabase.table("expedientes").insert({"numero_processo": proc, "cliente": cli, "descricao": desc, "data_manifestacao": dt.strftime("%Y-%m-%d"), "responsavel": resp, "status": "Pendente"}).execute()
                        registrar_auditoria(username, "Cadastrar Expediente", "Expedientes", f"Processo: {proc}")
                        st.cache_data.clear()
                        st.session_state['cad_exp_sucesso'] = True
                        st.rerun()
                    if voltar_exp:
                        st.session_state['submenu_atual'] = "Consultar Expedientes"
                        st.rerun()

                if st.session_state.get('cad_exp_sucesso'):
                    confirmar_operacao("🎉 Expediente cadastrado com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Expediente", key="btn_novo_exp", type="primary", use_container_width=True):
                            st.session_state['cad_exp_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_exp", use_container_width=True):
                            st.session_state['cad_exp_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Expedientes"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Expedientes via Excel")
                st.caption("O arquivo deve conter as colunas: numero_processo, cliente, descricao, data_manifestacao (AAAA-MM-DD), responsavel, status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_exp")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("expedientes", file_up)

            elif sub == "Consultar Expedientes":
                st.header("📋 Expedientes & Gestão Rápida de Status")
                res = carregar_dados("expedientes")
                if res:
                    df_exp = pd.DataFrame(res)
                    if 'data_manifestacao' in df_exp.columns:
                        df_exp['data_manifestacao'] = df_exp['data_manifestacao'].apply(formatar_data_br)

                    if 'status' in df_exp.columns:
                        exibir_tabela(df_exp.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        exibir_tabela(df_exp, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.subheader("⚡ Atualização Rápida de Status")
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']} ({i.get('status', 'Pendente')})": i for i in res}
                    sel_exp = st.selectbox("Selecione o Expediente:", list(edict.keys()), key="sel_up_exp")
                    obj_exp = edict[sel_exp]
                    
                    novo_status_exp = st.selectbox("Novo Status:", ["Pendente", "Em Andamento", "Manifestado"], index=["Pendente", "Em Andamento", "Manifestado"].index(obj_exp.get('status', 'Pendente')) if obj_exp.get('status', 'Pendente') in ["Pendente", "Em Andamento", "Manifestado"] else 0, key="st_exp_val")
                    
                    if st.button("Atualizar Status do Expediente", type="primary"):
                        supabase.table("expedientes").update({"status": novo_status_exp}).eq("id", obj_exp['id']).execute()
                        registrar_auditoria(username, "Atualizar Status", "Expedientes", f"Processo ID {obj_exp['id']} para {novo_status_exp}")
                        st.cache_data.clear()
                        confirmar_operacao("Status atualizado com sucesso!")
                        st.rerun()
                else: st.info("Sem expedientes cadastrados.")

            elif sub == "Editar Expediente":
                st.header("✏️ Editar Expediente")
                res = carregar_dados("expedientes")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i for i in res}
                    sel = st.selectbox("Expediente:", list(edict.keys()))
                    obj = edict[sel]
                    with st.form("fe_exp"):
                        ep, ec, ed, er, es = st.text_input("Processo", value=obj.get('numero_processo','')), st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Descrição", value=obj.get('descricao','')), st.text_input("Responsável", value=obj.get('responsavel','')), st.selectbox("Status", ["Pendente", "Em Andamento", "Manifestado"])
                        
                        col_eed1, col_eed2 = st.columns(2)
                        with col_eed1:
                            salvar_ed_exp = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_eed2:
                            voltar_ed_exp = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_exp:
                            supabase.table("expedientes").update({"numero_processo": ep, "cliente": ec, "descricao": ed, "responsavel": er, "status": es}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Expediente", "Expedientes", f"ID: {obj['id']}")
                            st.cache_data.clear(); confirmar_operacao("Atualizado!"); st.rerun()
                        if voltar_ed_exp:
                            st.session_state['submenu_atual'] = "Consultar Expedientes"
                            st.rerun()

            elif sub == "Excluir Expediente" and user_role == 'admin':
                st.header("🗑️ Excluir Expediente")
                res = carregar_dados("expedientes")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i['id'] for i in res}
                    sel = st.selectbox("Expediente:", list(edict.keys()))
                    if st.checkbox("Confirmo exclusão do expediente selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("expedientes").delete().eq("id", edict[sel]).execute()
                        registrar_auditoria(username, "Excluir Expediente", "Expedientes", f"ID: {edict[sel]}")
                        st.cache_data.clear(); confirmar_operacao("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os expedientes.")
                    if st.checkbox("Confirmo a exclusão de TODOS os expedientes cadastrados."):
                        if st.button("🔥 EXCLUIR TODOS OS EXPEDIENTES", type="primary"):
                            supabase.table("expedientes").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS EXPEDIENTES", "Expedientes", "Exclusão em massa.")
                            st.cache_data.clear(); confirmar_operacao("Todos os expedientes foram excluídos!"); st.rerun()
                else: st.info("Sem expedientes cadastrados.")

        # --- MÓDULO EXPEDIENTES TRF ---
        elif menu_principal == "Expedientes TRF":
            if sub == "Cadastrar Expediente TRF":
                st.header("⚖️ Novo Expediente TRF")
                with st.form("fc_exp_trf", clear_on_submit=True):
                    proc, cli, desc, dt, resp = st.text_input("Processo"), st.text_input("Cliente"), st.text_input("Descrição"), st.date_input("Prazo", datetime.now()), st.text_input("Responsável")
                    
                    col_btrf1, col_btrf2 = st.columns(2)
                    with col_btrf1:
                        salvar_trf = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_btrf2:
                        voltar_trf = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_trf:
                        supabase.table("expedientes_trf").insert({"numero_processo": proc, "cliente": cli, "descricao": desc, "data_manifestacao": dt.strftime("%Y-%m-%d"), "responsavel": resp, "status": "Pendente"}).execute()
                        registrar_auditoria(username, "Cadastrar Expediente TRF", "Expedientes TRF", f"Processo: {proc}")
                        st.cache_data.clear()
                        st.session_state['cad_trf_sucesso'] = True
                        st.rerun()
                    if voltar_trf:
                        st.session_state['submenu_atual'] = "Consultar Expedientes TRF"
                        st.rerun()

                if st.session_state.get('cad_trf_sucesso'):
                    confirmar_operacao("🎉 Expediente TRF cadastrado com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Expediente TRF", key="btn_novo_trf", type="primary", use_container_width=True):
                            st.session_state['cad_trf_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_trf", use_container_width=True):
                            st.session_state['cad_trf_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Expedientes TRF"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Expedientes TRF via Excel")
                st.caption("O arquivo deve conter as colunas: numero_processo, cliente, descricao, data_manifestacao (AAAA-MM-DD), responsavel, status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_trf")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("expedientes_trf", file_up)

            elif sub == "Consultar Expedientes TRF":
                st.header("📋 Expedientes TRF & Gestão Rápida de Status")
                res = carregar_dados("expedientes_trf")
                if res:
                    df_trf = pd.DataFrame(res)
                    if 'data_manifestacao' in df_trf.columns:
                        df_trf['data_manifestacao'] = df_trf['data_manifestacao'].apply(formatar_data_br)

                    if 'status' in df_trf.columns:
                        exibir_tabela(df_trf.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        exibir_tabela(df_trf, use_container_width=True, hide_index=True)

                    st.markdown("---")
                    st.subheader("⚡ Atualização Rápida de Status")
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']} ({i.get('status', 'Pendente')})": i for i in res}
                    sel_trf = st.selectbox("Selecione o Expediente TRF:", list(edict.keys()), key="sel_up_trf")
                    obj_trf = edict[sel_trf]
                    
                    novo_status_trf = st.selectbox("Novo Status:", ["Pendente", "Em Andamento", "Manifestado"], index=["Pendente", "Em Andamento", "Manifestado"].index(obj_trf.get('status', 'Pendente')) if obj_trf.get('status', 'Pendente') in ["Pendente", "Em Andamento", "Manifestado"] else 0, key="st_trf_val")
                    
                    if st.button("Atualizar Status do Expediente TRF", type="primary"):
                        supabase.table("expedientes_trf").update({"status": novo_status_trf}).eq("id", obj_trf['id']).execute()
                        registrar_auditoria(username, "Atualizar Status TRF", "Expedientes TRF", f"Processo ID {obj_trf['id']} para {novo_status_trf}")
                        st.cache_data.clear()
                        confirmar_operacao("Status atualizado com sucesso!")
                        st.rerun()
                else: st.info("Sem expedientes TRF cadastrados.")

            elif sub == "Editar Expediente TRF":
                st.header("✏️ Editar Expediente TRF")
                res = carregar_dados("expedientes_trf")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i for i in res}
                    sel = st.selectbox("Expediente TRF:", list(edict.keys()))
                    obj = edict[sel]
                    with st.form("fe_exp_trf"):
                        ep, ec, ed, er, es = st.text_input("Processo", value=obj.get('numero_processo','')), st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Descrição", value=obj.get('descricao','')), st.text_input("Responsável", value=obj.get('responsavel','')), st.selectbox("Status", ["Pendente", "Em Andamento", "Manifestado"])
                        
                        col_edtrf1, col_edtrf2 = st.columns(2)
                        with col_edtrf1:
                            salvar_ed_trf = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_edtrf2:
                            voltar_ed_trf = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_trf:
                            supabase.table("expedientes_trf").update({"numero_processo": ep, "cliente": ec, "descricao": ed, "responsavel": er, "status": es}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Expediente TRF", "Expedientes TRF", f"ID: {obj['id']}")
                            st.cache_data.clear(); confirmar_operacao("Atualizado!"); st.rerun()
                        if voltar_ed_trf:
                            st.session_state['submenu_atual'] = "Consultar Expedientes TRF"
                            st.rerun()
                else: st.info("Sem expedientes TRF.")

            elif sub == "Excluir Expediente TRF" and user_role == 'admin':
                st.header("🗑️ Excluir Expediente TRF")
                res = carregar_dados("expedientes_trf")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i['id'] for i in res}
                    sel = st.selectbox("Expediente TRF:", list(edict.keys()))
                    if st.checkbox("Confirmo exclusão do expediente TRF selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("expedientes_trf").delete().eq("id", edict[sel]).execute()
                        registrar_auditoria(username, "Excluir Expediente TRF", "Expedientes TRF", f"ID: {edict[sel]}")
                        st.cache_data.clear(); confirmar_operacao("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os expedientes TRF.")
                    if st.checkbox("Confirmo a exclusão de TODOS os expedientes TRF cadastrados."):
                        if st.button("🔥 EXCLUIR TODOS OS EXPEDIENTES TRF", type="primary"):
                            supabase.table("expedientes_trf").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS EXPEDIENTES TRF", "Expedientes TRF", "Exclusão em massa.")
                            st.cache_data.clear(); confirmar_operacao("Todas as expedientes TRF foram excluídos!"); st.rerun()
                else: st.info("Sem expedientes TRF cadastrados.")

        # --- MÓDULO PENDÊNCIAS ---
        elif menu_principal == "Pendências":
            if sub == "Cadastrar Pendência":
                st.header("📋 Nova Pendência Documental")
                st.caption("Selecione cada documento separadamente. Cada item será cadastrado como uma pendência individual, permitindo acompanhar sua entrega.")
                catalogo_documentos = {
                    "Identificação e dados pessoais": ["RG", "CPF", "CNH", "Certidão de nascimento", "Certidão de casamento", "Certidão de união estável", "Certidão de óbito", "Comprovante de residência", "Comprovante de estado civil", "Título de eleitor", "Carteira de trabalho (CTPS)", "Comprovante de renda", "Declaração de hipossuficiência", "Comprovante de inscrição no CadÚnico"],
                    "Representação e documentos jurídicos": ["Procuração", "Substabelecimento", "Contrato de honorários", "Declaração de autenticidade", "Autorização de representação", "Documentos do representante legal", "Termo de curatela", "Termo de tutela", "Termo de guarda", "Certidão de interdição", "Documentos de herdeiros e sucessores"],
                    "Documentos trabalhistas": ["Contrato de trabalho", "CTPS (páginas relevantes)", "Contracheques / holerites", "Termo de rescisão (TRCT)", "Extrato do FGTS", "Guias de seguro-desemprego", "Aviso-prévio", "Cartões de ponto", "Escalas de trabalho", "Comprovantes de pagamento", "Acordo ou convenção coletiva", "Comunicações com empregador", "CAT (comunicação de acidente de trabalho)", "PPP (perfil profissiográfico previdenciário)", "LTCAT", "ASO / exames ocupacionais"],
                    "Documentos previdenciários / INSS": ["CNIS", "Extrato de benefício", "Carta de concessão", "Memória de cálculo do benefício", "Processo administrativo do INSS", "Comprovante de requerimento administrativo", "Comunicação de decisão / indeferimento", "Carteira de trabalho", "Carnês / guias GPS", "Documentos de atividade rural", "Autodeclaração rural", "Documentos de segurado especial", "PPP", "LTCAT", "Certidão de tempo de contribuição (CTC)", "Certidão de recolhimento prisional"],
                    "Saúde, perícias e assistência social": ["Laudo médico", "Atestado médico", "Relatório médico", "Exames laboratoriais", "Exames de imagem", "Receitas médicas", "Prontuário médico", "Relatório psicológico", "Relatório psiquiátrico", "Relatório de fisioterapia", "Comprovantes de tratamento", "Comprovantes de medicamentos", "Relatório social", "Avaliação biopsicossocial", "Documentos de deficiência", "Comprovantes de gastos com saúde"],
                    "Família e sucessões": ["Certidão de nascimento dos filhos", "Certidão de casamento atualizada", "Certidão de divórcio", "Pacto antenupcial", "Comprovantes de despesas dos dependentes", "Comprovantes de pagamento de pensão", "Comprovantes de renda dos responsáveis", "Documentos de bens do casal", "Escritura de imóvel", "Documentos de veículos", "Testamento", "Certidão de óbito do falecido", "Relação de herdeiros", "Relação de bens do espólio", "Certidões negativas do falecido"],
                    "Cível, consumidor e contratos": ["Contrato assinado", "Aditivos contratuais", "Notas fiscais", "Recibos", "Boletos", "Comprovantes de pagamento", "Extratos bancários", "Comprovantes de transferência / PIX", "Faturas de cartão", "Histórico de cobrança", "Comprovantes de negativação", "Protocolos de atendimento", "Reclamação administrativa", "Notificações extrajudiciais", "Conversas / mensagens", "E-mails", "Fotografias", "Vídeos", "Orçamentos", "Laudo técnico"],
                    "Imóveis, patrimônio e trânsito": ["Matrícula atualizada do imóvel", "Escritura pública", "Contrato de compra e venda", "IPTU", "Comprovantes de posse", "Planta / memorial descritivo", "Certidão de ônus reais", "Documentos de condomínio", "CRLV", "CRV / ATPV-e", "Boletim de ocorrência", "Auto de infração", "Notificação de multa", "Fotos do acidente", "Orçamento de reparo", "Apólice de seguro"],
                    "Empresas e tributário": ["Contrato social", "Alterações contratuais", "Cartão CNPJ", "Documentos dos sócios", "Inscrição estadual / municipal", "Alvará de funcionamento", "Balanços / demonstrações contábeis", "Declarações fiscais", "Guias e comprovantes de tributos", "Certidões negativas de débitos", "Notas fiscais eletrônicas", "Livros contábeis", "Procuração empresarial"],
                    "Processuais e provas": ["Petição inicial", "Contestação", "Réplica", "Documentos da parte contrária", "Intimação", "Citação", "Decisão judicial", "Sentença", "Acórdão", "Certidão de trânsito em julgado", "Cópia integral de processo", "Número do processo", "Comprovante de custas", "Comprovante de depósito judicial", "Rol de testemunhas", "Declaração de testemunha", "Quesitos periciais", "Parecer técnico", "Documentos para recurso", "Comprovante de cumprimento de decisão"]
                }
                with st.form("fc_pen", clear_on_submit=True):
                    cli = st.text_input("Cliente *")
                    proc = st.text_input("Processo (número ou identificação)")
                    st.markdown("#### Documentos solicitados")
                    selecionados = []
                    for grupo, documentos in catalogo_documentos.items():
                        with st.expander(grupo):
                            colunas = st.columns(2)
                            for indice, documento in enumerate(documentos):
                                with colunas[indice % 2]:
                                    if st.checkbox(documento, key=f"pen_doc_{grupo}_{indice}"):
                                        selecionados.append(documento)
                    outros = st.text_area("Outros documentos (um por linha)", help="Informe documentos específicos não encontrados na lista.")
                    selecionados.extend(linha.strip() for linha in outros.splitlines() if linha.strip())
                    # Evita documentos repetidos entre categorias e campos adicionais.
                    selecionados = list(dict.fromkeys(selecionados))
                    col_bpen1, col_bpen2 = st.columns(2)
                    with col_bpen1:
                        salvar_pen = st.form_submit_button("Cadastrar documentos", type="primary", use_container_width=True)
                    with col_bpen2:
                        voltar_pen = st.form_submit_button("⬅️ Voltar", use_container_width=True)
                    if salvar_pen:
                        if not cli.strip() or not selecionados:
                            st.warning("Informe o cliente e selecione ao menos um documento.")
                        else:
                            try:
                                registros = [{"cliente": cli.strip(), "processo": proc.strip(),
                                             "documento_devido": doc,
                                             "data_solicitacao": date.today().strftime("%Y-%m-%d"),
                                             "status": "Pendente"} for doc in selecionados]
                                supabase.table("pendencias").insert(registros).execute()
                                registrar_auditoria(username, "Cadastrar Pendências", "Pendências", f"Cliente: {cli.strip()} | Documentos: {len(registros)}")
                                st.cache_data.clear()
                                st.session_state['cad_pen_sucesso'] = True
                                st.rerun()
                            except Exception as erro:
                                st.error(f"Não foi possível cadastrar os documentos: {erro}")
                    if voltar_pen:
                        st.session_state['submenu_atual'] = "Consultar Pendências"
                        st.rerun()
                if st.session_state.get('cad_pen_sucesso'):
                    confirmar_operacao("Documentos cadastrados como pendências individuais!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Nova Pendência", key="btn_novo_pen", type="primary", use_container_width=True):
                            st.session_state['cad_pen_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_pen", use_container_width=True):
                            st.session_state['cad_pen_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Pendências"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Pendências via Excel")
                st.caption("O arquivo deve conter as colunas: cliente, processo, documento_devido, data_solicitacao (AAAA-MM-DD), status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_pen")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("pendencias", file_up)

            elif sub == "Consultar Pendências":
                st.header("📂 Pendências")
                res = carregar_dados("pendencias")
                if res:
                    df_pen = pd.DataFrame(res)
                    if 'data_solicitacao' in df_pen.columns:
                        df_pen['data_solicitacao'] = df_pen['data_solicitacao'].apply(formatar_data_br)

                    if 'status' in df_pen.columns:
                        exibir_tabela(df_pen.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        exibir_tabela(df_pen, use_container_width=True, hide_index=True)

                    pendencias_abertas = [p for p in res if str(p.get('status', '')).casefold() != 'entregue']
                    if pendencias_abertas:
                        opcoes_entrega = {f"#{p['id']} | {p.get('cliente', '')} | {p.get('documento_devido', '')}": p['id'] for p in pendencias_abertas}
                        escolha_entrega = st.selectbox("Selecione o documento entregue", list(opcoes_entrega), key="pen_entrega_documento")
                        if st.button("Marcar documento como entregue"):
                            supabase.table("pendencias").update({"status": "Entregue"}).eq("id", opcoes_entrega[escolha_entrega]).execute()
                        registrar_auditoria(username, "Marcar Entregue", "Pendências", f"Pendência ID: {pid}")
                        st.cache_data.clear(); confirmar_operacao("Atualizado!"); st.rerun()
                else: st.info("Sem pendências.")

            elif sub == "Editar Pendência":
                st.header("✏️ Editar Pendência")
                res = carregar_dados("pendencias")
                if res:
                    pdict = {f"ID: {i['id']} | {i['cliente']}": i for i in res}
                    sel = st.selectbox("Pendência:", list(pdict.keys()))
                    obj = pdict[sel]
                    with st.form("fe_pen"):
                        ec, ep, ed = st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Processo", value=obj.get('processo','')), st.text_input("Documentos", value=obj.get('documento_devido',''))
                        
                        col_edpen1, col_edpen2 = st.columns(2)
                        with col_edpen1:
                            salvar_ed_pen = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_edpen2:
                            voltar_ed_pen = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_pen:
                            supabase.table("pendencias").update({"cliente": ec, "processo": ep, "documento_devido": ed}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Pendência", "Pendências", f"ID: {obj['id']}")
                            st.cache_data.clear(); confirmar_operacao("Excluído!"); st.rerun()
                        if voltar_ed_pen:
                            st.session_state['submenu_atual'] = "Consultar Pendências"
                            st.rerun()

            elif sub == "Excluir Pendência" and user_role == 'admin':
                st.header("🗑️ Excluir Pendência")
                res = carregar_dados("pendencias")
                if res:
                    pdict = {f"ID: {i['id']} | {i['cliente']}": i['id'] for i in res}
                    sel = st.selectbox("Pendência:", list(pdict.keys()))
                    if st.checkbox("Confirmo exclusão da pendência selecionada.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("pendencias").delete().eq("id", pdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Pendência", "Pendências", f"ID: {pdict[sel]}")
                        st.cache_data.clear(); confirmar_operacao("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS as pendências.")
                    if st.checkbox("Confirmo a exclusão de TODOS as pendências cadastradas."):
                        if st.button("🔥 EXCLUIR TODOS AS PENDÊNCIAS", type="primary"):
                            supabase.table("pendencias").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODAS AS PENDÊNCIAS", "Pendências", "Exclusão em massa.")
                            st.cache_data.clear(); confirmar_operacao("Todas as pendências foram excluídas!"); st.rerun()
                else: st.info("Sem pendências cadastradas.")
