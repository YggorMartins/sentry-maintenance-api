"""
Schemas de Cliente.

A validação de CPF/CNPJ (dígito verificador) e a regra "documento
compatível com tipo de pessoa" acontecem AQUI, na borda da API — assim
o erro chega pro usuário de forma clara (422 com mensagem específica)
antes mesmo de tentar tocar o banco. A CheckConstraint no banco (ver
model) é a rede de segurança, não a primeira linha de validação.
"""
import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.core.enums import TipoPessoa
from app.utils.document_validators import is_valid_cnpj, is_valid_cpf


class ClienteBase(BaseModel):
    tipo_pessoa: TipoPessoa
    nome: str = Field(min_length=3, max_length=200)
    cpf: str | None = None
    cnpj: str | None = None
    endereco_logradouro: str | None = Field(default=None, max_length=200)
    endereco_numero: str | None = Field(default=None, max_length=20)
    endereco_complemento: str | None = Field(default=None, max_length=100)
    endereco_bairro: str | None = Field(default=None, max_length=100)
    endereco_cidade: str | None = Field(default=None, max_length=100)
    endereco_uf: str | None = Field(default=None, min_length=2, max_length=2)
    endereco_cep: str | None = None
    telefone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    observacoes: str | None = None

    @model_validator(mode="after")
    def validar_documento_por_tipo_pessoa(self) -> "ClienteBase":
        digits = lambda v: re.sub(r"\D", "", v) if v else v  # noqa: E731

        if self.tipo_pessoa == TipoPessoa.FISICA:
            if not self.cpf:
                raise ValueError("CPF é obrigatório para pessoa física.")
            if self.cnpj:
                raise ValueError("CNPJ não deve ser informado para pessoa física.")
            self.cpf = digits(self.cpf)
            if not is_valid_cpf(self.cpf):
                raise ValueError("CPF inválido.")

        if self.tipo_pessoa == TipoPessoa.JURIDICA:
            if not self.cnpj:
                raise ValueError("CNPJ é obrigatório para pessoa jurídica.")
            if self.cpf:
                raise ValueError("CPF não deve ser informado para pessoa jurídica.")
            self.cnpj = digits(self.cnpj)
            if not is_valid_cnpj(self.cnpj):
                raise ValueError("CNPJ inválido.")

        if self.endereco_cep:
            self.endereco_cep = digits(self.endereco_cep)

        return self


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
