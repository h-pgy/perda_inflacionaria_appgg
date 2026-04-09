import streamlit as st
import pandas as pd
import plotly.express as px
import io

def load_data():
    df = pd.read_csv("microdados_perda_inflacionaria.csv", sep=";", decimal=",")
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)
    return df

def sidebar_factory():
    st.sidebar.subheader("APOGESP")
    st.sidebar.write("Associação dos Analistas de Políticas Públicas e Gestão Governamental")
    
    st.sidebar.divider()
    
    st.sidebar.subheader("Metodologia")
    
    st.sidebar.write("""
    A metodologia baseia-se no cruzamento de dados históricos do Portal de Dados Abertos com as tabelas 
    vencimentais da carreira, corrigindo os valores originais de 2016 pelo IPC-FIPE para calcular a defasagem real.
    """)
    
    st.sidebar.link_button(
        "Ver Notebook de Cálculo (GitHub)", 
        "https://github.com/h-pgy/perda_inflacionaria_appgg/blob/main/calculo_perda_inflacionaria.ipynb"
    )
    
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
        "Selecione o intervalo de anos para filtrar todos os gráficos e dados",
        min_value=ano_min,
        max_value=ano_max,
        value=(ano_min, ano_max)
    )
    
    df_filtrado = df[(df["ano_referencia"] >= range_anos[0]) & (df["ano_referencia"] <= range_anos[1])]
    return df_filtrado

def individual_selector_factory(df):
    st.divider()
    nomes = sorted(df["nome"].unique())
    nome_selecionado = st.selectbox("Selecione o servidor para análise individual comparativa", nomes)
    return df[df["nome"] == nome_selecionado], nome_selecionado

def dashboard_columns_factory(df_carreira, df_individuo, nome_servidor):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Visão Geral da Carreira")
        perda_total_carreira = df_carreira["perda_inflacionaria_atualizada"].sum()
        st.metric("Perda Total Acumulada (Carreira)", f"R$ {perda_total_carreira:,.2f}")
        
        evolucao_carreira = df_carreira.groupby("data_referencia")["perda_inflacionaria_atualizada"].sum().reset_index().sort_values("data_referencia")
        evolucao_carreira["perda_acumulada"] = evolucao_carreira["perda_inflacionaria_atualizada"].cumsum()
        
        fig_carreira = px.line(
            evolucao_carreira, 
            x="data_referencia", 
            y="perda_acumulada",
            title="Evolução da Perda Acumulada - Toda a Carreira",
            labels={"perda_acumulada": "Soma Acumulada (R$)", "data_referencia": "Tempo"}
        )
        st.plotly_chart(fig_carreira, use_container_width=True)

    with col2:
        st.subheader(f"Visão Individual: {nome_servidor}")
        perda_total_ind = df_individuo["perda_inflacionaria_atualizada"].sum()
        st.metric(f"Perda Total Acumulada ({nome_servidor})", f"R$ {perda_total_ind:,.2f}")
        
        df_individuo_sorted = df_individuo.sort_values("data_referencia")
        df_individuo_sorted["perda_acumulada_ind"] = df_individuo_sorted["perda_inflacionaria_atualizada"].cumsum()
        
        fig_individual = px.line(
            df_individuo_sorted, 
            x="data_referencia", 
            y="perda_acumulada_ind",
            title=f"Evolução da Perda Acumulada - {nome_servidor}",
            labels={"perda_acumulada_ind": "Soma Acumulada (R$)", "data_referencia": "Tempo"}
        )
        st.plotly_chart(fig_individual, use_container_width=True)

def data_download_factory(df):
    st.divider()
    with st.expander("Acessar Microdados e Exportação"):
        st.write("Abaixo estão listados os microdados filtrados conforme o intervalo de anos selecionado no slider principal.")
        st.dataframe(df.sort_values(by=["data_referencia", "nome"], ascending=[False, True]), use_container_width=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
        processed_data = output.getvalue()
        
        st.download_button(
            label="Baixar dados filtrados em Excel",
            data=processed_data,
            file_name="microdados_appgg_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def main():
    st.set_page_config(page_title="Dashboard APPGG - Perda Inflacionária", layout="wide")
    
    df_raw = load_data()
    sidebar_factory()
    df_filtrado = header_factory(df_raw)
    
    if not df_filtrado.empty:
        df_individuo, nome_servidor = individual_selector_factory(df_filtrado)
        dashboard_columns_factory(df_filtrado, df_individuo, nome_servidor)
        data_download_factory(df_filtrado)
    else:
        st.warning("Nenhum dado encontrado para o intervalo selecionado.")

if __name__ == "__main__":
    main()