"""
Enum de papéis (roles) de usuário do sistema.

Fica em core/ (não em models/) porque é usado tanto pelo model quanto
pelos schemas Pydantic e pelas dependencies de autorização — colocá-lo
em models/ criaria uma dependência desnecessária de schemas -> models.
"""
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INSPETOR = "inspetor"
    MECANICO = "mecanico"
    CLIENTE = "cliente"
