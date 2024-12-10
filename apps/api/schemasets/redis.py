from ninja import Schema


class TodoListItemSchema(Schema):
    # TODO: Schema 准确的使用场景在哪？滥用会导致 Schema 类型过多啊...
    value: str
