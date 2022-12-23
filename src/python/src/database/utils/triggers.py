class CurrentTimestampOnUpdateTriggerDDL(object):
    _target_column: str = "updated_at"
    _body: str = (
        "CREATE TRIGGER UpdateOnCurrentTimestamp{table_name_cap} "
        "AFTER UPDATE "
        "ON {table_name} "
        "FOR EACH ROW "
        "BEGIN "
        "update {table_name} set {target_column}=CURRENT_TIMESTAMP WHERE id = NEW.id; "
        "END;"
    )
    _stmt: str

    def __init__(self, table_name: str, _target_column: str = _target_column):
        self._table_name: str = table_name
        self._compile()

    def recompile(self):
        self._compile()

    def _compile(self):
        self._stmt = self._body.format(
            table_name=self._table_name,
            table_name_cap=self._table_name.capitalize(),
            target_column=self._target_column
        )

    def __str__(self):
        return self._stmt

    def __repr__(self):
        return self.__str__()
