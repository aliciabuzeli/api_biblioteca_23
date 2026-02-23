from flask import jsonify, request
from main import app, con
from funcao import verificar_senha
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
from flask import send_file
import os

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/livros', methods=['GET'])

def livros():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT id_livros, titulo, autor, ano_publicacao FROM LIVROS")
        livros = cursor.fetchall()
        livros_list = []
        for livro in livros:
            livros_list.append({
                'id_livros': livro[0],
                'titulo': livro[1],
                'autor': livro[2],
                'ano_publicacao': livro[3]
            })
        return jsonify(mensagem='Lista de livros', livros=livros_list)

    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar Banco de dados: {e}'), 500
    finally:
        cursor.close()


@app.route('/criar_livros', methods=['POST'])
def criar_livros():


    titulo = request.form.get('titulo')
    autor = request.form.get('autor')
    ano_publicacao = request.form.get('ano_publicacao')
    imagem = request.files.get('imagem')

    try:
        cursor = con.cursor()
        cursor.execute("select 1 from livros where titulo = ?", (titulo,))
        if cursor.fetchone():
            return jsonify({"error": "Livro já cadastrado!"}),400
        cursor.execute("INSERT INTO LIVROS (titulo, autor, ano_publicacao) VALUES(?, ?, ?) RETURNING id_livros", (titulo, autor, ano_publicacao))

        codigo_livro =cursor.fetchone()[0]
        con.commit()

        caminho_imagem =None

        if imagem:
            nome_imagem = f"{codigo_livro}.jpg"
            caminho_imagem_destino = os.path.join(app.config['UPLOAD_FOLDER'], "livros")
            os.makedirs(caminho_imagem_destino, exist_ok=True)
            caminho_imagem = os.path.join(caminho_imagem_destino, nome_imagem)
            imagem.save(caminho_imagem)

        return jsonify({
            'mensagem': 'Livro criado com sucesso!',
            'livro': {
                'titulo': titulo,
                'autor': autor,
                'ano_publicacao': ano_publicacao
            }
        }), 201

    except Exception as e:
        return jsonify(mensagem=f'Erro ao inserir no banco de dados: {e}'), 500
    finally:
        cursor.close()

@app.route('/editar_livros/<int:id>', methods=['PUT'])
def editar_livros(id):

    cursor = con.cursor()
    cursor.execute("SELECT id_livros, titulo, autor, ano_publicacao FROM livros WHERE id_livros = ?", (id,))
    tem_livro = cursor.fetchone()
    if not tem_livro:
        cursor.close()
        return jsonify({"error": "Livro não encontrado!"}), 404

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor.execute("UPDATE livros SET titulo = ?, autor = ?, ano_publicacao = ? WHERE id_livros = ?", (titulo, autor, ano_publicacao, id))
    con.commit()
    cursor.close()

    return jsonify({"mensagem": "Livro atualizado com sucesso!",
                    'livros': {
                        'id_livros': id,
                        'titulo': titulo,
                        'autor': autor,
                        'ano_publicacao': ano_publicacao
                               }
                    })

@app.route('/deletar_livros/<int:id>', methods=['DELETE'])
def deletar_livros(id):
    cursor = con.cursor()
    cursor.execute("SELECT 1 FROM livros WHERE id_livros = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Livro não encontrado!"}), 404

    cursor.execute("DELETE FROM livros WHERE id_livros = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify(
        {"mensagem": "Livro deletado com sucesso!",
         'id_livros': id}

    )

@app.route('/usuarios', methods=['GET'])
def usuarios():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT id_usuario, nome, usuario, senha FROM usuarios")
        usuarios = cursor.fetchall()
        usuario_list = []
        for usuarios in usuarios:
            usuario_list.append({
                'id_usuario': usuarios[0],
                'nome': usuarios[1],
                'usuario': usuarios[2],
                'senha': usuarios[3]
            })
        return jsonify(mensagem='Lista de usuarios', usuario=usuario_list)

    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar Banco de dados: {e}'), 500
    finally:
        cursor.close()


@app.route('/criar_usuarios', methods=['POST'])
def criar_usuarios():
    dados = request.get_json()

    nome = dados.get('nome')
    usuario = dados.get('usuario')
    senha = dados.get('senha')

    try:
        cursor = con.cursor()
        cursor.execute("select 1 from usuarios where usuario = ?", (usuario,))
        if cursor.fetchone():
            return jsonify({"error": "Usuário já cadastrado!"}), 400
        if verificar_senha(senha) == False:
            return jsonify({"error": "Senha deve conter letra maiúscula, letra minúscula, número e caractere especial!"}), 400

        senha_hash = generate_password_hash(senha).decode('utf-8')

        cursor.execute("""INSERT INTO usuarios (nome, usuario, senha) VALUES(?, ?, ?)""", (nome, usuario, senha_hash))
        con.commit()
        return jsonify({
            'mensagem': 'Usuario criado com sucesso!',
            'usuarios': {
                'nome': nome,
                'usuario': usuario,
                'senha': senha_hash
            }
        }), 201

    except Exception as e:
        return jsonify(mensagem=f'Erro ao inserir no banco de dados: {e}'), 500
    finally:
        cursor.close()


@app.route('/editar_usuarios/<int:id>', methods=['PUT'])
def editar_usuarios(id):

    cursor = con.cursor()
    cursor.execute("SELECT id_usuario, nome, usuario, senha FROM usuarios WHERE id_usuario = ?", (id,))
    tem_usuario = cursor.fetchone()
    if not tem_usuario:
        cursor.close()
        return jsonify({"error": "Usuario não encontrado!"}), 404

    data = request.get_json()
    nome = data.get('nome')
    usuario = data.get('usuario')
    senha = data.get('senha')

    if verificar_senha(senha) == False:
        return jsonify(
            {"error": "Senha deve conter letra maiúscula, letra minúscula, número e caractere especial!"}), 400

    senha_hash = generate_password_hash(senha).decode('utf-8')

    cursor.execute("UPDATE usuarios SET nome = ?, usuario = ?, senha = ? WHERE id_usuario = ?", (nome, usuario, senha_hash, id))
    con.commit()
    cursor.close()

    return jsonify({"mensagem": "Usuario atualizado com sucesso!",
                    'usuarios': {
                        'id_usuario': id,
                        'nome': nome,
                        'usuario': usuario,
                        'senha': senha_hash
                               }
                    })


@app.route('/deletar_usuarios/<int:id>', methods=['DELETE'])
def deletar_usuarios(id):
    cursor = con.cursor()
    cursor.execute("SELECT 1 FROM usuarios WHERE id_usuario = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Usuario não encontrado!"}), 404

    cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify(
        {"mensagem": "Usuario deletado com sucesso!",
         'id_usuario': id}

    )




app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    senha = data.get('senha')

    try:
        cursor = con.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        if not resultado:
            return jsonify({"error": "Usuário não encontrado!"}), 404

        senha_hash = resultado[0]
        if not check_password_hash(senha_hash, senha):
            return jsonify({"error": "Senha incorreta!"}), 401

        return jsonify({"mensagem": "Login bem-sucedido!"})

    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar Banco de dados: {e}'), 500
    finally:
        cursor.close()



@app.route('/livros_relatorio', methods=['GET'])
def livros_relatorio():
     cursor = con.cursor()
     cursor.execute("SELECT id_livros, titulo, autor, ano_publicacao FROM livros")
     livros = cursor.fetchall()
     cursor.close()

     pdf = FPDF()
     pdf.set_auto_page_break(auto=True, margin=15)
     pdf.add_page()
     pdf.set_font("Arial", style='B', size=16)
     pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')

     pdf.ln(5)  # Espaço entre o título e a linha
     pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
     pdf.ln(5)  # Espaço após a linha

     pdf.set_font("Arial", size=12)
     for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)


     contador_livros = len(livros)
     pdf.ln(10)  # Espaço antes do contador
     pdf.set_font("Arial", style='B', size=12)
     pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')

     pdf_path = "relatorio_livros.pdf"
     pdf.output(pdf_path)
     return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')





@app.route('/usuario_relatorio', methods=['GET'])
def usuario_relatorio():
     cursor = con.cursor()
     cursor.execute("SELECT id_usuario, nome, usuario FROM usuarios")
     usuarios = cursor.fetchall()
     cursor.close()

     pdf = FPDF()
     pdf.set_auto_page_break(auto=True, margin=15)
     pdf.add_page()
     pdf.set_font("Arial", style='B', size=16)
     pdf.cell(200, 10, "Relatorio de Usuarios", ln=True, align='C')

     pdf.ln(5)  # Espaço entre o título e a linha
     pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
     pdf.ln(5)  # Espaço após a linha

     pdf.set_font("Arial", size=12)
     for usuarios in usuarios:
        pdf.cell(200, 10, f"ID: {usuarios[0]} - {usuarios[1]} - {usuarios[2]}", ln=True)


     contador_usuarios = len(usuarios)
     pdf.ln(10)  # Espaço antes do contador
     pdf.set_font("Arial", style='B', size=12)
     pdf.cell(200, 10, f"Total de usuários cadastrados: {contador_usuarios}", ln=True, align='C')

     pdf_path = "relatorio_usuarios.pdf"
     pdf.output(pdf_path)
     return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')









