"""Business-rule failures. Framework-agnostic — the web layer maps these to HTTP."""


class DomainError(Exception):
    """Base class for every error raised out of application/domain code."""


class NotFoundError(DomainError):
    def __init__(self, entity: str, entity_id):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"No {entity} with id {entity_id}.")


class ValidationError(DomainError):
    def __init__(self, message: str, fields: dict = None):
        super().__init__(message)
        self.message = message
        self.fields = fields
