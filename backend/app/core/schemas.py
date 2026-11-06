from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class EsquemaBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
    )

    def a_json(self) -> dict:
        return self.model_dump(by_alias=True, mode="json")
