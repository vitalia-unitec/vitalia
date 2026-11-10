from pydantic import BaseModel, ConfigDict


def a_camel(nombre: str) -> str:
    primera, *resto = nombre.split("_")
    return primera + "".join(parte[:1].upper() + parte[1:] for parte in resto)


class EsquemaBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=a_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
    )

    def a_json(self) -> dict:
        return self.model_dump(by_alias=True, mode="json")
