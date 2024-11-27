from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/dados/')
def pegarvendas():
    dados = pd.read_csv('../0_bases_originais/coletor.csv', sep=',')
    return jsonify(dados.to_json())

app.run(debug=True)    



