import streamlit as st

# 1. Configuração da Página
st.set_page_config(page_title="Auditoria FUNDEF - Matinha", page_icon="📊", layout="wide")

# CSS Customizado
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #0f3057;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #00587a;
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border-left: 5px solid #0f3057;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .metric-title { font-size: 13px; color: #6c757d; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 22px; color: #212529; font-weight: bold; }
    .highlight { color: #d9534f; } 
    .success-text { color: #28a745; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MOTOR DE CÁLCULO TRIBUTÁRIO (Atualizado com Regra de Transição)
# -----------------------------------------------------------------------------
def calcular_irrf_mensal(base_mensal):
    """
    Aplica a regra vigente de IRRF, incluindo a parcela adicional a deduzir 
    para a faixa de transição entre R$ 5.000,00 e R$ 7.350,00.
    """
    if base_mensal <= 5000.00:
        return 0.00
    
    # Faixa de transição específica (entre 5.000,01 e 7.350,00)
    elif 5000.00 < base_mensal <= 7350.00:
        # 1. Cálculo padrão da tabela (assumindo alíquota de 27,5% e dedução de 908,73 para essa faixa de exemplo)
        imposto_base = (base_mensal * 0.275) - 908.73
        
        # 2. Cálculo do desconto adicional vigente
        desconto_adicional = 978.62 - (0.133145 * base_mensal)
        
        # Garante que o desconto adicional não seja negativo
        desconto_adicional = max(0, desconto_adicional)
        
        # 3. Cota final do IRRF mensal
        imposto_final = imposto_base - desconto_adicional
        return max(0, imposto_final)
        
    # Acima de 7350.00 (Regra normal da tabela cheia de 27,5%)
    else:
        imposto_base = (base_mensal * 0.275) - 908.73
        return max(0, imposto_base)

# 2. Cabeçalho
st.title("📊 Simulador Avançado de Rateio FUNDEF")
st.caption("Motor de Cálculo RRA Integrado | Tabela Progressiva e Regra de Transição Vigente")
st.markdown("---")

# 3. Painel de Entradas
st.subheader("Parâmetros do Beneficiário")
col1, col2, col3 = st.columns(3)

with col1:
    total_receber = st.number_input("Valor Bruto Total (R$)", min_value=0.0, value=200000.0, step=1000.0)
with col2:
    juros_mora = st.number_input("Juros de Mora (R$) - Isento", min_value=0.0, value=30000.0, step=1000.0)
with col3:
    meses_trabalhados = st.number_input("Nº de Meses Efetivos (NM)", min_value=1, value=30, step=1)

st.markdown("<br>", unsafe_allow_html=True)

# 4. Processamento
if st.button("Executar Auditoria Tributária e Gerar Relatório"):
    
    # Cálculos base
    principal_tributavel = total_receber - juros_mora
    base_mensal_rra = principal_tributavel / meses_trabalhados
    
    # Cálculo do Imposto
    imposto_mensal = calcular_irrf_mensal(base_mensal_rra)
    imposto_total_retido = imposto_mensal * meses_trabalhados
    
    # O Valor Líquido é o Total Bruto (Principal + Juros) menos o Imposto Retido
    valor_liquido_receber = total_receber - imposto_total_retido

    # 5. Dashboard de Resultados
    st.markdown("---")
    st.subheader("Relatório de Conformidade (Pronto para Integração SIP)")
    
    # Primeira linha de cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Principal (Base RRA)</div><div class='metric-value'>R$ {principal_tributavel:,.2f}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Fatia de Juros (Isento)</div><div class='metric-value'>R$ {juros_mora:,.2f}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Média Mensal Apurada</div><div class='metric-value'>R$ {base_mensal_rra:,.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Segunda linha de cards (O Resultado Real)
    c4, c5 = st.columns(2)
    with c4:
        st.markdown(f"<div class='metric-box' style='border-left: 5px solid #d9534f;'><div class='metric-title'>IRRF Total a Reter na Fonte</div><div class='metric-value highlight'>R$ {imposto_total_retido:,.2f}</div></div>", unsafe_allow_html=True)
    with c5:
        st.markdown(f"<div class='metric-box' style='border-left: 5px solid #28a745;'><div class='metric-title'>Valor Líquido na Conta do Servidor</div><div class='metric-value success-text'>R$ {valor_liquido_receber:,.2f}</div></div>", unsafe_allow_html=True)

    # Diagnóstico Textual e Memória de Cálculo
    st.markdown("<br>", unsafe_allow_html=True)
    if imposto_total_retido == 0:
        st.success(f"✅ **Parecer Legal:** A média mensal de R$ {base_mensal_rra:,.2f} encontra-se na faixa de isenção. Retenção de IRRF zerada.")
    else:
        st.warning(f"⚠️ **Parecer Legal:** A média mensal de R$ {base_mensal_rra:,.2f} ultrapassou o teto de isenção. Foi aplicada a regra de transição com parcela adicional a deduzir. Imposto mensal apurado: R$ {imposto_mensal:,.2f}. Retenção total para os {meses_trabalhados} meses: R$ {imposto_total_retido:,.2f}.")
        
    with st.expander("Ver Memória de Cálculo Detalhada"):
        st.write(f"- **Base Mensal (Principal / Meses):** R$ {base_mensal_rra:,.2f}")
        st.write(f"- **Imposto Base (Tabela Padrão):** R$ {((base_mensal_rra * 0.275) - 908.73):,.2f}")
        if 5000.00 < base_mensal_rra <= 7350.00:
            st.write(f"- **Desconto Adicional (Regra de Transição):** R$ {(978.62 - (0.133145 * base_mensal_rra)):,.2f}")
        st.write(f"- **Cota Mensal Final:** R$ {imposto_mensal:,.2f}")
        st.write(f"- **Cálculo Final:** {meses_trabalhados} meses x R$ {imposto_mensal:,.2f} = **R$ {imposto_total_retido:,.2f}**")