import bcrypt
import logging

class AuthManager:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.current_user = None

    def register_user(self, tipo_documento, numero_documento, nombre, correo, contrasena, rol):
        hashed_password = self._hash_password(contrasena)
        logging.debug(f"Registrando usuario: {correo}")
        query = "INSERT INTO usuarios (tipo_documento, numero_documento, nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (tipo_documento, numero_documento, nombre, correo, hashed_password, rol)
        result = self.db_connector.execute_query(query, params)
        logging.debug(f"Resultado del registro: {result}")
        return result is not None and result > 0

    def login(self, correo, contrasena, tipo_usuario):
        logging.debug(f"Intento de inicio de sesión para: {correo}, tipo: {tipo_usuario}")
        query = "SELECT * FROM usuarios WHERE correo = %s AND rol = %s"
        result = self.db_connector.execute_query(query, (correo, tipo_usuario))

        logging.debug(f"Resultado de la consulta: {result}")

        if result and len(result) > 0:
            user = result[0]
            stored_password = user['contrasena']

            logging.debug(f"Contraseña almacenada: {stored_password}")
            logging.debug(f"Contraseña proporcionada: {contrasena}")

            if stored_password.startswith('$2b$') and len(stored_password) == 60:
                logging.debug("La contraseña almacenada está hasheada")
                if self._check_password(contrasena, stored_password):
                    self.current_user = user
                    logging.debug("Inicio de sesión exitoso (contraseña hasheada)")
                    return True
                else:
                    logging.debug("Fallo en la verificación de la contraseña hasheada")
            else:
                logging.debug("La contraseña almacenada no está hasheada")
                if contrasena == stored_password:
                    hashed_password = self._hash_password(contrasena)
                    update_query = "UPDATE usuarios SET contrasena = %s WHERE id_usuario = %s"
                    self.db_connector.execute_query(update_query, (hashed_password, user['id_usuario']))
                    self.current_user = user
                    logging.debug("Inicio de sesión exitoso (contraseña actualizada)")
                    return True
                else:
                    logging.debug("Fallo en la comparación de contraseña no hasheada")

        logging.debug("Inicio de sesión fallido")
        return False
    def logout(self):
        self.current_user = None
        logging.debug("Sesión cerrada")

    def get_current_user(self):
        return self.current_user

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _check_password(self, provided_password, stored_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

    def check_permission(self, required_role):
        if not self.current_user:
            return False
        user_role = self.current_user['rol']
        return user_role == 'dueños'  # Simplificado para este caso específico

    def _update_last_login(self):
        if self.current_user:
            query = "UPDATE usuarios SET ultima_sesion = CURRENT_TIMESTAMP WHERE id_usuario = %s"
            self.db_connector.execute_query(query, (self.current_user['id_usuario'],))
            logging.debug(f"Actualizada última sesión para el usuario {self.current_user['correo']}")