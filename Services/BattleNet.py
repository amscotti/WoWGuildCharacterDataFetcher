import aiohttp


class BattleNet:
    """
    A class to interact with the Battle.net API.
    """

    BASE_URL = 'https://us.api.blizzard.com'

    def __init__(self, client_id: str,
                 client_secret: str,
                 access_token: str,
                 session: aiohttp.ClientSession):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.session = session

    async def close(self) -> None:
        """
        Close the aiohttp session.
        """
        await self.session.close()

    @classmethod
    async def create(cls, client_id: str, client_secret: str) -> 'BattleNet':
        """
        Create a new BattleNet instance with the given client_id and client_secret.
        """
        session = aiohttp.ClientSession()
        access_token = await cls.__get_access_token(session, client_id, client_secret)

        return cls(client_id, client_secret, access_token, session)

    @classmethod
    async def __get_access_token(cls,
                                 session: aiohttp.ClientSession,
                                 client_id: str,
                                 client_secret: str) -> str:
        """
        Get an access token using the given client_id and client_secret.
        """
        token_url = 'https://us.battle.net/oauth/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        async with session.post(token_url, data=data) as response:
            if response.status == 200:
                json_data = await response.json()
                return json_data['access_token']
            else:
                raise ValueError(f"Failed to obtain access token: {response.text}")

    def __get_headers(self) -> dict[str, str]:
        """
        Generate the headers required for the API requests.
        """
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Battlenet-Namespace': 'profile-us',
        }

    async def get_character_data(self, realm: str, character_name: str) -> dict:
        """
        Fetch character data for the given realm and character_name.
        """
        url = f"{self.BASE_URL}/profile/wow/character/{realm}/{character_name}"
        async with self.session.get(url, headers=self.__get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ValueError(f"Failed to fetch character data: {response.text}")

    async def get_guild_data(self, realm: str, guild_name: str) -> dict:
        """
        Fetch guild data for the given realm and guild_name.
        """
        url = f"{self.BASE_URL}/data/wow/guild/{realm}/{guild_name}/roster"
        async with self.session.get(url, headers=self.__get_headers()) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ValueError(f"Failed to fetch guild data for {guild_name} on {realm}")
