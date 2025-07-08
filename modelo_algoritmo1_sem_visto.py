import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ================================================
# 1. Conexão com o banco
# ================================================
from app.conexao import criar_conexao

# ================================================
# 2. Carregar dados com base em curtidas e visualizações
# ================================================
def carregar_dados():
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    # Buscar top hashtags das últimas 10 horas
    cursor.execute("""
        SELECT h.id
        FROM hashtags h
        JOIN post_hashtags ph ON h.id = ph.hashtag_id
        JOIN posts p ON ph.post_id = p.id
        WHERE p.data_postagem >= NOW() - INTERVAL 10 HOUR
        GROUP BY h.id
        ORDER BY COUNT(*) DESC
        LIMIT 3
    """)
    top_hashtags = [row['id'] for row in cursor.fetchall()] or [-1]
    format_strings = ','.join(['%s'] * len(top_hashtags))

    # CURTIDAS = Exemplo positivo (exibido = 1)
    cursor.execute(f"""
        SELECT
            c.usuario_id,
            c.post_id,
            1 AS curtiu,
            IF(cm.usuario_id IS NOT NULL, 1, 0) AS comentou,
            IF(s.id_seguindo IS NOT NULL, 1, 0) AS segue_autor,
            u.perfil_publico,
            (SELECT COUNT(*) FROM curtidas c2 WHERE c2.post_id = p.id) AS curtidas_post,
            (SELECT COUNT(*) FROM comentarios cm2 WHERE cm2.post_id = p.id) AS comentarios_post,
            TIMESTAMPDIFF(HOUR, p.data_postagem, NOW()) AS tempo_post,
            IF(ph.hashtag_id IN ({format_strings}), 1, 0) AS top_hashtag,
            1 AS exibido
        FROM curtidas c
        JOIN posts p ON p.id = c.post_id
        JOIN users u ON u.id = p.users_id
        LEFT JOIN comentarios cm ON cm.post_id = p.id AND cm.usuario_id = c.usuario_id
        LEFT JOIN seguindo s ON s.id_seguidor = c.usuario_id AND s.id_seguindo = u.id
        LEFT JOIN post_hashtags ph ON ph.post_id = p.id
        LIMIT 1000
    """, top_hashtags)
    positivos = cursor.fetchall()

    # VISUALIZAÇÕES
    cursor.execute(f"""
        SELECT
            v.usuario_id,
            v.post_id,
            0 AS curtiu,
            0 AS comentou,
            IF(s.id_seguindo IS NOT NULL, 1, 0) AS segue_autor,
            u.perfil_publico,
            (SELECT COUNT(*) FROM curtidas c2 WHERE c2.post_id = p.id) AS curtidas_post,
            (SELECT COUNT(*) FROM comentarios cm2 WHERE cm2.post_id = p.id) AS comentarios_post,
            TIMESTAMPDIFF(HOUR, p.data_postagem, NOW()) AS tempo_post,
            IF(ph.hashtag_id IN ({format_strings}), 1, 0) AS top_hashtag,
            0 AS exibido
        FROM visualizacoes v
        JOIN posts p ON p.id = v.post_id
        JOIN users u ON u.id = p.users_id
        LEFT JOIN curtidas c ON c.post_id = p.id AND c.usuario_id = v.usuario_id
        LEFT JOIN comentarios cm ON cm.post_id = p.id AND cm.usuario_id = v.usuario_id
        LEFT JOIN seguindo s ON s.id_seguidor = v.usuario_id AND s.id_seguindo = u.id
        LEFT JOIN post_hashtags ph ON ph.post_id = p.id
        WHERE c.id IS NULL AND cm.id IS NULL
        LIMIT 1000
    """, top_hashtags)
    negativos = cursor.fetchall()

    cursor.close()
    conexao.close()

    df = pd.DataFrame(positivos + negativos)
    return df

# ================================================
# 3. Treinamento do modelo
# ================================================
def treinar_modelo(df):
    features = ['curtiu', 'comentou', 'segue_autor', 'perfil_publico',
                'curtidas_post', 'comentarios_post', 'tempo_post', 'top_hashtag']
    X = df[features]
    y = df['exibido']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("=== Avaliação do Modelo ===")
    print(classification_report(y_test, modelo.predict(X_test)))

    return modelo

# ================================================
# 4. Salvar o modelo
# ================================================
def salvar_modelo(modelo, caminho='models/modelo_feed.pkl'):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'wb') as f:
        pickle.dump(modelo, f)
    print(f"✔️ Modelo salvo em: {caminho}")

# ================================================
# 5. Pipeline principal
# ================================================
if __name__ == '__main__':
    print("📥 Carregando dados de interação...")
    df = carregar_dados()
    print(f"🔢 Total de registros: {len(df)}")

    print("🧠 Treinando modelo de recomendação...")
    modelo = treinar_modelo(df)

    print("💾 Salvando modelo treinado...")
    salvar_modelo(modelo)
