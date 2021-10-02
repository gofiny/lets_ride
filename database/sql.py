tables = {
    "users": '''CREATE TABLE IF NOT EXISTS "users"
                (
                    "user_id" UUID NOT NULL UNIQUE PRIMARY KEY,
                    "nickname" VARCHAR(35) NULL UNIQUE,
                    "first_name" VARCHAR(100) NOT NULL,
                    "reg_time" TIMESTAMP NOT NULL,
                    "born_date" DATE,
                    "gender" VARCHAR(6),
                    "hashed_password" VARCHAR(128)
                )''',

    "profiles": '''CREATE TABLE IF NOT EXISTS "profiles"
                (
                    "profile_id" UUID NOT NULL UNIQUE PRIMARY KEY,
                    "user_id" UUID NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE,
                    "status" BOOL DEFAULT true,
                    "desired_gender" VARCHAR(6),
                    "min_age" SMALLINT,
                    "max_age" SMALLINT,
                    "type" SMALLINT,
                    "vehicle_type" VARCHAR(8)
                )''',  # type 0 - driver, 1 - companion, 2 - together

    "user_rating": '''CREATE TABLE IF NOT EXISTS "user_rating"
                (
                    "rating_id" UUID NOT NULL UNIQUE PRIMARY KEY,
                    "user_id" UUID NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE,
                    "rate" INT DEFAULT 0,
                    "rate_count" INT DEFAULT 0
                )''',

    "sessions": '''CREATE TABLE IF NOT EXISTS "sessions"
                (
                    "session_id" UUID NOT NULL UNIQUE PRIMARY KEY,
                    "user_id" UUID NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE,
                    "device_id" VARCHAR(32) NOT NULL,
                    "start_time" TIMESTAMP NOT NULL,
                    "token" VARCHAR(100) NOT NULL
                )''',

    "user_photos": '''CREATE TABLE IF NOT EXISTS "user_photos"
                (   
                    "photo_id" UUID NOT NULL UNIQUE PRIMARY KEY,
                    "user_id" UUID NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
                )''',

    "profile_photos": '''CREATE TABLE IF NOT EXISTS "profile_photos"
                (   
                    "photo_id" UUID NOT NULL UNIQUE PRIMARY KEY,
                    "profile_id" UUID NOT NULL REFERENCES "profiles" ("profile_id") ON DELETE CASCADE
                )'''
}


select_nickname = '''SELECT nickname FROM users WHERE LOWER(nickname)=LOWER($1)'''

create_user = '''WITH new_user  AS (
                    INSERT INTO 
                        users 
                            (user_id, nickname, first_name, reg_time, born_date, gender, hashed_password)
                        VALUES
                            ($1, $2, $3, $4, $5, $6, $7))
                    INSERT INTO
                        user_rating
                            (rating_id, user_id)
                        VALUES ($8, $1)'''

get_session_token_by_device = '''SELECT token FROM sessions WHERE user_id=$1 AND device_id=$2'''

insert_session = '''INSERT INTO sessions VALUES ($1, $2, $3, $4, $5)'''

select_session_token = '''SELECT token FROM sessions WHERE user_id=$1 AND device_id=$2'''

select_photo_count = '''SELECT COUNT(photo_id) FROM {photo_type}_photos WHERE {photo_type}_id=$1'''

insert_photo = '''INSERT INTO {photo_type}_photos VALUES ($1, $2)'''

insert_profile = '''INSERT INTO profiles 
                        (
                            profile_id, user_id, desired_gender, min_age, max_age, type, vehicle_type
                        )
                    VALUES ($1, $2, $3, $4, $5, $6, $7)'''

check_profile = '''SELECT profile_id FROM profiles WHERE user_id=$1 AND type=$2'''
