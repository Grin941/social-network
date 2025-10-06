import datetime
import random
import typing
import uuid

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

    def generate_text(self, nb_sentences: typing.Optional[int] = None) -> str:
        return self._faker.paragraph(
            nb_sentences=nb_sentences or random.randint(1, const.SENTENCES_COUNT_TO)
        )

    def generate_user(
        self,
        bio_sentences_count: int = const.BIO_SENTENCES_COUNT,
        sex: typing.Optional[int] = None,
        password: typing.Optional[str] = None,
    ) -> models.NewUserDomain:
        if sex is None:
            sex = random.randint(const.MALE, const.FEMALE)

        return models.NewUserDomain(
            first_name=self.generate_name(sex),
            second_name=self.generate_last_name(sex),
            birthdate=datetime.datetime.combine(
                self._faker.date_of_birth(), datetime.datetime.min.time()
            ),
            biography=self.generate_text(nb_sentences=bio_sentences_count),
            city=self._faker.city(),
            password=password or self._faker.password(),
        )

    def generate_users(
        self,
        entities_count: int,
        bio_sentences_count: int = const.BIO_SENTENCES_COUNT,
        sex: typing.Optional[int] = None,
        password: typing.Optional[str] = None,
    ) -> typing.Generator[models.NewUserDomain, None, None]:
        for i in range(entities_count):
            yield self.generate_user(
                bio_sentences_count=bio_sentences_count, sex=sex, password=password
            )

    def generate_post(
        self,
        user_id: uuid.UUID,
    ) -> models.NewPostDomain:
        return models.NewPostDomain(
            author_id=user_id,
            text=self.generate_text(),
        )

    def generate_posts(
        self,
        user_id: uuid.UUID,
        entities_count: int = const.POSTS_PER_USER_COUNT,
    ) -> typing.Generator[models.NewPostDomain, None, None]:
        for i in range(entities_count):
            yield self.generate_post(user_id=user_id)

    @staticmethod
    def generate_dialog(
        user_id: uuid.UUID,
        friend_id: uuid.UUID,
    ) -> models.NewChatDomain:
        return models.NewChatDomain(name=f"{friend_id} - {user_id}")

    @staticmethod
    def generate_dialog_participant(
        user_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> models.NewChatParticipantDomain:
        return models.NewChatParticipantDomain(user_id=user_id, chat_id=chat_id)

    def generate_message(
        self,
        user_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> models.NewChatMessageDomain:
        return models.NewChatMessageDomain(
            author_id=user_id,
            chat_id=chat_id,
            text=self.generate_text(nb_sentences=1),
        )
