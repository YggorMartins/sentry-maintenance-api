"""Cria o administrador inicial sem expor elevação de papel pela API."""

import argparse
import getpass
import os

from pydantic import ValidationError

from app.core.roles import UserRole
from app.database.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


def _password_from_environment(variable_name: str | None) -> str:
    if variable_name:
        password = os.getenv(variable_name)
        if not password:
            raise SystemExit(f"A variável {variable_name!r} não está definida ou está vazia.")
        return password

    password = getpass.getpass("Senha do administrador: ")
    confirmation = getpass.getpass("Confirme a senha: ")
    if password != confirmation:
        raise SystemExit("As senhas informadas não coincidem.")
    return password


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria um administrador inicial.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument(
        "--password-env",
        help="Nome de uma variável de ambiente que contém a senha (útil em automação).",
    )
    args = parser.parse_args()

    try:
        data = UserCreate(
            full_name=args.full_name,
            email=args.email,
            password=_password_from_environment(args.password_env),
            role=UserRole.ADMIN,
        )
    except ValidationError as exc:
        raise SystemExit(f"Dados inválidos: {exc}") from exc

    with SessionLocal() as session:
        users = UserRepository(session)
        if users.get_by_email(str(data.email)) is not None:
            raise SystemExit("Já existe um usuário com este email; nenhuma alteração foi feita.")
        user = users.create(data)

    print(f"Administrador criado com sucesso: {user.email}")


if __name__ == "__main__":
    main()
