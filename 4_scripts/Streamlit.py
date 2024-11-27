import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import json

from sqlalchemy import create_engine 
engine = create_engine('sqlite:///4_scripts/banco.db', echo=True)
connection = engine.raw_connection()

df = pd.read_sql('SELECT * FROM banco', con=connection) 
print("Dados lidos do banco de dados:") 
print(df.head())

# # Ler o banco de dados
# df = pd.read_sql('SELECT * FROM dados', con=connection)
# print("Dados lidos do banco de dados:")
# print(df.head())

# # Filtragem e carregamento da base de dados
# df = pd.read_csv('../1_bases_tratadas/base_tratada.csv', sep=',', encoding='utf-8')
# df = df.drop(df.columns[0], axis=1)
# df.rename(columns={'nome': 'Nome do jogo', 'porcentagem_desconto':'Desconto (%)', 'preco':'preco', 'tipo':'tipo', 'sistema':'sistema', 'plataforma':'plataforma'}, inplace=True)

# Inicio da sidebar
st.sidebar.title("AP2 Gabriel/Vinícius")
st.sidebar.markdown("---")

palavra_chave = st.sidebar.text_input('Buscar o Nome do jogo ou palavra-chave:')

if palavra_chave:
    df_filtrado = df.loc[df['Nome do jogo'].str.contains(palavra_chave, case=False)]
else:
    plataforma = st.sidebar.selectbox('Selecione a plataforma:', ['Console', 'PC', 'Mobile'])

    if plataforma == 'Console':
        preco_min, preco_max = st.sidebar.slider('Selecione o intervalo de preço:', float(df['preco'].min()), float(df['preco'].max()), (float(df['preco'].min()), float(df['preco'].max())), step=0.1)
        df_filtrado = df[(df['preco'] >= preco_min) & (df['preco'] <= preco_max) & (df['plataforma'] == 'console')]
        sistema = st.sidebar.selectbox('Selecione o sistema:', ['Nintendo', 'Playstation', 'Xbox'])
        sistema = sistema.lower()
        df_filtrado = df_filtrado.loc[df_filtrado['sistema'].str.contains(sistema)]
        st.info('Com exceção da Nintendo, aos demais sistemas são disponibilizados apenas créditos para a loja virtual da plataforma.', icon="ℹ️")
    elif plataforma == 'PC':
        preco_min, preco_max = st.sidebar.slider('Selecione o intervalo de preço:', float(df['preco'].min()), float(df['preco'].max()), (float(df['preco'].min()), float(df['preco'].max())), step=0.1)
        df_filtrado = df[(df['preco'] >= preco_min) & (df['preco'] <= preco_max) & (df['plataforma'] == 'pc')]
        sistema = st.sidebar.selectbox('Selecione o sistema:', ['Windows','Steam', 'Mac', 'Linux'])
        sistema = sistema.lower()
        df_filtrado = df_filtrado.loc[df_filtrado['sistema'].str.contains(sistema)]
    else:
        preco_min, preco_max = st.sidebar.slider('Selecione o intervalo de preço:', float(df['preco'].min()), float(df['preco'].max()), (float(df['preco'].min()), float(df['preco'].max())), step=0.1)
        df_filtrado = df[(df['preco'] >= preco_min) & (df['preco'] <= preco_max) & (df['plataforma'] == 'mobile')]
        sistema = st.sidebar.selectbox('Selecione o sistema:', ['Android', 'iOS'])
        sistema = sistema.lower()
        df_filtrado = df_filtrado.loc[df_filtrado['sistema'].str.contains(sistema)]
        st.info('São disponibilizados apenas créditos para a loja virtual da plataforma.', icon="ℹ️")
st.sidebar.markdown("---")

# Inicio do index
st.write(
    '''
    ***Tabela filtrada***
    '''
)

if df_filtrado.empty:
    st.error('Nenhum jogo encontrado com essa palavra-chave ou seleção.')
else:
    st.markdown('Esta tabela é resultado dos filtros utilizados do menu:')
    pd.set_option('display.max_colwidth', None)
    st.write(df_filtrado)
    # Inicio dos gráficos plotly

    # calcula a porcentagem da maior e menor tipo
    df_filtrado_por_categoria = df_filtrado.groupby(['plataforma', 'tipo']).count().reset_index()[['plataforma', 'tipo', 'nome']]
    df_filtrado_por_categoria = df_filtrado_por_categoria.pivot_table(values='nome', index='tipo', columns='plataforma', fill_value=0)
    total_jogos_por_plataforma = df_filtrado_por_categoria.sum(axis=0)

    df_filtrado_por_categoria_porcentagem = df_filtrado_por_categoria / total_jogos_por_plataforma * 100

    categoria_maior_porcentagem = df_filtrado_por_categoria_porcentagem.idxmax().values[0]
    maior_porcentagem = df_filtrado_por_categoria_porcentagem.max().values[0]

    categoria_menor_porcentagem = df_filtrado_por_categoria_porcentagem.idxmin().values[0]
    menor_porcentagem = df_filtrado_por_categoria_porcentagem.min().values[0]

    df_filtrado_por_categoria = df_filtrado.groupby('tipo').count().reset_index()
    fig = px.pie(df_filtrado_por_categoria, values='nome', names='tipo', title='Distribuição dos jogos por tipo')
    st.plotly_chart(fig)
    st.markdown(
        f"""
        Este gráfico de pizza representa a distribuição de tipo de acordo com a plataforma
        <br>
        Maior porcentagem: `{categoria_maior_porcentagem}` com `{maior_porcentagem:.2f}%` dos jogos
        <br>
        Menor porcentagem: `{categoria_menor_porcentagem}` com `{menor_porcentagem:.2f}%` dos jogos
        """,
        unsafe_allow_html=True
    )

    # calcula o maior e menor valor de preço e desconto
    df_desconto_jogo = df_filtrado[['porcentagem_desconto', 'nome','preco','tipo']].dropna()
    df_maior_promocao = df_desconto_jogo.sort_values(by='porcentagem_desconto', ascending=False)
    df_menor_promocao = df_desconto_jogo.sort_values(by='porcentagem_desconto', ascending=True)

    maior_desconto_jogo = df_maior_promocao.iloc[0]['nome']
    maior_desconto_valor = df_maior_promocao.iloc[0]['porcentagem_desconto']
    maior_desconto_preco = df_maior_promocao.iloc[0]['preco']
    maior_desconto_categoria = df_maior_promocao.iloc[0]['tipo']

    menor_desconto_jogo = df_menor_promocao.iloc[0]['nome']
    menor_desconto_valor = df_menor_promocao.iloc[0]['porcentagem_desconto']
    menor_desconto_preco = df_menor_promocao.iloc[0]['preco']
    menor_desconto_categoria = df_menor_promocao.iloc[0]['tipo']

    fig = px.scatter(df_filtrado, x="preco", y="porcentagem_desconto", color="tipo", title="Preço x Desconto x tipo")
    st.plotly_chart(fig)
    st.markdown(
        f"""
        Este gráfico de disperção representa a distribuição de desconto de acordo com o preço e tipo
        <br>
        Maior promoção: `{maior_desconto_jogo}` - `{maior_desconto_valor}%`: `R${maior_desconto_preco}` (`{maior_desconto_categoria}`)
        <br>
        Menor promoção: `{menor_desconto_jogo}` - `{menor_desconto_valor}%`: `R${menor_desconto_preco}` (`{menor_desconto_categoria}`)
        """,
        unsafe_allow_html=True
    )

    # calcula a quantidade de jogos por sistema
    df_sistemas = df_filtrado[['sistema']].dropna()

    df_sistemas_count = df_sistemas.groupby('sistema').size().sort_values(ascending=False)

    maior_quantidade = df_sistemas_count.index[0]
    menor_quantidade = df_sistemas_count.index[-1]

    fig = px.histogram(df_filtrado, x="sistema", title="Número de jogos por sistema")
    st.plotly_chart(fig)
    st.markdown(
    f"""
    Este gráfico de barras representa o número total de compatibilidade de jogos por sistema
    <br>
    Maior compatibilidade: `{maior_quantidade}`
    <br>
    Menor compatibilidade: `{menor_quantidade}`
    """,
    unsafe_allow_html=True
)

    # calcular o numero de outliers
    Q1 = df_filtrado['preco'].quantile(0.25)
    Q3 = df_filtrado['preco'].quantile(0.75)
    IQR = Q3 - Q1

    outliers = df_filtrado[(df_filtrado['preco'] < (Q1 - 1.5 * IQR)) | (df_filtrado['preco'] > (Q3 + 1.5 * IQR))]
    num_outliers = len(outliers)


    fig = px.box(df_filtrado, x="preco", y="tipo", color="tipo", title="Bloxplot das tipo relacionados ao preço")
st.plotly_chart(fig)
if num_outliers != 0:
        st.markdown(
        f"""
        Este bloxplot representa a distribuição de tipo de acordo com o preço
        <br>
        Quantidade de outliers: `{num_outliers}`
        """,
        unsafe_allow_html=True
        )
else:
        st.markdown(
        f"""
        Este bloxplot representa a distribuição de categoria de acordo com o preço
        <br>
        """,
        unsafe_allow_html=True
        )
        st.error("Não existe outliers neste bloxplot")

# Fim dos gráficos plotly
# Inicio dos gráficos streamlit

preco_original = df_filtrado['preco'] / (100 - df_filtrado['porcentagem_desconto']) * 100
st.subheader('Preço original x Preço com desconto')
st.line_chart(pd.DataFrame({'Preço Original': preco_original, 'Preço com Desconto': df_filtrado['preco']}))
st.markdown(
f"""
Este gráfico de linhas representa a comparação entre o preço original com o preço com o desconto, sendo o `eixo Y` representando o `preco` e o `eixo X` representando o index de cada `Jogo`
""",
unsafe_allow_html=True
)

# Fim dos gráficos streamlit
st.write(
'''
***Tabela geral***
'''
)

pd.set_option('display.max_colwidth', None)
st.write(df.dropna())
st.warning('Dica: Ao selecionar a coluna, ela já é filtrada por ordem', icon="💡")
# Fim do index
