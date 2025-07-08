import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from app.conexao import criar_conexao

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

    # Curtidas (exemplo positivo, exibido=1)
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
            1 AS exibido,
            -- Se já viu ou não o post
            IF(EXISTS (
                SELECT 1 FROM visualizacoes v2 
                WHERE v2.usuario_id = c.usuario_id AND v2.post_id = c.post_id
            ), 1, 0) AS ja_visto
        FROM curtidas c
        JOIN posts p ON p.id = c.post_id
        JOIN users u ON u.id = p.users_id
        LEFT JOIN comentarios cm ON cm.post_id = p.id AND cm.usuario_id = c.usuario_id
        LEFT JOIN seguindo s ON s.id_seguidor = c.usuario_id AND s.id_seguindo = u.id
        LEFT JOIN post_hashtags ph ON ph.post_id = p.id
        LIMIT 1000
    """, top_hashtags)
    positivos = cursor.fetchall()

    # Visualizações (exemplo negativo, exibido=0)
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
            0 AS exibido,
            -- Se já viu ou não (para visualizações sempre 1, pois já viu)
            1 AS ja_visto
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


def treinar_modelo(df):
    features = [
        'curtiu', 'comentou', 'segue_autor', 'perfil_publico',
        'curtidas_post', 'comentarios_post', 'tempo_post', 'top_hashtag',
        'ja_visto'
    ]
    X = df[features]
    y = df['exibido']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("=== Avaliação do Modelo ===")
    print(classification_report(y_test, modelo.predict(X_test)))

    return modelo


def salvar_modelo(modelo, caminho='modelo_algoritmo/modelo_feed.pkl'):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'wb') as f:
        pickle.dump(modelo, f)
    print(f"✔️ Modelo salvo em: {caminho}")


# Exemplo função para aplicar o ranking considerando o peso para ja_visto
def aplicar_ranking_personalizado(posts, usuario_id, modelo_ml):
    import pandas as pd

    def extrair_features_post(post, usuario_id):
        return {
            'curtiu': int(post.get('curtido_pelo_usuario', False)),
            'comentou': int(any(c['usuario_id'] == usuario_id for c in post.get('comentarios', []))),
            'segue_autor': int(post.get('seguindo', False)),
            'perfil_publico': int(post.get('perfil_publico', 1)),
            'curtidas_post': int(post.get('curtidas', 0)),
            'comentarios_post': int(post.get('comentarios_count', 0)),
            'tempo_post': int(post.get('tempo_post', 0)),
            'top_hashtag': int(post.get('top_hashtag', 0)),
            # Aqui você teria que preencher essa info para cada post, por exemplo:
            'ja_visto': int(post.get('ja_visto', 0)),
        }

    dados_features = [extrair_features_post(post, usuario_id) for post in posts]
    df = pd.DataFrame(dados_features)

    if df.empty:
        return posts

    scores = modelo_ml.predict_proba(df)[:, 1]

    # PESOS
    peso_score_ml = 2.5
    peso_curtidas = 2.0
    peso_comentarios = 2.5
    peso_seguindo = 1.8
    peso_frescor = 0.15
    peso_ja_visto = -1.5  # Penaliza posts já vistos

    for i, post in enumerate(posts):
        score_ml = scores[i]
        post['score_ml'] = round(score_ml, 4)

        curtidas = post.get('curtidas', 0)
        comentarios = post.get('comentarios_count', 0)
        seguindo = int(post.get('seguindo', False))
        tempo_post = post.get('tempo_post', 0)
        ja_visto = int(post.get('ja_visto', 0))

        frescor = max(0, (24 - tempo_post)) * peso_frescor

        post['score_total'] = round(
            score_ml * peso_score_ml +
            curtidas * peso_curtidas +
            comentarios * peso_comentarios +
            seguindo * peso_seguindo +
            frescor +
            ja_visto * peso_ja_visto,
            4
        )

    posts.sort(key=lambda x: x['score_total'], reverse=True)
    return posts


if __name__ == '__main__':
    print("📥 Carregando dados de interação...")
    df = carregar_dados()
    print(f"🔢 Total de registros: {len(df)}")

    print("🧠 Treinando modelo de recomendação...")
    modelo = treinar_modelo(df)

    print("💾 Salvando modelo treinado...")
    salvar_modelo(modelo)
