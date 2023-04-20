from pydantic import BaseModel


class Character(BaseModel):
    id: int
    name: str
    race: str
    gender: str
    character_class: str
    faction: str
    level: int
    active_spec: str | None
    realm: str
    guild: str
    achievement_points: int
    equipped_item_level: int
    average_item_level: int

    @classmethod
    def from_nested_data(cls, data: dict):
        return cls(
            id=data["id"],
            name=data["name"],
            race=data["race"]["name"]["en_US"],
            gender=data["gender"]["name"]["en_US"],
            character_class=data["character_class"]["name"]["en_US"],
            faction=data["faction"]["name"]["en_US"],
            level=data["level"],
            active_spec=data['active_spec']['name']['en_US'] if 'active_spec' in data else None,
            realm=data['realm']['name']['en_US'],
            guild=data['guild']['name'],
            achievement_points=data['achievement_points'],
            equipped_item_level=data['equipped_item_level'],
            average_item_level=data['average_item_level']
        )
