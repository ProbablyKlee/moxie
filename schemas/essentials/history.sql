--
-- The MIT License (MIT)
-- Copyright (c) 2022-Present Lia Marie
-- Permission is hereby granted, free of charge, to any person obtaining a
-- copy of this software and associated documentation files (the "Software"),
-- to deal in the Software without restriction, including without limitation
-- the rights to use, copy, modify, merge, publish, distribute, sublicense,
-- and/or sell copies of the Software, and to permit persons to whom the
-- Software is furnished to do so, subject to the following conditions:
-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
-- OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
-- FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
-- DEALINGS IN THE SOFTWARE.
--
CREATE TABLE IF NOT EXISTS user_history (
    id serial not null,
    user_id bigint not null,
    user_type text not null,
    entry_type text not null,
    added_at timestamp with time zone not null default now(),
    CONSTRAINT user_history_fkey FOREIGN KEY (user_id)
        REFERENCES users (user_id)  ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS user_history_user_id_idx ON user_history (user_id);
CREATE INDEX IF NOT EXISTS user_history_user_type_idx ON user_history (user_type);

CREATE OR REPLACE FUNCTION insert_history_item(p_user_id bigint, p_user_type text, p_entry_type text)
RETURNS void AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM user_history WHERE user_id = p_user_id AND user_type = p_user_type ORDER BY id DESC
        ) THEN
        IF NOT EXISTS (
            SELECT 1 FROM user_history WHERE user_id = p_user_id AND user_type = p_user_type AND entry_type = p_entry_type ORDER BY id DESC
            ) THEN
            INSERT INTO user_history (user_id, user_type, entry_type) VALUES (p_user_id, p_user_type, p_entry_type);
        END IF;
    ELSE
        INSERT INTO user_history (user_id, user_type, entry_type) VALUES (p_user_id, p_user_type, p_entry_type);
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS avatar_history (
   user_id bigint not null,
   avatar_id serial not null,
   format text not null,
   avatar bytea not null,
   added_at timestamp with time zone not null default now(),
    CONSTRAINT avatar_history_fkey FOREIGN KEY (user_id)
         REFERENCES users (user_id) MATCH SIMPLE
         ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS avatar_history_user_id_idx ON avatar_history (user_id);

CREATE OR REPLACE FUNCTION insert_avatar_history_item(p_user_id bigint, p_format text, p_avatar bytea)
RETURNS void AS $$
BEGIN
    IF NOT EXISTS (
        WITH last_avatar AS (
            SELECT avatar FROM avatar_history WHERE user_id = p_user_id
            ORDER BY added_at DESC LIMIT 1
        )
        SELECT 1 FROM last_avatar WHERE avatar = p_avatar
    ) THEN
        INSERT INTO avatar_history (user_id, format, avatar) VALUES (p_user_id, p_format, p_avatar);
    END IF;
END;
$$ LANGUAGE plpgsql;
