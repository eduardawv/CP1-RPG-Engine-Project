from flask import Flask, render_template, jsonify
import oracledb
import os
from dotenv import load_dotenv

app = Flask(__name__, template_folder="../templates")

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/herois")
def herois():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_heroi, nome, classe, hp_atual, hp_max, status
        FROM TB_HEROIS
        ORDER BY id_heroi
    """)

    colunas = [col[0].lower() for col in cursor.description]

    resultado = []

    for linha in cursor.fetchall():
        resultado.append(dict(zip(colunas, linha)))

    cursor.close()
    conn.close()

    return jsonify(resultado)

@app.route("/resetar", methods=["POST"])
def resetar():

    conn = get_connection()
    cursor = conn.cursor()

    plsql = """

    BEGIN

        UPDATE TB_HEROIS
        SET hp_atual = hp_max,
            status = 'ATIVO';

        COMMIT;

    END;

    """

    cursor.execute(plsql)

    cursor.close()
    conn.close()

    return {"status": "vida resetada"}


@app.route("/processar", methods=["POST"])
def processar():

    conn = get_connection()
    cursor = conn.cursor()

    plsql = """

    DECLARE
        v_dano_nevoa NUMBER := 15;

        CURSOR c_herois IS
            SELECT id_heroi, hp_atual
            FROM TB_HEROIS
            WHERE status = 'ATIVO'
            FOR UPDATE;

        v_novo_hp NUMBER;

    BEGIN

        FOR r IN c_herois LOOP

            v_novo_hp := r.hp_atual - v_dano_nevoa;

            IF v_novo_hp <= 0 THEN
                UPDATE TB_HEROIS
                SET hp_atual = 0,
                    status = 'CAIDO'
                WHERE CURRENT OF c_herois;
            ELSE
                UPDATE TB_HEROIS
                SET hp_atual = v_novo_hp
                WHERE CURRENT OF c_herois;
            END IF;

        END LOOP;

        COMMIT;

    END;
    """

    cursor.execute(plsql)

    cursor.close()
    conn.close()

    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)