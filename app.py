from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from entities.user import User
from dotenv import load_dotenv
from entities.riddle import Riddle
from entities.game_session import GameSession
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"

@login_manager.user_loader
def load_user(user_id: int):
    return User.get_by_id(user_id)

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.route('/')
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('auth/signin.html')

@app.route('/signup')
def signup():
    return render_template('auth/signup.html')

@app.route('/home')
@login_required
def home():
    winners = GameSession.get_top_winners()
    return render_template('home.html', winners=winners)

@app.route('/level1')
@login_required
def level1():
    return render_template('levels/level1.html')

@app.route('/level2')
@login_required
def level2():
    if current_user.role == 'admin':
        abort(403)
    return render_template('levels/level2.html')

@app.route('/level3')
@login_required
def level3():
    if current_user.role == 'admin':
        abort(403)
    return render_template('levels/level3.html')

@app.route('/level4')
@login_required
def level4():
    if current_user.role == 'admin':
        abort(403)
    return render_template('levels/level4.html')

@app.route('/level5')
@login_required
def level5():
    if current_user.role == 'admin':
        abort(403)
    return render_template('levels/level5.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        abort(403)
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@app.route('/api/users', methods=["POST"])
def create_user():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.check_email_exists(email):
        return jsonify({"success": False, "message": "El correo electrónico ingresado ya se encuentra registrado."}), 409

    is_saved = User.save(name, email, password)

    if is_saved:
        return jsonify({"success": True, "message": "Su cuenta fue creada correctamente."}), 201
    else:
        return jsonify({"success": False, "message": "Error al crear cuenta."}), 500

@app.route('/api/login', methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Debes ingresar tu correo y contraseña."}), 400

    user = User.get_by_credentials(email, password)

    if user is None:
        return jsonify({"success": False, "message": "Correo o contraseña incorrectos."}), 401

    if user == "inactive":
        return jsonify({"success": False, "message": "Su cuenta ha sido desactivada. Comuníquese con el administrador del sistema."}), 403

    login_user(user)
    return jsonify({"success": True, "message": "Inicio de sesión exitoso.", "role": user.role}), 200

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))

@app.route('/api/answer', methods=['POST'])
@login_required
def check_answer():
    # Solo jugadores pueden responder
    if current_user.role == 'admin':
        abort(403)
    
    data = request.get_json()
    level = data.get('level')
    answer = data.get('answer', '').strip().lower()
    total_attempts = data.get('total_attempts', 0)

    riddle = Riddle.get_active_by_level(level)

    if riddle is None:
        return jsonify({'success': False, 'message': 'No hay adivinanza para este nivel.'}), 404

    if answer == riddle.answer.lower():
        # Si es el último nivel, guardar partida ganada
        if level == 5:
            GameSession.save(current_user.id, total_attempts, True)
        return jsonify({'success': True, 'message': '¡Correcto!', 'next_level': level + 1}), 200
    else:
        new_attempts = total_attempts + 1
        # Si se acabaron los intentos, guardar partida perdida
        if new_attempts >= 3:
            GameSession.save(current_user.id, new_attempts, False)
        return jsonify({'success': False, 'message': 'Respuesta incorrecta.', 'total_attempts': new_attempts}), 200

@app.route('/admin/levels')
@login_required
def admin_levels():
    if current_user.role != 'admin':
        abort(403)
    riddles = Riddle.get_all()
    return render_template('admin/levels.html', riddles=riddles)

@app.route('/api/riddles', methods=['POST'])
@login_required
def create_riddle():
    if current_user.role != 'admin':
        abort(403)
    data = request.get_json()
    image = data.get('image')
    hint = data.get('hint')
    answer = data.get('answer')
    level = data.get('level')
    if not all([image, hint, answer, level]):
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos.'}), 400
    is_saved = Riddle.save(image, hint, answer, int(level))
    if is_saved:
        return jsonify({'success': True, 'message': 'Adivinanza creada correctamente.'}), 201
    else:
        return jsonify({'success': False, 'message': 'Error al crear adivinanza.'}), 500

@app.route('/api/riddles/activate', methods=['POST'])
@login_required
def activate_riddle():
    if current_user.role != 'admin':
        abort(403)
    data = request.get_json()
    riddle_id = data.get('id')
    level = data.get('level')
    is_updated = Riddle.set_active(riddle_id, level)
    if is_updated:
        return jsonify({'success': True, 'message': 'Adivinanza activada correctamente.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Error al activar adivinanza.'}), 500

if __name__ == '__main__':
    app.run()