import datetime
import random
import typing

import faker

from data_generator import const
from social_network.domain import models


class DataGenerator:
    def __init__(self, seed: int = const.SEED, locale: str = const.LOCALE) -> None:
        self._faker = faker.Faker(seed=seed, locale=locale)

    def generate_name(self, sex: typing.Optional[int] = None) -> str:
        if sex == const.MALE:
            return self._faker.first_name_male()
        elif sex == const.FEMALE:
            return self._faker.first_name_female()
        else:
            return self._faker.first_name()

    def generate_last_name(self, sex: typing.Optional[int] = None) -> str:
        if sex == const.MALE:
            return self._faker.last_name_male()
        elif sex == const.FEMALE:
            return self._faker.last_name_female()
        else:
            return self._faker.last_name()

    def generate_user(
        self,
        bio_sentences_count: int = const.BIO_SENTENCES_COUNT,
        sex: typing.Optional[int] = None,
    ) -> models.NewUserDomain:
        if sex is None:
            sex = random.randint(const.MALE, const.FEMALE)

        return models.NewUserDomain(
            first_name=self.generate_name(sex),
            second_name=self.generate_last_name(sex),
            birthdate=datetime.datetime.combine(
                self._faker.date_of_birth(), datetime.datetime.min.time()
            ),
            biography=self._faker.paragraph(nb_sentences=bio_sentences_count),
            city=self._faker.city(),
            password=self._faker.password(),
        )

    def generate_users(
        self,
        entities_count: int,
        bio_sentences_count: int = const.BIO_SENTENCES_COUNT,
        sex: typing.Optional[int] = None,
    ) -> typing.Generator[models.NewUserDomain, None, None]:
        for i in range(entities_count):
            yield self.generate_user(bio_sentences_count=bio_sentences_count, sex=sex)
