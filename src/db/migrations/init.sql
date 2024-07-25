CREATE TABLE IF NOT EXISTS "api_tokens" (
    "token_id" SERIAL PRIMARY KEY,
    "api_token" TEXT NOT NULL,
    "rate" DECIMAL(10, 2),
    "currency" VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS "users" (
    "user_id" BIGINT NOT NULL PRIMARY KEY,
    "username" VARCHAR(255),
    "first_name" VARCHAR(255),
    "last_name" VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS "user_tokens" (
    "user_id" BIGINT NOT NULL,
    "token_id" INT NOT NULL,
    "worksnaps_user_id" INT NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES "users" ("user_id") ON DELETE CASCADE,
    FOREIGN KEY ("token_id") REFERENCES "api_tokens" ("token_id") ON DELETE CASCADE,
    PRIMARY KEY ("user_id", "token_id", "worksnaps_user_id")
);
