# ejercicio4.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------
# Configuración de conexión a MySQL
# Cambia 'password' por tu contraseña de MySQL
# -------------------------------------------------------
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '1234',
    'database': 'tareas_db'
}

def get_connection():
    """Crea y devuelve una conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)


# -------------------------------------------------------
# POST /tareas — Crear una nueva tarea
# -------------------------------------------------------
@app.route('/tareas', methods=['POST'])
def crear_tarea():
    datos = request.get_json()

    if not datos:
        return jsonify({'error': 'No se recibieron datos'}), 400

    titulo      = datos.get('titulo')
    descripcion = datos.get('descripcion', '')
    estado      = datos.get('estado', 'pendiente')

    if not titulo:
        return jsonify({'error': 'Falta el campo titulo'}), 400

    # Validar que el estado sea un valor permitido
    if estado not in ['pendiente', 'en progreso', 'completada']:
        return jsonify({'error': 'Estado no válido. Use: pendiente, en progreso, completada'}), 400

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO tareas (titulo, descripcion, estado) VALUES (%s, %s, %s)"
        cursor.execute(sql, (titulo, descripcion, estado))
        conn.commit()

        nuevo_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            'mensaje':     'Tarea creada correctamente',
            'id':          nuevo_id,
            'titulo':      titulo,
            'descripcion': descripcion,
            'estado':      estado
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------------------------------------------
# GET /tareas — Consultar todas las tareas
# -------------------------------------------------------
@app.route('/tareas', methods=['GET'])
def obtener_tareas():
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM tareas")
        tareas = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'total':  len(tareas),
            'tareas': tareas
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------------------------------------------
# PUT /tareas/<id> — Actualizar una tarea por ID
# -------------------------------------------------------
@app.route('/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    datos = request.get_json()

    if not datos:
        return jsonify({'error': 'No se recibieron datos'}), 400

    titulo      = datos.get('titulo')
    descripcion = datos.get('descripcion')
    estado      = datos.get('estado')

    # Validar estado si fue enviado
    if estado and estado not in ['pendiente', 'en progreso', 'completada']:
        return jsonify({'error': 'Estado no válido. Use: pendiente, en progreso, completada'}), 400

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar que la tarea existe
        cursor.execute("SELECT * FROM tareas WHERE id = %s", (id,))
        tarea = cursor.fetchone()

        if not tarea:
            cursor.close()
            conn.close()
            return jsonify({'error': f'No existe una tarea con id {id}'}), 404

        # Usar el valor nuevo si se envió, si no conservar el actual
        nuevo_titulo      = titulo      if titulo      is not None else tarea['titulo']
        nuevo_descripcion = descripcion if descripcion is not None else tarea['descripcion']
        nuevo_estado      = estado      if estado      is not None else tarea['estado']

        sql = "UPDATE tareas SET titulo = %s, descripcion = %s, estado = %s WHERE id = %s"
        cursor.execute(sql, (nuevo_titulo, nuevo_descripcion, nuevo_estado, id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'mensaje':     'Tarea actualizada correctamente',
            'id':          id,
            'titulo':      nuevo_titulo,
            'descripcion': nuevo_descripcion,
            'estado':      nuevo_estado
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------------------------------------------
# DELETE /tareas/<id> — Eliminar una tarea por ID
# -------------------------------------------------------
@app.route('/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar que la tarea existe antes de eliminar
        cursor.execute("SELECT * FROM tareas WHERE id = %s", (id,))
        tarea = cursor.fetchone()

        if not tarea:
            cursor.close()
            conn.close()
            return jsonify({'error': f'No existe una tarea con id {id}'}), 404

        cursor.execute("DELETE FROM tareas WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'mensaje': f'Tarea con id {id} eliminada correctamente'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)