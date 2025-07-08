import pickle
import pandas as pd
from datetime import datetime

# ============================
# Conexão com o banco de dados
# ============================
from app.conexao import criar_conexao

# ============================
# Carregar modelo de ML treinado
# ============================
with open('models/modelo_feed.pkl', 'rb') as f:
    modelo = pickle.load(f)

# ============================
# Função principal
# ============================
def calcular_score_universal():
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)

    print("📥 Buscando posts para avaliação...")
    cursor.execute("""
        SELECT 
            p.id AS post_id,
            p.users_id,
            p.data_postagem,
            u.perfil_publico
        FROM posts p
        JOIN users u ON u.id = p.users_id
        ORDER BY p.data_postagem DESC
        LIMIT 200
    """)
    posts = cursor.fetchall()

    for post in posts:
        post_id = post['post_id']
        user_autor = post['users_id']
        perfil_publico = int(post.get('perfil_publico', 1))
        tempo_post = int((datetime.now() - post['data_postagem']).total_seconds() / 3600)

        # Buscar curtidas e comentários totais
        cursor.execute("SELECT COUNT(*) as total FROM curtidas WHERE post_id = %s", (post_id,))
        curtidas_post = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM comentarios WHERE post_id = %s", (post_id,))
        comentarios_post = cursor.fetchone()['total']

        # Verificar se tem hashtag popular
        cursor.execute("""
            SELECT h.id
            FROM hashtags h
            JOIN post_hashtags ph ON h.id = ph.hashtag_id
            WHERE ph.post_id = %s
        """, (post_id,))
        hashtags = [row['id'] for row in cursor.fetchall()]

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
        top_hashtags = [row['id'] for row in cursor.fetchall()]
        top_hashtag = int(any(h in top_hashtags for h in hashtags))

        # Simular usuários para avaliar score
        cursor.execute("SELECT id FROM users WHERE id != %s ORDER BY RAND() LIMIT 10", (user_autor,))
        usuarios = cursor.fetchall()

        features = []
        for u in usuarios:
            # Simulação neutra
            features.append({
                'curtiu': 0,
                'comentou': 0,
                'segue_autor': 0,
                'perfil_publico': perfil_publico,
                'curtidas_post': curtidas_post,
                'comentarios_post': comentarios_post,
                'tempo_post': tempo_post,
                'top_hashtag': top_hashtag
            })

        if features:
            df = pd.DataFrame(features)
            score = round(modelo.predict_proba(df)[:, 1].mean(), 4)

            # Atualizar no banco
            cursor.execute("UPDATE posts SET score_ml = %s WHERE id = %s", (score, post_id))
            print(f"✅ Post {post_id} → score salvo: {score}")

    conn.commit()
    cursor.close()
    conn.close()
    print("🏁 Finalizado com sucesso!")

# ============================
# Execução
# ============================
if __name__ == "__main__":
    calcular_score_universal()
