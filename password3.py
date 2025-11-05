#passlib
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256

password_plano = "mi_contraseña_secreta"
hash_password = pbkdf2_sha256.hash(password_plano)
print(f"contraseña encriptada: {hash_password}")

# Verificación de la contraseña
contraseña_interna = "mi_contraseña_secreta"
is_correct = pbkdf2_sha256.verify(contraseña_interna, hash_password)
print(f"¿La contraseña es correcta? {is_correct}")

#passlib con contexto
contexto = CryptContext(schemes=["pbkdf2_sha256"], 
                        default="pbkdf2_sha256",
                        pbkdf2_sha256__default_rounds=30000
)

texto = "x?1_p-M.4!em"
texto_encriptado = contexto.hash(texto)
print(f"Texto encriptado: {texto_encriptado}")

# Verificación del texto
texto_interno = "x?1_p-M.4!em"
is_valid = contexto.verify(texto_interno, texto_encriptado)
print(f"¿El texto es correcto? {is_valid}")

