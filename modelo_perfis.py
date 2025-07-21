import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from app.conexao import criar_conexao

# =========================
# CARREGAR DADOS DE INTERAÇÕES
# =========================
def carregar_dados_perfis():
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    # Positivos (seguindo)
    cursor.execute("""
        SELECT 
            s.id_seguidor AS usuario_id,
            s.id_seguindo AS perfil_id,
            1 AS seguiu,
            u.perfil_publico,
            TIMESTAMPDIFF(DAY, u.data_cadastro, NOW()) AS dias_desde_cadastro,
            EXISTS (
                SELECT 1 FROM seguindo s2
                WHERE s2.id_seguidor = s.id_seguidor 
                  AND s2.id_seguindo IN (
                      SELECT s3.id_seguindo FROM seguindo s3 WHERE s3.id_seguidor = u.id
                  )
            ) AS amigos_em_comum,
            EXISTS (
                SELECT 1 FROM curtidas c 
                JOIN posts p ON p.id = c.post_id
                WHERE c.usuario_id = s.id_seguidor AND p.users_id = u.id
            ) AS curtiu_post_do_perfil,
            1 AS exibido
        FROM seguindo s
        JOIN users u ON u.id = s.id_seguindo
        WHERE u.suspenso = 0
    """)
    positivos = cursor.fetchall()

    # Negativos (visualizado e não seguido)
    cursor.execute("""
        SELECT 
            v.usuario_id,
            v.perfil_id,
            0 AS seguiu,
            u.perfil_publico,
            TIMESTAMPDIFF(DAY, u.data_cadastro, NOW()) AS dias_desde_cadastro,
            EXISTS (
                SELECT 1 FROM seguindo s2
                WHERE s2.id_seguidor = v.usuario_id 
                  AND s2.id_seguindo IN (
                      SELECT s3.id_seguindo FROM seguindo s3 WHERE s3.id_seguidor = u.id
                  )
            ) AS amigos_em_comum,
            EXISTS (
                SELECT 1 FROM curtidas c 
                JOIN posts p ON p.id = c.post_id
                WHERE c.usuario_id = v.usuario_id AND p.users_id = u.id
            ) AS curtiu_post_do_perfil,
            0 AS exibido
        FROM visualizacoes_perfis v
        JOIN users u ON u.id = v.perfil_id
        WHERE NOT EXISTS (
            SELECT 1 FROM seguindo s 
            WHERE s.id_seguidor = v.usuario_id AND s.id_seguindo = v.perfil_id
        ) AND u.suspenso = 0
    """)
    negativos = cursor.fetchall()

    cursor.close()
    conexao.close()

    df = pd.DataFrame(positivos + negativos)
    return df

# =========================
# TREINAR MODELO
# =========================
def treinar_modelo(df):
    features = [
        'perfil_publico',
        'dias_desde_cadastro',
        'amigos_em_comum',
        'curtiu_post_do_perfil'
    ]
    X = df[features]
    y = df['exibido']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("=== RELATÓRIO DO MODELO ===")
    print(classification_report(y_test, modelo.predict(X_test)))

    return modelo

# =========================
# SALVAR MODELO
# =========================
def salvar_modelo(modelo, caminho='modelo_algoritmo/modelo_perfis.pkl'):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'wb') as f:
        pickle.dump(modelo, f)
    print(f"✔️ Modelo salvo com sucesso em {caminho}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🔄 Carregando dados...")
    df = carregar_dados_perfis()
    
    if df.empty:
        print("⚠️ Nenhum dado disponível para treinar o modelo.")
        exit()

    print(f"🔢 Total de amostras: {len(df)}")
    modelo = treinar_modelo(df)
    salvar_modelo(modelo)
