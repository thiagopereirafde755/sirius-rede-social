from flask import Blueprint, redirect, url_for, session, request, flash
from app.conexao import criar_conexao
from flask import request
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader

excluir_post_bp = Blueprint('excluirpost', __name__)

# =============================================================
#  CONFIGURAÇAO DA CLOUDINARY
# =============================================================
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# =============================================================
#  EXCLUIR POST
# =============================================================
@excluir_post_bp.route('/excluir_post_inicio/<int:post_id>', methods=['POST'])
def excluir_post(post_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    next_page = request.form.get('next')
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # VERIFICA SE O POST PERTENCE AO USER E PEGA OS public_id
                cursor.execute("""
                    SELECT users_id, imagem_public_id, video_public_id 
                    FROM posts WHERE id = %s
                """, (post_id,))
                post = cursor.fetchone()

                if post and post['users_id'] == usuario_id:
                    # DELETA AS MIDIAS DO CLOUDINARY
                    if post.get('imagem_public_id'):
                        try:
                            cloudinary.uploader.destroy(post['imagem_public_id'], invalidate=True)
                        except Exception as e:
                            print(f"[ERRO] Falha ao deletar imagem no Cloudinary: {e}")
                    if post.get('video_public_id'):
                        try:
                            cloudinary.uploader.destroy(post['video_public_id'], resource_type='video', invalidate=True)
                        except Exception as e:
                            print(f"[ERRO] Falha ao deletar vídeo no Cloudinary: {e}")

                    # DELETA AS NOTIFICACOES
                    cursor.execute("DELETE FROM notificacoes WHERE post_id = %s", (post_id,))

                    # DELETA OS COMENTARIOS
                    cursor.execute("DELETE FROM comentarios WHERE post_id = %s", (post_id,))

                    # DELETA AS CURTIDAS
                    cursor.execute("DELETE FROM curtidas WHERE post_id = %s", (post_id,))

                    # DELETA OS SALVO
                    cursor.execute("DELETE FROM posts_salvos WHERE post_id = %s", (post_id,))

                    # DELETA OS REPUBLICADOS
                    cursor.execute("DELETE FROM posts_republicados WHERE post_id = %s", (post_id,))

                    # DELETA O POST
                    cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                    
                    conexao.commit()
                    flash('Post excluído com sucesso.', 'success')
                else:
                    flash('Você não tem permissão para excluir este post.', 'danger')

            conexao.close()
        return redirect(next_page or url_for('inicio.inicio'))
    except Exception as e:
        flash(f'Erro ao excluir o post: {str(e)}', 'danger')
        return redirect(next_page or url_for('inicio.inicio'))

    
