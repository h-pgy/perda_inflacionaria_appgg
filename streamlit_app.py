import streamlit as st
import pandas as pd
import plotly.express as px

def load_data():
    df = pd.read_csv("microdados_perda_inflacionaria.csv", sep=";", decimal=",")
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)
    return df

def sidebar_factory():
    st.sidebar.subheader("APOGESP")
    st.sidebar.write("Associação dos Analistas de Políticas Públicas e Gestão Governamental")
    
    st.sidebar.divider()
    
    st.sidebar.write("""
    A metodologia baseia-se no cruzamento de dados históricos do Portal de Dados Abertos com as tabelas 
    vencimentais da carreira, corrigindo os valores originais de 2016 pelo IPC-FIPE para calcular a defasagem real.
    """)
    
    with st.sidebar.expander("Ver detalhes da metodologia"):
        st.write("""
        A metodologia aplicada consistiu inicialmente na extração via web scraping de todos os arquivos CSV contendo a relação de servidores ativos disponíveis no Portal de Dados Abertos da Prefeitura de São Paulo desde o ano de 2016. Este marco temporal foi escolhido por representar o início das primeiras nomeações decorrentes do concurso inaugural da carreira de Analista de Políticas Públicas e Gestão Governamental. A partir dessa coleta os dados foram consolidados em um dataframe unificado onde realizamos a padronização das colunas de nome registro funcional e sigla da carreira além da inserção do mês de referência correspondente a cada arquivo original.
        
        Considerando que a sigla da carreira armazena a informação do nível ocupado conseguimos identificar o posicionamento de cada APPGG ativo em qualquer mês da série histórica. Cruzamos essas informações com as tabelas de vencimentos extraídas diretamente da legislação municipal observando os períodos de vigência e as datas base de maio. Esse procedimento permitiu realizar o input do vencimento nominal exato recebido por cada servidor em cada mês de sua trajetória na prefeitura garantindo que servidores nomeados em momentos distintos passassem a compor a base apenas a partir de seu ingresso efetivo.
        
        Para o cálculo da defasagem estabelecemos como parâmetro o vencimento previsto na tabela original da carreira de 2016. Esse valor de referência foi reajustado mês a mês utilizando o IPC FIPE que é o índice inflacionário oficial adotado pela administração municipal com dados obtidos via API do Banco Central. A perda inflacionária nominal de cada mês foi calculada pela diferença entre o valor que deveria ser pago com a correção integral e o vencimento nominal efetivamente praticado na folha de pagamento daquele período.
        
        Como etapa final de processamento todas as perdas nominais identificadas ao longo dos anos foram atualizadas para valores reais presentes utilizando novamente o índice IPC FIPE. Esse tratamento permite uma análise financeira precisa do impacto acumulado demonstrando quanto cada servidor deixou de receber em termos de poder de compra atualizado. O resultado final permite agrupamentos e análises que expõem o tamanho do prejuízo financeiro individual e coletivo enfrentado pela carreira ao longo de sua existência.
        """)

def header_factory(df):
    st.title("Análise de Perda Inflacionária - Carreira APPGG")
    
    st.write("Este aplicativo apresenta o impacto financeiro acumulado causado pela inflação na remuneração dos Analistas de Políticas Públicas e Gestão Governamental. Através do cruzamento de dados históricos de lotação e tabelas de vencimentos quantificamos a defasagem em relação ao poder de compra original da carreira estabelecido em 2016.")

    anos = sorted(df["ano_referencia"].unique())
    ano_min, ano_max = int(min(anos)), int(max(anos))
    
    range_anos = st.slider(
        "Selecione o intervalo de anos para a visão geral",
        min_value=ano_min,
        max_value=ano_max,
        value=(ano_min, ano_max)
    )
    
    return df[(df["ano_referencia"] >= range_anos[0]) & (df["ano_referencia"] <= range_anos[1])]

def metrics_factory(df):
    col1, col2, col3 = st.columns(3)
    perda_total = df["perda_inflacionaria_atualizada"].sum()
    media_perda = df["perda_inflacionaria_atualizada"].mean()
    total_servidores = df["rf"].nunique()
    
    col1.metric("Perda Total Acumulada", f"R$ {perda_total:,.2f}")
    col2.metric("Média de Perda Mensal por Servidor", f"R$ {media_perda:,.2f}")
    col3.metric("Total de Servidores no Período", total_servidores)

def charts_factory(df):
    st.subheader("Evolução da Perda Acumulada no Tempo (Geral)")
    
    evolucao_mensal = df.groupby("data_referencia")["perda_inflacionaria_atualizada"].sum().reset_index()
    evolucao_mensal = evolucao_mensal.sort_values("data_referencia")
    evolucao_mensal["perda_acumulada"] = evolucao_mensal["perda_inflacionaria_atualizada"].cumsum()
    
    fig_linha = px.line(
        evolucao_mensal, 
        x="data_referencia", 
        y="perda_acumulada", 
        labels={"perda_acumulada": "Perda Acumulada (R$)", "data_referencia": "Mês"},
        title="Soma da Perda Acumulada de todos os APPGGs Ativos"
    )
    st.plotly_chart(fig_linha, use_container_width=True)

def individual_analysis_factory(df_total):
    st.divider()
    st.subheader("Consulta por Servidor")
    nomes = sorted(df_total["nome"].unique())
    nome_selecionado = st.selectbox("Selecione o nome para análise individual", nomes)
    
    df_individuo = df_total[df_total["nome"] == nome_selecionado].sort_values("data_referencia")
    
    perda_total_ind = df_individuo["perda_inflacionaria_atualizada"].sum()
    st.metric(f"Perda Total Acumulada - {nome_selecionado}", f"R$ {perda_total_ind:,.2f}")
    
    df_individuo["perda_acumulada_ind"] = df_individuo["perda_inflacionaria_atualizada"].cumsum()
    
    fig_ind = px.line(
        df_individuo, 
        x="data_referencia", 
        y="perda_acumulada_ind", 
        labels={"perda_acumulada_ind": "Perda Acumulada (R$)", "data_referencia": "Data"},
        title=f"Curva de Perda Acumulada - {nome_selecionado}"
    )
    st.plotly_chart(fig_ind, use_container_width=True)

def main():
    st.set_page_config(page_title="Dashboard APPGG", layout="wide")
    
    df_raw = load_data()
    
    sidebar_factory()
    df_filtrado = header_factory(df_raw)
    
    if not df_filtrado.empty:
        metrics_factory(df_filtrado)
        charts_factory(df_filtrado)
        individual_analysis_factory(df_raw)
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")

if __name__ == "__main__":
    main()